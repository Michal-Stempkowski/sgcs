import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *
from sgcs.factory import Factory
from sgcs.induction.cyk_executors import *
from sgcs.induction.environment import Environment
from sgcs.induction.production import ProductionPool
from sgcs.induction.rule import Rule
from sgcs.induction.rule_population import RulePopulation
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
                ExecutorLevel.per_parent_combination: self.child_mocker(CykSymbolPairExecutor),
                ExecutorLevel.per_cell: self.child_mocker(CykParentCombinationExecutor),
                ExecutorLevel.per_row: self.child_mocker(CykCellExecutor),
                ExecutorLevel.per_table: self.child_mocker(CykRowExecutor)
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

        type( self.parent_executor).current_row = PropertyMock(return_value=2)
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

    def test_parent_combinations_should_be_executed(self):
        # When:
        self.sut.execute(self.environment_mock, self.rule_population_mock,
                         self.production_pool_mock)

        # Then:
        assert_that(self.children_created, are_(
            [
                (self.sut, 1, self.executor_factory),
                (self.sut, 2, self.executor_factory),
                (self.sut, 3, self.executor_factory)
            ]
        ))


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
        self.sut.execute(self.environment_mock, self.rule_population_mock,
                         self.production_pool_mock)

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
        self.sut.execute(self.environment_mock, self.rule_population_mock,
                         self.production_pool_mock)

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
