from enum import Enum
from sgcs.induction.detector import Detector


class CykTypeId(Enum):
    symbol_pair_executor = 0
    parent_combination_executor = 1
    cell_executor = 2
    row_executor = 3
    table_executor = 4
    production_pool = 5
    environment = 6
    cyk_result = 7


class CykResult(object):
    def __init__(self):
        self.belongs_to_grammar = False


class CykExecutor(object):
    def __init__(self, child_level, executor_factory):
        self.child_level = child_level
        self.executor_factory = executor_factory

    def create_child_executor(self, *args):
        return self.executor_factory.create(self.child_level, *args)


class CykTableExecutor(CykExecutor):
    def __init__(self, executor_factory):
        super().__init__(CykTypeId.row_executor, executor_factory)

    def execute(self, environment, rule_population):
        sentence_length = environment.get_sentence_length()

        for row in range(1, sentence_length):
            child_executor = self.create_child_executor(self, row, self.executor_factory)
            child_executor.execute(environment, rule_population)

        return self.executor_factory.create(CykTypeId.cyk_result)


class CykRowExecutor(CykExecutor):
    def __init__(self, table_executor, row, executor_factory):
        super().__init__(CykTypeId.cell_executor, executor_factory)
        self._row = row
        self.parent_executor = table_executor

    @property
    def current_row(self):
        return self._row

    def execute(self, environment, rule_population):
        row_length = environment.get_row_length(self.current_row)

        for col in range(0, row_length):
            child_executor = self.create_child_executor(self, col, self.executor_factory)
            child_executor.execute(environment, rule_population)


class CykCellExecutor(CykExecutor):
    def __init__(self, row_executor, column, executor_factory):
        super().__init__(CykTypeId.parent_combination_executor, executor_factory)
        self.parent_executor = row_executor
        self._column = column

    @property
    def current_row(self):
        return self.parent_executor.current_row

    @property
    def current_col(self):
        return self._column

    def execute(self, environment, rule_population):
        production_pool = self.executor_factory.create(CykTypeId.production_pool)
        for shift in range(1, self.current_row):
            child_executor = self.create_child_executor(self, shift, self.executor_factory)
            child_executor.execute(environment, rule_population, production_pool)

        if production_pool.is_empty():
            pass  # If production_pool is empty, then perform some coverage

        if not production_pool.is_empty():
            effectors = production_pool.get_effectors()
            environment.add_symbols((self.current_row, self.current_col), effectors)


class CykParentCombinationExecutor(CykExecutor):
    def __init__(self, cell_executor, shift, executor_factory):
        super().__init__(CykTypeId.symbol_pair_executor, executor_factory)
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

    def execute(self, environment, rule_population, production_pool):
        coordinates = self.get_coordinates()
        left_parent_symbol_count = environment.get_left_parent_symbol_count(coordinates)
        right_parent_symbol_count = environment.get_right_parent_symbol_count(coordinates)

        for left_id in range(left_parent_symbol_count):
            for right_id in range(right_parent_symbol_count):
                child_executor = self.create_child_executor(self, left_id, right_id,
                                                            self.executor_factory)
                child_executor.execute(environment, rule_population, production_pool)

    def get_coordinates(self):
        return (self.parent_executor.current_row,
                self.parent_executor.current_col,
                self.shift)


class CykSymbolPairExecutor(CykExecutor):
    def __init__(self, parent_executor, left_id, right_id, executor_factory):
        super().__init__(None, executor_factory)
        self.parent_executor = parent_executor
        self.left_id = left_id
        self.right_id = right_id

    def execute(self, environment, rule_population, production_pool):
        coordinates = self.get_coordinates()

        detector = Detector(coordinates)

        for production in detector.generate_production(environment, rule_population):
            production_pool.add_production(production)

    def get_coordinates(self):
        return (self.parent_executor.current_row,
                self.parent_executor.current_col,
                self.parent_executor.shift,
                self.left_id,
                self.right_id)

    def __str__(self):
        return self.__class__.__name__ + '({' + '};{'.join(self.get_coordinates()) + "})"
