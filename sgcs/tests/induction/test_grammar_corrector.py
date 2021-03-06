import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.rule import TerminalRule, Rule
from core.rule_population import RulePopulation
from core.symbol import Symbol
from induction.cyk_service import CykService
from induction.grammar_corrector import GrammarCorrector
from statistics.grammar_statistics import GrammarStatistics


class TestGrammarCorrector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = GrammarCorrector()

        self.rule_population_mock = create_autospec(RulePopulation)
        self.rule_population_mock.configure_mock(universal_symbol=Symbol('U'),
                                                 starting_symbol=Symbol('S'))
        self.statistics_mock = create_autospec(GrammarStatistics)

        self.rule_a = self.mk_rule('A', 'a')
        self.rule_b = self.mk_rule('B', 'a')
        self.universal_symbol = self.mk_rule('U', 'c')

        self.accessible_rule = self.mk_rule('C', 'A', 'B')
        self.second_lvl_accessible_rule = self.mk_rule('T', 'A', 'B')
        self.not_accessible_rule = self.mk_rule('X', 'H', 'B')
        self.starting_symbol = self.mk_rule('S', 'H', 'H')

        self.rule_accessible_from_top = self.mk_rule('H', 'J', 'G')
        self.second_lvl_rule_accessible_from_top = self.mk_rule('G', 'M', 'C')

    @staticmethod
    def mk_rule(parent, left_child, right_child=None):
        if right_child is None:
            return TerminalRule(Symbol(parent), Symbol(left_child))
        else:
            return Rule(Symbol(parent), Symbol(left_child), Symbol(right_child))

    def production_correction_scenario(self, terminal_rules, to_be_removed, correction_function):
        self.rule_population_mock.get_terminal_rules.return_value = \
            iter(terminal_rules)
        self.rule_population_mock.get_all_non_terminal_rules.return_value = [
            self.accessible_rule,
            self.not_accessible_rule,
            self.starting_symbol,
            self.second_lvl_accessible_rule,
            self.rule_accessible_from_top,
            self.second_lvl_rule_accessible_from_top
        ]

        correction_function(self.rule_population_mock, self.statistics_mock)

        call_args = set(map(lambda x: x[0][0],
                            self.rule_population_mock.remove_rule.call_args_list))
        assert_that(call_args, contains_inanyorder(*to_be_removed))

    def test_universal_symbol_practically_disables_non_productive_correction(self):
        self.production_correction_scenario([self.rule_a, self.rule_b, self.universal_symbol],
                                            [], self.sut.remove_non_productive)

    def test_should_be_able_to_remove_non_productive_rules(self):
        self.production_correction_scenario([self.rule_a, self.rule_b],
                                            [self.not_accessible_rule,
                                             self.starting_symbol,
                                             self.rule_accessible_from_top,
                                             self.second_lvl_rule_accessible_from_top],
                                            self.sut.remove_non_productive)

    def test_should_be_able_to_remove_not_reachable_rules(self):
        self.production_correction_scenario([self.rule_a, self.rule_b, self.universal_symbol],
                                            [self.not_accessible_rule,
                                             self.second_lvl_accessible_rule],
                                            self.sut.remove_not_reachable)

    def test_should_be_able_to_remove_all_unnecessary_rules(self):
        self.production_correction_scenario([self.rule_a, self.rule_b, self.universal_symbol],
                                            [self.not_accessible_rule,
                                             self.second_lvl_accessible_rule],
                                            self.sut.correct_grammar)

        self.production_correction_scenario([self.rule_a, self.rule_b],
                                            [self.not_accessible_rule,
                                             self.starting_symbol,
                                             self.rule_accessible_from_top,
                                             self.second_lvl_rule_accessible_from_top,
                                             self.second_lvl_accessible_rule],
                                            self.sut.correct_grammar)
