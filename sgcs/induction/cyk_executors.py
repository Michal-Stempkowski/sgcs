from induction.coverage_operators import CoverageType
from sgcs.induction.detector import Detector


class CykTypeId(object):
    symbol_pair_executor = 0
    parent_combination_executor = 1
    cell_executor = 2
    row_executor = 3
    table_executor = 4
    production_pool = 5
    environment = 6
    cyk_result = 7
    terminal_cell_executor = 8


class CykResult(object):
    def __init__(self):
        self.belongs_to_grammar = False
        self.is_positive = None

    def __str__(self):
        props = ['belongs?:{0}'.format('Y' if self.belongs_to_grammar else 'N')]
        return self.__class__.__name__ + '({' + '};{'.join(props) + "})"


class CykExecutor(object):
    def __init__(self, child_level, cyk_service):
        self.child_level = child_level
        self.cyk_service = cyk_service

    def create_child_executor(self, *args):
        return self.cyk_service.factory.create(self.child_level, *args)

    def __str__(self):
        return self.__class__.__name__ + '({' + '};{'.join(self.get_coordinates()) + "})"

    def get_coordinates(self):
        return tuple()


class CykTableExecutor(CykExecutor):
    def __init__(self, cyk_service):
        super().__init__(CykTypeId.row_executor, cyk_service)

    @staticmethod
    def _belongs_to_grammar(rule_population, environment):
        last_cell_coordinates = environment.get_sentence_length() - 1, 0
        return rule_population.starting_symbol in \
            environment.get_symbols(last_cell_coordinates)

    def execute(self, environment, rule_population):
        sentence_length = environment.get_sentence_length()

        for row in range(0, sentence_length):
            child_executor = self.create_child_executor(self, row, self.cyk_service)
            child_executor.execute(environment, rule_population)

        if not self._belongs_to_grammar(rule_population, environment):
            last_cell_coordinates = sentence_length - 1, 0
            self.cyk_service.coverage_operations.perform_coverage(
                self.cyk_service,
                CoverageType.no_starting_symbol,
                environment,
                rule_population,
                last_cell_coordinates)

        result = self.cyk_service.factory.create(CykTypeId.cyk_result)
        result.belongs_to_grammar = self._belongs_to_grammar(rule_population, environment)
        result.is_positive = environment.is_sentence_positive()
        return result


class CykStochasticTableExecutor(CykTableExecutor):
    @staticmethod
    def _belongs_to_grammar(rule_population, environment):
        return environment.get_most_probable_production_for(
            rule_population.starting_symbol) is not None


class CykRowExecutor(CykExecutor):
    def __init__(self, table_executor, row, cyk_service):
        super().__init__(CykTypeId.cell_executor, cyk_service)
        self._row = row
        self.parent_executor = table_executor

    @property
    def current_row(self):
        return self._row

    def execute(self, environment, rule_population):
        row_length = environment.get_row_length(self.current_row)

        for col in range(0, row_length):
            child_executor = self.create_child_executor(self, col, self.cyk_service)
            child_executor.execute(environment, rule_population)

    def get_coordinates(self):
        return self.current_row,


class CykFirstRowExecutor(CykRowExecutor):
    def __init__(self, table_executor, row, cyk_service):
        super().__init__(table_executor, row, cyk_service)
        self.child_level = CykTypeId.terminal_cell_executor


class CykCellExecutor(CykExecutor):
    def __init__(self, row_executor, column, cyk_service):
        super().__init__(CykTypeId.parent_combination_executor, cyk_service)
        self.parent_executor = row_executor
        self._column = column

    @property
    def current_row(self):
        return self.parent_executor.current_row

    @property
    def current_col(self):
        return self._column

    def execute(self, environment, rule_population):
        for shift in range(1, self.current_row + 1):
            child_executor = self.create_child_executor(self, shift, self.cyk_service)
            child_executor.execute(environment, rule_population)

        # If production_pool is empty, then perform some coverage
        if not environment.get_symbols(self.get_coordinates()):
            self.cyk_service.coverage_operations.perform_coverage(
                self.cyk_service,
                CoverageType.no_effector_found,
                environment,
                rule_population,
                self.get_coordinates()
            )

    def get_coordinates(self):
        return self.current_row, self.current_col


class CykTerminalCellExecutor(CykCellExecutor):
    def execute(self, environment, rule_population):
        productions = self._generate_productions(environment, rule_population)

        self._add_productions(environment, productions)

        self._perform_coverage_if_required(environment, rule_population)

    def _generate_productions(self, environment, rule_population):
        detector = Detector(self.get_coordinates())
        return detector.generate_production(environment, rule_population)

    @staticmethod
    def _add_productions(environment, productions):
        for production in productions:
            environment.add_production(production)

    def _perform_coverage_if_required(self, environment, rule_population):
        if environment.has_no_productions(self.get_coordinates()):
            self.cyk_service.coverage_operations.perform_coverage(
                self.cyk_service,
                CoverageType.unknown_terminal_symbol,
                environment,
                rule_population,
                self.get_coordinates()
            )


class CykParentCombinationExecutor(CykExecutor):
    def __init__(self, cell_executor, shift, cyk_service):
        super().__init__(CykTypeId.symbol_pair_executor, cyk_service)
        self.parent_executor = cell_executor
        self._shift = shift

    @property
    def current_row(self):
        return self.parent_executor.current_row

    @property
    def current_col(self):
        return self.parent_executor.current_col

    @property
    def shift(self):
        return self._shift

    def execute(self, environment, rule_population):
        coordinates = self.get_coordinates()
        left_parent_symbol_count = environment.get_left_parent_symbol_count(coordinates)
        right_parent_symbol_count = environment.get_right_parent_symbol_count(coordinates)

        for left_id in range(left_parent_symbol_count):
            for right_id in range(right_parent_symbol_count):
                child_executor = self.create_child_executor(self, left_id, right_id,
                                                            self.cyk_service)
                child_executor.execute(environment, rule_population)

    def get_coordinates(self):
        return (self.parent_executor.current_row,
                self.parent_executor.current_col,
                self.shift)


class CykSymbolPairExecutor(CykExecutor):
    def __init__(self, parent_executor, left_id, right_id, cyk_service):
        super().__init__(None, cyk_service)
        self.parent_executor = parent_executor
        self.left_id = left_id
        self.right_id = right_id

    def execute(self, environment, rule_population):
        productions = self._generate_productions(environment, rule_population)

        self._add_productions(environment, productions)

    def _generate_productions(self, environment, rule_population):
        detector = Detector(self.get_coordinates())
        return detector.generate_production(environment, rule_population)

    @staticmethod
    def _add_productions(environment, productions):
        for production in productions:
            environment.add_production(production)

    def get_coordinates(self):
        return (self.parent_executor.current_row,
                self.parent_executor.current_col,
                self.parent_executor.shift,
                self.left_id,
                self.right_id)


def set_probabilities(productions, rule_population):
    for production in productions:
            if not production.is_empty():
                production.probability = rule_population.get_normalized_rule_probability(
                    production.rule)


class CykStochasticTerminalCellExecutor(CykTerminalCellExecutor):
    def execute(self, environment, rule_population):
        productions = self._generate_productions(environment, rule_population)

        set_probabilities(productions, rule_population)

        self._add_productions(environment, productions)

        self._perform_coverage_if_required(environment, rule_population)


class CykStochasticSymbolPairExecutor(CykSymbolPairExecutor):
    def execute(self, environment, rule_population):
        productions = self._generate_productions(environment, rule_population)

        set_probabilities(productions, rule_population)

        self._add_productions(environment, productions)
