import unittest
from unittest.mock import create_autospec, PropertyMock, call
from hamcrest import *
from sgcs.factory import Factory
from sgcs.induction.cyk_executors import *
from sgcs.induction.environment import Environment
from sgcs.induction.production import ProductionPool, Production, TerminalProduction
from sgcs.induction.rule import Rule, TerminalRule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol
from sgcs.tests.test_common import are_


class ExecutorSuite(unittest.TestCase):
    def initialize_mocks(self, parent_class):
        self.parent_executor = create_autospec(parent_class) if parent_class else None
        self.environment_mock = create_autospec(Environment)
        self.rule_population_mock = create_autospec(RulePopulation)
        self.production_pool_mock = create_autospec(ProductionPool)
        self.children_created = []

        self.executor_factory = Factory(
            {
                CykTypeId.parent_combination_executor: self.child_mocker(CykParentCombinationExecutor),
                CykTypeId.cell_executor: self.child_mocker(CykCellExecutor),
                CykTypeId.row_executor: self.child_mocker(CykRowExecutor),
                CykTypeId.table_executor: self.child_mocker(CykTableExecutor),
                CykTypeId.symbol_pair_executor: self.child_mocker(CykSymbolPairExecutor),
                CykTypeId.production_pool: lambda *args: self.production_pool_mock,
                CykTypeId.cyk_result: CykResult,
                CykTypeId.terminal_cell_executor: self.child_mocker(CykTerminalCellExecutor)
            }
        )

    def child_mocker(self, mock_spec):
        return lambda *args: \
            self.children_created.append(args) or create_autospec(mock_spec)


class TestCykSymbolPairExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_mocks(CykParentCombinationExecutor)

        self.production_pool_mock.add_production.side_effect = self.capture_production
        self.captured_productions = []

        self.initialize_coordinates()

        self.sut = CykSymbolPairExecutor(self.parent_executor, self.left_id, self.right_id,
                                         self.executor_factory)

    def initialize_coordinates(self):
        self.left_id = 0
        self.right_id = 1

        type(self.parent_executor).current_row = PropertyMock(return_value=2)
        type(self.parent_executor).current_col = PropertyMock(return_value=3)
        type(self.parent_executor).shift = PropertyMock(return_value=4)

    def capture_production(self, production):
        self.captured_productions.append(production)

    def test_adding_production_should_result_in_storing_it(self):
        # Given:
        symbols = ('B', 'C')
        rules = [Rule('A', 'B', 'C'), Rule('D', 'B', 'C')]
        self.environment_mock.get_symbols.return_value = symbols
        self.rule_population_mock.get_rules_by_right.return_value = rules

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock,
                         self.production_pool_mock)

        # Then:
        assert_that(self.captured_productions, has_length(2))


class TestCykParentCombinationExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_mocks(CykCellExecutor)
        self.initialize_coordinates()

        self.sut = CykParentCombinationExecutor(self.parent_executor, self.shift,
                                                self.executor_factory)

    def initialize_coordinates(self):
        self.shift = 1

        type(self.parent_executor).current_row = PropertyMock(return_value=2)
        type(self.parent_executor).current_col = PropertyMock(return_value=3)

    def test_symbol_pair_combinations_should_be_executed(self):
        # Given:
        self.environment_mock.get_left_parent_symbol_count.return_value = 2
        self.environment_mock.get_right_parent_symbol_count.return_value = 3

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock,
                         self.production_pool_mock)

        # Then:
        assert_that(self.children_created, are_(
            [
                (self.sut, 0, 0, self.executor_factory),
                (self.sut, 0, 1, self.executor_factory),
                (self.sut, 0, 2, self.executor_factory),
                (self.sut, 1, 0, self.executor_factory),
                (self.sut, 1, 1, self.executor_factory),
                (self.sut, 1, 2, self.executor_factory)
            ]
        ))

    def test_on_no_matching_symbols_no_child_creator_should_be_created(self):
        # Given:
        self.environment_mock.get_left_parent_symbol_count.return_value = 2
        self.environment_mock.get_right_parent_symbol_count.return_value = 0

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock,
                         self.production_pool_mock)

        # Then:
        assert_that(self.children_created, is_(empty()))


class TestCykCellExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_mocks(CykRowExecutor)
        self.initialize_coordinates()

        self.sut = CykCellExecutor(self.parent_executor, self.current_col, self.executor_factory)

    def initialize_coordinates(self):
        type(self.parent_executor).current_row = PropertyMock(return_value=4)
        self.current_col = 3

    def parent_combinations_should_be_executed_scenario(self, effectors):
        # Given:
        self.production_pool_mock.is_empty.return_value = not effectors
        self.production_pool_mock.get_effectors.return_value = effectors

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock)

        # Then:
        assert_that(self.children_created, are_(
            [
                (self.sut, 1, self.executor_factory),
                (self.sut, 2, self.executor_factory),
                (self.sut, 3, self.executor_factory)
            ]
        ))

    def test_effectors_found(self):
        # Given:
        effectors = {'A', 'B', 'C'}

        # When:
        self.parent_combinations_should_be_executed_scenario(effectors)

        # Then:
        self.environment_mock.add_symbols.assert_called_once_with((4, 3), effectors)

    def test_effectors_not_found(self):
        # Given:
        effectors = {}

        # When:
        self.parent_combinations_should_be_executed_scenario(effectors)

        # Then:
        assert_that(self.environment_mock.add_symbols.called, is_(False))


class TestCykRowExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_mocks(CykTableExecutor)
        self.initialize_coordinates()

        self.sut = CykRowExecutor(self.parent_executor, self.current_row, self.executor_factory)

    def initialize_coordinates(self):
        self.current_row = 2

    def test_cells_in_row_should_be_executed(self):
        # Given:
        self.environment_mock.get_row_length.return_value = 2

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock)

        # Then:
        assert_that(self.children_created, are_(
            [
                (self.sut, 0, self.executor_factory),
                (self.sut, 1, self.executor_factory)
            ]
        ))


class TestCykTableExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_mocks(None)

        self.sut = CykTableExecutor(self.executor_factory)

    def test_cells_in_row_should_be_executed(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 5

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock)

        # Then:
        assert_that(self.children_created, are_(
            [
                (self.sut, 0, self.executor_factory),
                (self.sut, 1, self.executor_factory),
                (self.sut, 2, self.executor_factory),
                (self.sut, 3, self.executor_factory),
                (self.sut, 4, self.executor_factory)
            ]
        ))


class TestCykFirstRowExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_mocks(CykTableExecutor)
        self.initialize_coordinates()

        self.sut = CykFirstRowExecutor(self.parent_executor, self.current_row, self.executor_factory)

    def initialize_coordinates(self):
        self.current_row = 0

    def test_cells_in_row_should_be_executed(self):
        # Given:
        self.environment_mock.get_row_length.return_value = 3

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock)

        # Then:
        assert_that(self.children_created, are_(
            [
                (self.sut, 0, self.executor_factory),
                (self.sut, 1, self.executor_factory),
                (self.sut, 2, self.executor_factory)
            ]
        ))


class TestCykTerminalCellExecutor(ExecutorSuite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.initialize_mocks(CykFirstRowExecutor)
        self.initialize_coordinates()

        self.sut = CykTerminalCellExecutor(self.parent_executor, self.current_col,
                                           self.executor_factory)

    def initialize_coordinates(self):
        type(self.parent_executor).current_row = PropertyMock(return_value=0)
        self.current_col = 3

    def terminal_symbol_scenario(self, rules):
        # Given:
        selected_rules = [x for x in rules if x.left_child == Symbol(5)]
        effectors = [x.parent for x in selected_rules]

        self.environment_mock.get_sentence_symbol.return_value = Symbol(5)
        self.rule_population_mock.get_terminal_rules.return_value = selected_rules
        self.production_pool_mock.get_effectors.return_value = effectors
        self.production_pool_mock.is_empty.return_value = not effectors

        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock)

        # Then:
        self.environment_mock.get_sentence_symbol.assert_called_once_with(self.current_col)
        self.rule_population_mock.get_terminal_rules.assert_called_once_with(Symbol(5))

    def test_if_rules_allows_should_find_valid_executors(self):
        # Given:
        rule_1 = TerminalRule(Symbol(3), Symbol(5))
        rule_2 = TerminalRule(Symbol(2), Symbol(5))

        # When:
        self.terminal_symbol_scenario([rule_1, rule_2])

        # Then:
        self.production_pool_mock.add_production.assert_has_calls(
            [
                call(TerminalProduction(rule_1)),
                call(TerminalProduction(rule_2))
            ])
        self.environment_mock.add_symbols.assert_called_once_with(
            (self.sut.current_row, self.sut.current_col), [Symbol(3), Symbol(2)])

    def test_if_no_matching_rules_should_find_no_executors(self):
        # Given:
        rule_1 = TerminalRule(Symbol(3), Symbol(8))
        rule_2 = TerminalRule(Symbol(2), Symbol(9))

        # When:
        self.terminal_symbol_scenario([rule_1, rule_2])

        # Then:
        assert_that(self.production_pool_mock.add_production.called, is_(False))
        assert_that(self.environment_mock.add_symbols.called, is_(False))
