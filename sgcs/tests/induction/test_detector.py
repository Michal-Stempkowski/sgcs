import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.induction.detector import Detector
from sgcs.induction.environment import Environment, CykTableIndexError
from sgcs.induction.rule import Rule
from sgcs.induction.rule_population import RulePopulation


class TestDetector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinates = (4, 4, 2, 0, 1)  # current_row, current_col, shift, left_id, right_id
        self.environment_mock = create_autospec(Environment)
        self.rule_population_mock = create_autospec(RulePopulation)
        self.sut = Detector(self.coordinates)

    def generate_population_given_symbols_and_rules(self, symbols, rules):
        self.environment_mock.get_detector_symbols.return_value = symbols
        self.rule_population_mock.get_rules_by_right.return_value = rules

        return self.sut.generate_production(
            self.environment_mock, self.rule_population_mock)

    def test_invalid_coord_should_cause_an_exception(self):
        self.environment_mock.get_detector_symbols.side_effect = \
            CykTableIndexError(self.coordinates)

        assert_that(
            calling(self.sut.generate_production).
                with_args(self.environment_mock, self.rule_population_mock),
            raises(CykTableIndexError, repr(self.coordinates)))

        self.environment_mock.get_detector_symbols.assert_called_once_with(self.coordinates)
        assert_that(self.rule_population_mock.get_rules_by_right.call_count, is_(equal_to(0)))

    def test_on_no_rules_generate_production_should_return_empty_production(self):
        # Given:
        symbols = ('B', 'C')
        rules = []

        # When:
        productions = self.generate_population_given_symbols_and_rules(symbols, rules)

        # Then:
        assert_that(productions, has_length(1))
        only_production = productions[0]
        assert_that(only_production.is_empty())
        assert_that(only_production.detector, is_(equal_to(self.sut)))
        self.rule_population_mock.get_rules_by_right.assert_called_once_with(symbols)
        self.environment_mock.get_detector_symbols.assert_called_once_with(self.coordinates)

    def test_on_many_rules_many_productions_should_be_generated(self):
        # Given:
        symbols = ('B', 'C')
        rules = [Rule('A', 'B', 'C'), Rule('D', 'B', 'C')]

        # When:
        productions = self.generate_population_given_symbols_and_rules(symbols, rules)

        # Then:
        assert_that(productions, has_length(2))
        prod_a, prod_b = productions
        self.assertTrue(all(not prod.is_empty() for prod in productions))
        assert_that(prod_a.detector, is_(equal_to(self.sut)))
        assert_that(prod_b.detector, is_(equal_to(self.sut)))
        assert_that(prod_a.rule, is_(equal_to(rules[0])))
        assert_that(prod_b.rule, is_(equal_to(rules[1])))
        self.rule_population_mock.get_rules_by_right.assert_called_once_with(symbols)
        self.environment_mock.get_detector_symbols.assert_called_once_with(self.coordinates)
