import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.rule import TerminalRule, Rule
from core.rule_population import RulePopulation
from core.symbol import Symbol, Sentence
from induction.cyk_executors import CykResult
from induction.cyk_service import CykService
from induction.detector import Detector
from induction.environment import Environment
from induction.production import Production
from induction.traceback import Traceback
from statistics.grammar_statistics import GrammarStatistics


class TestTraceback(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.visitor1_calls = []
        self.visitor2_calls = []
        self.sut = Traceback([lambda x, _1, _2, _3, _4: self.visitor1_calls.append(x),
                              lambda x, _1, _2, _3, _4: self.visitor2_calls.append(x)])

        self.grammar_statistics_mock = create_autospec(GrammarStatistics)

        self.cyk_service_mock = create_autospec(CykService)
        self.cyk_service_mock.configure_mock(statistics=self.grammar_statistics_mock)

        self.environment_mock = create_autospec(Environment)
        self.environment_mock.configure_mock(sentence=create_autospec(Sentence))

        self.rule_population_mock = create_autospec(RulePopulation)
        self.rule_population_mock.configure_mock(starting_symbol=Symbol('S'))

        self.cyk_result = CykResult()

    @staticmethod
    def mk_production(coordinates, parent, left_child, right_child=None):
        if right_child is None:
            rule = TerminalRule(Symbol(parent), Symbol(left_child))
        else:
            rule = Rule(Symbol(parent), Symbol(left_child), Symbol(right_child))

        return Production(Detector(coordinates), rule)

    def test_for_terminal_rule_traceback_should_call_visitors(self):
        # Given:
        self.cyk_result.belongs_to_grammar = True

        production = self.mk_production((0, 0, 0, 0, 0), 'S', 'a')
        self.environment_mock.get_last_cell_productions.return_value = [production]
        self.environment_mock.get_child_productions.return_value = []

        # When:
        self.sut.perform_traceback(self.cyk_service_mock, self.environment_mock,
                                   self.cyk_result, self.rule_population_mock)

        # # Then:
        assert_that(self.environment_mock.get_last_cell_productions.call_count, is_(equal_to(1)))
        assert_that(self.visitor1_calls, only_contains(production))
        assert_that(self.visitor2_calls, only_contains(production))

    def test_for_non_terminal_rule_traceback_should_traverse_table(self):
        # Given:
        self.cyk_result.belongs_to_grammar = True

        base_production = self.mk_production((1, 0, 1, 0, 0), 'S', 'A', 'B')
        left_production = self.mk_production((0, 0, 0, 0, 0), 'A', 'a')
        left_production_2 = self.mk_production((0, 0, 0, 0, 0), 'A', 'e')
        right_production = self.mk_production((0, 1, 0, 0, 0), 'B', 'b')
        all_productions = [base_production, left_production, left_production_2, right_production]
        self.environment_mock.get_last_cell_productions.return_value = [base_production]
        self.environment_mock.get_child_productions.side_effect = \
            lambda x: all_productions[1:] if x == base_production else []

        # When:
        self.sut.perform_traceback(self.cyk_service_mock, self.environment_mock,
                                   self.cyk_result, self.rule_population_mock)

        # Then:
        assert_that(self.environment_mock.get_last_cell_productions.call_count, is_(equal_to(1)))
        assert_that(self.visitor1_calls, contains(
            base_production, left_production, left_production_2, right_production))
        assert_that(self.visitor2_calls, contains(
            base_production, left_production, left_production_2, right_production))

    def test_should_start_with_starting_symbol_only(self):
        # Given:
        self.cyk_result.belongs_to_grammar = True

        production = self.mk_production((0, 0, 0, 0, 0), 'A', 'a')
        self.environment_mock.get_last_cell_productions.return_value = [production]
        self.environment_mock.get_child_productions.return_value = []

        # When:
        self.sut.perform_traceback(self.cyk_service_mock, self.environment_mock,
                                   self.cyk_result, self.rule_population_mock)

        # Then:
        assert_that(self.environment_mock.get_last_cell_productions.call_count, is_(equal_to(1)))
        assert_that(self.visitor1_calls, is_(empty()))
        assert_that(self.visitor2_calls, is_(empty()))
