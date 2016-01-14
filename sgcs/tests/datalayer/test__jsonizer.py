import logging
import random
import unittest

from hamcrest import *

from core.rule import Rule
from core.rule_population import RulePopulation, StochasticRulePopulation
from core.symbol import Symbol
from datalayer.jsonizer import RulePopulationJsonizer
from utils import Randomizer


class TestJsonizer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO,
                            filename=r"C:\Users\Michał\PycharmProjects\mgr\sgcs\log.log",
                            format='%(asctime)s %(message)s')

        self.starting_symbol = Symbol(1)
        self.terminal_rule = Rule(Symbol(101), Symbol(-101))
        self.non_terminal_rule = Rule(Symbol(101), Symbol(101), Symbol(101))
        self.sut = RulePopulationJsonizer(
            RulePopulationJsonizer.make_binding_map(
                [
                    RulePopulation,
                    StochasticRulePopulation
                ]
            )
        )
        self.randomizer = Randomizer(random.Random())

    def _rule_population_serialization_scenario(self, population):
        # Given:
        population.add_rule(self.terminal_rule, self.randomizer)
        population.add_rule(self.non_terminal_rule, self.randomizer)

        # When:
        json = self.sut.to_json(population)
        pop2 = self.sut.from_json(json, self.randomizer, starting_symbol=self.starting_symbol)

        # Then:
        assert_that(pop2, is_not(None))
        assert_that(pop2.get_all_non_terminal_rules(), only_contains(self.non_terminal_rule))
        assert_that(pop2.get_terminal_rules(), only_contains(self.terminal_rule))

    def test_rule_population_serialization(self):
        self._rule_population_serialization_scenario(RulePopulation(self.starting_symbol))

    def test_stochastic_rule_population_serialization(self):
        self._rule_population_serialization_scenario(StochasticRulePopulation(self.starting_symbol))
