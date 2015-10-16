from unittest import TestCase
from hamcrest import *
from sgcs.factory import Factory
from sgcs.induction import cyk_executors, production, environment
from sgcs.induction.cyk_executors import CykTypeId
from sgcs.induction.cyk_service import CykService
from sgcs.induction.rule import Rule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol, Sentence


class TestModule(TestCase):
    def setUp(self):
        self.sut = None

    def create_sut(self, factory):
        self.sut = CykService(factory)

    def create_sentence(self, *sentence_seq):
        return Sentence([Symbol(x) for x in sentence_seq])

    def create_rules(self, rules):
        rule_population = RulePopulation()
        for rule in rules:
            rule_population.add_rule(rule)

        return rule_population

    def test_nok_scenario(self):
        factory = Factory({
            CykTypeId.symbol_pair_executor: cyk_executors.CykSymbolPairExecutor,
            CykTypeId.parent_combination_executor: cyk_executors.CykParentCombinationExecutor,
            CykTypeId.cell_executor: cyk_executors.CykCellExecutor,
            CykTypeId.row_executor: cyk_executors.CykRowExecutor,
            CykTypeId.table_executor: cyk_executors.CykTableExecutor,
            CykTypeId.production_pool: production.ProductionPool,
            CykTypeId.environment: environment.Environment,
            CykTypeId.cyk_result: cyk_executors.CykResult
        })

        sentence = self.create_sentence(0, 1, 1, 0, 1, 0, 0)
        rules_population = self.create_rules([
            # Rule(2, 0, )
        ])
        self.create_sut(factory)

        cyk_result = self.sut.perform_cyk(rules_population, sentence)
        assert_that(cyk_result.belongs_to_grammar, is_(False))
