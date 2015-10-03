import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.induction.cyk_executors import CykSymbolPairExecutor, CykParentCombinationExecutor
from sgcs.induction.environment import Environment
from sgcs.induction.production import ProductionPool
from sgcs.induction.rule import Rule
from sgcs.induction.rule_population import RulePopulation


class TestCykSymbolPairExecutor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initialize_mocks()
        self.initialize_coordinates()

        self.sut = CykSymbolPairExecutor(self.parent_executor, self.left_id, self.right_id)

    def initialize_mocks(self):
        self.parent_executor = create_autospec(CykParentCombinationExecutor)
        self.environment_mock = create_autospec(Environment)
        self.rule_population_mock = create_autospec(RulePopulation)
        self.production_pool_mock = create_autospec(ProductionPool)

        self.production_pool_mock.add_production.side_effect = self.capture_production
        self.captured_productions = []

    def initialize_coordinates(self):
        self.left_id = 0
        self.right_id = 1

        self.parent_executor.current_row.return_value = 2
        self.parent_executor.current_col.return_value = 3
        self.parent_executor.shift.return_value = 4

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
