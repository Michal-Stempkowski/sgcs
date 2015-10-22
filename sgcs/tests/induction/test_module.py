from random import Random
from unittest import TestCase
from unittest.mock import create_autospec
from hamcrest import *
from sgcs.factory import Factory
from sgcs.induction import cyk_executors, production, environment
from sgcs.induction.cyk_configuration import CykConfiguration
from sgcs.induction.cyk_executors import CykTypeId
from sgcs.induction.cyk_service import CykService
from sgcs.induction.rule import Rule, TerminalRule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol, Sentence
from sgcs.utils import Randomizer


class TestModule(TestCase):
    def setUp(self):
        self.sut = None
        self.random_number_generator_mock = create_autospec(Random)
        self.randomizer = Randomizer(self.random_number_generator_mock)
        self.cyk_configuration = CykConfiguration()

    def create_sut(self, factory):
        self.sut = CykService(factory, self.cyk_configuration, self.randomizer)

    def create_sentence(self, *sentence_seq):
        return Sentence(sentence_seq)

    def create_rules(self, rules):
        rule_population = RulePopulation(Symbol('S'))
        for rule in rules:
            rule_population.add_rule(rule)

        return rule_population

    def perform_cyk_scenario(self, sentence, rules_population, belongs_to_grammar):
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

        cyk_result = self.sut.perform_cyk(rules_population, sentence)
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

        rules_population = self.create_rules([])

        self.perform_cyk_scenario(sentence, rules_population, False)

    def test_ok_scenario(self):
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

        self.perform_cyk_scenario(sentence, rules_population, True)

    def test_another_ok_scenario(self):
        sentence = self.create_sentence(
            Symbol('she'),
            Symbol('eats'),
            Symbol('a'),
            Symbol('fish'),
            Symbol('with'),
            Symbol('a'),
            Symbol('fork'))

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

        self.perform_cyk_scenario(sentence, rules_population, True)

    def test_another_big_ok_scenario(self):
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

        self.perform_cyk_scenario(sentence, rules_population, True)
