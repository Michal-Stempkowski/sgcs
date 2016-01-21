import logging
import unittest

from hamcrest import *

from core.rule import Rule
from core.rule_population import StochasticRulePopulation
from core.symbol import Symbol
from executors.simulation_executor import SimulationExecutor


class TestSimulationExecutor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO,
                            filename=r"C:\Users\Michał\PycharmProjects\mgr\sgcs\log.log",
                            format='%(asctime)s %(message)s')

        self.sut = SimulationExecutor()
        self.starting_symbol = Symbol(1)

    def test_population_saving_and_loading(self):
        # Given:
        path = r"C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\data\experimental"
        name = 'tmp'
        terminal_rule = Rule(Symbol(101), Symbol(-101))
        non_terminal_rule = Rule(Symbol(101), Symbol(101), Symbol(101))

        population = StochasticRulePopulation(self.starting_symbol)
        population.add_rule(terminal_rule, self.sut.randomizer)
        population.add_rule(non_terminal_rule, self.sut.randomizer)

        # When:
        self.sut.save_population(population, lambda _: '', path, name)
        loaded_pop = self.sut.load_population(path, name, starting_symbol=self.starting_symbol)

        # Then:
        assert_that(loaded_pop.get_all_non_terminal_rules(), only_contains(non_terminal_rule))
        assert_that(loaded_pop.get_terminal_rules(), only_contains(terminal_rule))
