from random import Random
from unittest import TestCase
from unittest.mock import create_autospec
from hamcrest import *
from sgcs.factory import Factory
from sgcs.induction import cyk_executors, production, environment
from sgcs.induction.coverage import TerminalCoverageOperator, UniversalCoverageOperator, \
    AggressiveCoverageOperator, StartingCoverageOperator, FullCoverageOperator, CoverageOperations
from sgcs.induction.cyk_configuration import CykConfiguration, CoverageConfiguration, \
    CoverageOperatorsConfiguration, CoverageOperatorConfiguration
from sgcs.induction.cyk_executors import CykTypeId
from sgcs.induction.cyk_service import CykService
from sgcs.induction.rule import Rule, TerminalRule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol, Sentence
from sgcs.utils import Randomizer


class TestModule(TestCase):
    def setUp(self):
        self.sut = None
        self.randomizer = Randomizer(Random())
        self.cyk_configuration = CykConfiguration()
        self.coverage_operations = CoverageOperations()

        self.grammar_sentence = self.create_sentence(
            Symbol('she'),
            Symbol('eats'),
            Symbol('a'),
            Symbol('fish'),
            Symbol('with'),
            Symbol('a'),
            Symbol('fork'))

        self.empty_rule_population = self.create_rules([])

    def create_sut(self, factory):
        self.sut = CykService(factory, self.cyk_configuration,
                              self.randomizer, self.coverage_operations)

    def create_sentence(self, *sentence_seq, is_positive_sentence=True):
        return Sentence(sentence_seq, is_positive_sentence)

    def create_rules(self, rules):
        rule_population = RulePopulation(Symbol('S'), universal_symbol=Symbol('U'))
        for rule in rules:
            rule_population.add_rule(rule)

        return rule_population

    def perform_cyk_scenario(self, sentence, rules_population, belongs_to_grammar):
        # Given:
        factory = Factory({
            CykTypeId.symbol_pair_executor: cyk_executors.CykSymbolPairExecutor,
            CykTypeId.parent_combination_executor: cyk_executors.CykParentCombinationExecutor,
            CykTypeId.cell_executor: cyk_executors.CykCellExecutor,
            CykTypeId.row_executor:
                lambda table_executor, row, executor_factory:
                cyk_executors.CykRowExecutor(table_executor, row, executor_factory) if row > 0
                else cyk_executors.CykFirstRowExecutor(table_executor, row, executor_factory),
            CykTypeId.table_executor: cyk_executors.CykTableExecutor,
            CykTypeId.production_pool: production.ProductionPool,
            CykTypeId.environment: environment.Environment,
            CykTypeId.cyk_result: cyk_executors.CykResult,
            CykTypeId.terminal_cell_executor: cyk_executors.CykTerminalCellExecutor
        })
        self.create_sut(factory)

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

    def prepare_coverage_module(self):
        self.coverage_operations.operators = [
            TerminalCoverageOperator(),
            UniversalCoverageOperator(),
            AggressiveCoverageOperator(),
            StartingCoverageOperator(),
            FullCoverageOperator()
        ]

        terminal_configuration = self.default_coverage_operator_configuration()
        universal_configuration = self.default_coverage_operator_configuration()
        aggressive_configuration = self.default_coverage_operator_configuration()
        starting_configuration = self.default_coverage_operator_configuration()
        full_configuration = self.default_coverage_operator_configuration()

        self.cyk_configuration.coverage = CoverageConfiguration()
        self.cyk_configuration.coverage.operators = CoverageOperatorsConfiguration()

        self.cyk_configuration.coverage.operators.terminal = terminal_configuration
        self.cyk_configuration.coverage.operators.universal = universal_configuration
        self.cyk_configuration.coverage.operators.aggressive = aggressive_configuration
        self.cyk_configuration.coverage.operators.starting = starting_configuration
        self.cyk_configuration.coverage.operators.full = full_configuration

    def default_coverage_operator_configuration(self):
        configuration = CoverageOperatorConfiguration()
        configuration.chance = 0
        return configuration

    def test_adding_coverage_module_should_change_nothing_if_chances_not_set(self):
        self.prepare_coverage_module()

        self.test_another_ok_scenario()

    def test_terminal_coverage_operator_should_work(self):
        # Given:
        self.prepare_coverage_module()
        self.cyk_configuration.coverage.operators.terminal.chance = 1
        rules_population = self.empty_rule_population

        # When:
        self.perform_cyk_scenario(self.grammar_sentence, rules_population, False)

        # Then:
        assert_that(len(rules_population.terminal_rules), is_(equal_to(6)))

    def test_universal_coverage_operator_should_work(self):
        # Given:
        self.prepare_coverage_module()
        self.cyk_configuration.coverage.operators.universal.chance = 1
        rules_population = self.empty_rule_population

        # When:
        self.perform_cyk_scenario(self.grammar_sentence, rules_population, False)

        # Then:
        d = rules_population.terminal_rules
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
        self.prepare_coverage_module()
        self.cyk_configuration.coverage.operators.starting.chance = 1
        sentence = Sentence(
            [Symbol('fork')],
            is_positive_sentence=True
        )
        rules_population = self.empty_rule_population

        # When:
        self.perform_cyk_scenario(sentence, rules_population, True)

        # Then:
        d = rules_population.terminal_rules
        assert_that([d[k] for k in d], only_contains(
            {Symbol('S'): TerminalRule(Symbol('S'), Symbol('fork'))}
        ))
