from random import Random
from unittest import TestCase

from hamcrest import *

from core.rule import Rule, TerminalRule
from core.rule_population import RulePopulation
from core.symbol import Symbol, Sentence
from grammar_estimator import EvolutionStepEstimator
from rule_adding import AddingRulesConfiguration, AddingRuleSupervisor
from sgcs.induction.cyk_configuration import CykConfiguration
from sgcs.induction.cyk_service import CykService
from sgcs.utils import Randomizer
from statistics.grammar_statistics import GrammarStatistics, \
    ClassicRuleStatistics, ClassicFitness, ClassicalStatisticsConfiguration


class TestModule(TestCase):
    def setUp(self):
        self.sut = None
        self.randomizer = Randomizer(Random())
        self.cyk_configuration = CykConfiguration.create(
            should_correct_grammar=False,
            terminal_chance=0,
            universal_chance=0,
            aggressive_chance=0,
            starting_chance=0,
            full_chance=0
        )
        self.statistics_configuration = ClassicalStatisticsConfiguration.default()

        self.statistics = GrammarStatistics.default(self.randomizer, self.statistics_configuration)
        self.rule_adding = AddingRuleSupervisor.default(self.randomizer)

        self.grammar_sentence = self.create_sentence(
            Symbol('she'),
            Symbol('eats'),
            Symbol('a'),
            Symbol('fish'),
            Symbol('with'),
            Symbol('a'),
            Symbol('fork'))

        self.empty_rule_population = self.create_rules([])
        self.example_rule_population = self.create_rules([
            Rule(Symbol('S'), Symbol('A'), Symbol('B')),
            Rule(Symbol('S'), Symbol('A'), Symbol('C')),
            Rule(Symbol('C'), Symbol('S'), Symbol('B')),
            Rule(Symbol('B'), Symbol('B'), Symbol('B'))
        ])
        self.random_rules = self.create_rules([
            Rule(Symbol('S'), Symbol('NP'), Symbol('VP')),
            Rule(Symbol('VP'), Symbol('VP'), Symbol('PP')),
            Rule(Symbol('VP'), Symbol('V'), Symbol('NP')),
            Rule(Symbol('PP'), Symbol('P'), Symbol('NP')),
            Rule(Symbol('NP'), Symbol('Det'), Symbol('N')),
            Rule(Symbol('S'), Symbol('A'), Symbol('B')),
            Rule(Symbol('S'), Symbol('A'), Symbol('C')),
            Rule(Symbol('C'), Symbol('S'), Symbol('B')),
            Rule(Symbol('B'), Symbol('B'), Symbol('B'))
        ])

    def create_sentence(self, *sentence_seq, is_positive_sentence=True):
        return Sentence(sentence_seq, is_positive_sentence)

    def create_rules(self, rules):
        rule_population = RulePopulation(Symbol('S'), universal_symbol=Symbol('U'))
        for rule in rules:
            rule_population.add_rule(rule, self.randomizer)

        return rule_population

    def service_wire_up(self, rules_population):
        # Given:
        self.sut = CykService.default(self.randomizer, self.rule_adding)
        self.sut.configuration = self.cyk_configuration
        self.sut.statistics = self.statistics
        self.sut.traceback = self.sut._traceback_creator(self.sut.statistics.statistics_visitors)

        for rule in rules_population.get_all_non_terminal_rules():
            self.sut.statistics.on_added_new_rule(rule)

    def perform_cyk_scenario(self, sentence, rules_population, belongs_to_grammar):
        # Given:
        self.service_wire_up(rules_population)

        # When:
        cyk_result = self.sut.perform_cyk(rules_population, sentence)

        # Then:
        assert_that(cyk_result.belongs_to_grammar, is_(equal_to(belongs_to_grammar)))

    def test_nok_scenario(self):
        sentence = self.create_sentence(
            Symbol(0),
            Symbol(1),
            Symbol(1),
            Symbol(0),
            Symbol(1),
            Symbol(0),
            Symbol(0))

        self.perform_cyk_scenario(sentence, self.empty_rule_population, False)

    def test_ok_scenario(self):
        # Given:
        sentence = self.create_sentence(
            Symbol('a'),
            Symbol('a'),
            Symbol('b'),
            Symbol('b'))

        rules_population = self.create_rules([
            Rule(Symbol('S'), Symbol('A'), Symbol('B')),
            Rule(Symbol('S'), Symbol('A'), Symbol('C')),
            Rule(Symbol('C'), Symbol('S'), Symbol('B')),
            TerminalRule(Symbol('C'), Symbol('a')),
            Rule(Symbol('B'), Symbol('B'), Symbol('B')),
            TerminalRule(Symbol('B'), Symbol('b')),
            TerminalRule(Symbol('A'), Symbol('a'))
        ])

        # When/Then:
        self.perform_cyk_scenario(sentence, rules_population, True)

    def test_another_ok_scenario(self):
        rules_population = self.create_rules([
            Rule(Symbol('S'), Symbol('NP'), Symbol('VP')),
            Rule(Symbol('VP'), Symbol('VP'), Symbol('PP')),
            Rule(Symbol('VP'), Symbol('V'), Symbol('NP')),
            TerminalRule(Symbol('VP'), Symbol('eats')),
            Rule(Symbol('PP'), Symbol('P'), Symbol('NP')),
            Rule(Symbol('NP'), Symbol('Det'), Symbol('N')),
            TerminalRule(Symbol('NP'), Symbol('she')),
            TerminalRule(Symbol('V'), Symbol('eats')),
            TerminalRule(Symbol('P'), Symbol('with')),
            TerminalRule(Symbol('N'), Symbol('fish')),
            TerminalRule(Symbol('N'), Symbol('fork')),
            TerminalRule(Symbol('Det'), Symbol('a'))
        ])

        self.perform_cyk_scenario(self.grammar_sentence, rules_population, True)

    def test_another_big_ok_scenario(self):
        # Given:
        sentence = self.create_sentence(
            Symbol('1'),
            Symbol('0'),
            Symbol('0'),
            Symbol('0'),
            Symbol('1'),
            Symbol('0'),
            Symbol('1'),
            Symbol('1'),
            Symbol('0'),
            Symbol('1'),
            Symbol('0'),
            Symbol('1'))

        rules_population = self.create_rules([
            Rule(Symbol('S'), Symbol('Z'), Symbol('Y*')),
            Rule(Symbol('S'), Symbol('Y'), Symbol('Z*')),
            TerminalRule(Symbol('Z'), Symbol('0')),
            TerminalRule(Symbol('Y'), Symbol('1')),
            TerminalRule(Symbol('Z*'), Symbol('0')),
            TerminalRule(Symbol('Y*'), Symbol('1')),
            Rule(Symbol('Z*'), Symbol('Z'), Symbol('S')),
            Rule(Symbol('Y*'), Symbol('Y'), Symbol('S')),
            Rule(Symbol('Z*'), Symbol('Y'), Symbol('Z**')),
            Rule(Symbol('Y*'), Symbol('Z'), Symbol('Y**')),
            Rule(Symbol('Z**'), Symbol('Z*'), Symbol('Z*')),
            Rule(Symbol('Y**'), Symbol('Y*'), Symbol('Y*'))
        ])

        # When/Then:
        self.perform_cyk_scenario(sentence, rules_population, True)

    def prepare_rule_adding_module(self):
        self.rule_adding.configuration.crowding.factor = 2
        self.rule_adding.configuration.crowding.size = 3

    def test_adding_coverage_module_should_change_nothing_if_chances_not_set(self):
        self.prepare_rule_adding_module()

        self.test_another_ok_scenario()

    def test_terminal_coverage_operator_should_work(self):
        # Given:
        self.prepare_rule_adding_module()
        self.cyk_configuration.coverage.operators.terminal.chance = 1
        rules_population = self.empty_rule_population

        # When:
        self.perform_cyk_scenario(self.grammar_sentence, rules_population, False)

        # Then:
        assert_that(len(rules_population._terminal_rules), is_(equal_to(6)))

    def test_universal_coverage_operator_should_work(self):
        # Given:
        self.prepare_rule_adding_module()
        self.cyk_configuration.coverage.operators.universal.chance = 1
        rules_population = self.empty_rule_population

        # When:
        self.perform_cyk_scenario(self.grammar_sentence, rules_population, False)

        # Then:
        d = rules_population._terminal_rules
        assert_that([d[k] for k in d], only_contains(
            {Symbol('U'): TerminalRule(Symbol('U'), Symbol('fork'))},
            {Symbol('U'): TerminalRule(Symbol('U'), Symbol('she'))},
            {Symbol('U'): TerminalRule(Symbol('U'), Symbol('eats'))},
            {Symbol('U'): TerminalRule(Symbol('U'), Symbol('a'))},
            {Symbol('U'): TerminalRule(Symbol('U'), Symbol('fish'))},
            {Symbol('U'): TerminalRule(Symbol('U'), Symbol('with'))}
        ))

    def test_starting_coverage_operator_should_work(self):
        # Given:
        self.prepare_rule_adding_module()
        self.cyk_configuration.coverage.operators.starting.chance = 1
        sentence = Sentence(
            [Symbol('fork')],
            is_positive_sentence=True
        )
        rules_population = self.example_rule_population

        # When:
        self.perform_cyk_scenario(sentence, rules_population, True)

        # Then:
        d = rules_population._terminal_rules
        assert_that([d[k] for k in d], only_contains(
            {Symbol('S'): TerminalRule(Symbol('S'), Symbol('fork'))}
        ))

    def test_aggressive_coverage_operator_should_work(self):
        # Given:
        self.prepare_rule_adding_module()
        self.cyk_configuration.coverage.operators.terminal.chance = 1
        self.cyk_configuration.coverage.operators.aggressive.chance = 1
        rules_population = self.example_rule_population
        old_rules = list(rules_population._all_non_terminal_rules.copy())

        # When:
        self.perform_cyk_scenario(self.grammar_sentence, rules_population, False)

        # Then:
        assert_that(rules_population._all_non_terminal_rules, has_length(4))

        d = rules_population._terminal_rules
        assert_that([d[k] for k in d], has_length(6))
        assert_that(list(rules_population._all_non_terminal_rules),
                    is_not(contains_inanyorder(*old_rules)))

    def test_full_coverage_operator_should_work(self):
        # Given:
        self.prepare_rule_adding_module()
        self.cyk_configuration.coverage.operators.terminal.chance = 1
        self.cyk_configuration.coverage.operators.aggressive.chance = 1
        self.cyk_configuration.coverage.operators.full.chance = 1
        rules_population = self.example_rule_population

        # When/Then:
        self.perform_cyk_scenario(self.grammar_sentence, rules_population, True)

    def prepare_default_gcs_module(self):
        self.prepare_rule_adding_module()
        self.cyk_configuration.coverage.operators.terminal.chance = 1
        self.cyk_configuration.coverage.operators.universal.chance = 1
        self.cyk_configuration.coverage.operators.starting.chance = 1
        self.cyk_configuration.coverage.operators.aggressive.chance = 0.33
        self.cyk_configuration.coverage.operators.full.chance = 0.5

    def test_gcs_induction_should_run_smoothly(self):
        # Given:
        self.prepare_default_gcs_module()
        self.cyk_configuration.grammar_correction.should_run = False
        rule_population = self.random_rules

        sentences = [
            self.create_sentence(
                Symbol('she'),
                Symbol('eats'),
                Symbol('a'),
                Symbol('fish'),
                Symbol('with'),
                Symbol('a'),
                Symbol('fork')),

            self.create_sentence(
                Symbol('she'),
                Symbol('eats'),
                Symbol('a'),
                Symbol('fish')),

            self.create_sentence(
                Symbol('he'),
                Symbol('eats'),
                Symbol('a'),
                Symbol('fish'),
                Symbol('with'),
                Symbol('a'),
                Symbol('knife'))
        ]

        len_of_non_terminal_rules = len(list(rule_population.get_all_non_terminal_rules()))

        self.service_wire_up(rule_population)

        evolution_step_estimator = EvolutionStepEstimator()

        # When:
        self.sut.perform_cyk_for_all_sentences(rule_population, sentences, evolution_step_estimator,
                                               self.cyk_configuration, self.statistics)

        # Then:
        assert_that(len(list(rule_population.get_all_non_terminal_rules())),
                    is_(equal_to(len_of_non_terminal_rules)))
