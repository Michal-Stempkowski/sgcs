import logging
import os
import unittest
from random import Random
from unittest.mock import create_autospec

import time
from hamcrest import *

from algorithm.gcs_runner import GcsRunner, AlgorithmConfiguration, FitnessStopCriteria, \
    StepStopCriteria, TimeStopCriteria, CykServiceVariationManager
from algorithm.gcs_simulator import GcsSimulator, AsyncGcsSimulator
from datalayer.symbol_translator import SymbolTranslator
from evolution.evolution_configuration import EvolutionRouletteSelectorConfiguration
from grammar_estimator import GrammarEstimator
from induction.cyk_service import CykService
from rule_adding import AddingRuleSupervisor, AddingRulesConfiguration, AddingRuleStrategyHint
from statistics.grammar_statistics import GrammarStatistics
from utils import Randomizer


class LongTestGcsSimulator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO,
                            filename=r"C:\Users\Michał\PycharmProjects\mgr\sgcs\log.log",
                            format='%(asctime)s %(message)s')

        self.algorithm_variant = CykServiceVariationManager(is_stochastic=False)

        self.configuration = self.algorithm_variant.create_default_configuration()
        self.randomizer = Randomizer(Random())

        self.sut = GcsSimulator(self.randomizer, self.algorithm_variant)

        self.set_parameters()

    def mk_path(self, relative):
        return os.path.join(r"C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\data\example gramatics",
                            relative)

    def set_parameters(self):
        self.configuration.should_run_evolution = True
        self.configuration.evolution.selectors = [
            EvolutionRouletteSelectorConfiguration.create(),
            EvolutionRouletteSelectorConfiguration.create()
        ]

        self.configuration.induction.grammar_correction.should_run = False
        self.configuration.induction.coverage.operators.terminal.chance = 1
        self.configuration.induction.coverage.operators.universal.chance = 0
        self.configuration.induction.coverage.operators.starting.chance = 1
        self.configuration.induction.coverage.operators.starting.adding_hint = \
            AddingRuleStrategyHint.expand_population
        self.configuration.induction.coverage.operators.full.chance = 1
        self.configuration.induction.coverage.operators.full.adding_hint = \
            AddingRuleStrategyHint.expand_population

        self.configuration.max_algorithm_steps = 5000
        self.configuration.rule.max_non_terminal_symbols = 19
        self.configuration.rule.random_starting_population_size = 30
        self.configuration.max_execution_time = 8000
        self.configuration.satisfying_fitness = 1

        self.configuration.evolution.operators.crossover.chance = 0.2
        self.configuration.evolution.operators.mutation.chance = 0.8
        self.configuration.evolution.operators.inversion.chance = 0.8

        self.configuration.induction.coverage.operators.aggressive.chance = 0
        self.configuration.induction.coverage.operators.aggressive.adding_hint = \
            AddingRuleStrategyHint.expand_population

        self.configuration.rule.adding.crowding.factor = 18
        self.configuration.rule.adding.crowding.size = 3
        self.configuration.rule.adding.elitism.is_used = True
        self.configuration.rule.adding.elitism.size = 3
        self.configuration.rule.adding.max_non_terminal_rules = 40

        self.configuration.statistics.positive_weight = 1
        self.configuration.statistics.negative_weight = 2
        self.configuration.statistics.classical_fitness_weight = 1
        self.configuration.statistics.fertility_weight = 0
        self.configuration.statistics.base_fitness = 0.5
        self.configuration.max_algorithm_runs = 50

    def generic_simulation(self, learning_path, testing_path, name):
        logging.info('starting %s', name)
        with open(os.path.join(r'C:\Users\Michał\PycharmProjects\mgr\runs\auto',
                               name + '.txt'), 'w+') as file:
            learning_set = SymbolTranslator.create(learning_path)
            learning_set.negative_allowed = not self.algorithm_variant.is_stochastic

            testing_set = SymbolTranslator.create(testing_path)
            testing_set.negative_allowed = True

            result, ngen, grammar_estimator, population, *_ = self.sut.perform_simulation(
                learning_set, testing_set, self.configuration)

            print(result)
            print('NGen:', ngen)
            file.write(str(result))
            file.write(str(ngen))

    def test_simulation_dummy_test(self):
        learning_set = self.mk_path('tomita 1.txt')
        testing_set = self.mk_path('tomita 1.txt')

        self.generic_simulation(learning_set, testing_set, 'tomita 1')

    def test_simulation_for_tomita_l1(self):
        learning_set = self.mk_path('tomita 1.txt')
        testing_set = self.mk_path('t1 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 1')

    def test_simulation_for_tomita_l2(self):
        learning_set = self.mk_path('tomita 2.txt')
        testing_set = self.mk_path('t2 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 2')

    def test_simulation_for_tomita_l3(self):
        learning_set = self.mk_path('tomita 3.txt')
        testing_set = self.mk_path('t3 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 3')

    def test_simulation_for_tomita_l4(self):
        learning_set = self.mk_path('tomita 4.txt')
        testing_set = self.mk_path('t4 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 4')

    def test_simulation_for_tomita_l5(self):
        learning_set = self.mk_path('tomita 5.txt')
        testing_set = self.mk_path('t5 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 5')

    def test_simulation_for_tomita_l6(self):
        learning_set = self.mk_path('tomita 6.txt')
        testing_set = self.mk_path('t6 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 6')

    def test_simulation_for_tomita_l7(self):
        learning_set = self.mk_path('tomita 7.txt')
        testing_set = self.mk_path('t7 opt 15 max')

        self.generic_simulation(learning_set, testing_set, 'tomita 7')

    def test_simulation_for_tomita_l5_l7(self):
        print('tomita l5')
        learning_set = self.mk_path('tomita 5.txt')
        testing_set = self.mk_path('t5 opt 15 max')
        self.generic_simulation(learning_set, testing_set, 'tomita 5')

        print('tomita l6')
        learning_set = self.mk_path('tomita 6.txt')
        testing_set = self.mk_path('t6 opt 15 max')
        self.generic_simulation(learning_set, testing_set, 'tomita 6')

        print('tomita l7')
        learning_set = self.mk_path('tomita 7.txt')
        testing_set = self.mk_path('t7 opt 15 max')
        self.generic_simulation(learning_set, testing_set, 'tomita 7')

    def test_simulation_for_tomita_l1_l7(self):
        self.generic_simulation(self.mk_path('tomita 1.txt'), self.mk_path('t1 opt 15 max'), 'tomita 1')

        self.generic_simulation(self.mk_path('tomita 2.txt'), self.mk_path('t2 opt 15 max'), 'tomita 2')

        self.generic_simulation(self.mk_path('tomita 3.txt'), self.mk_path('t3 opt 15 max'), 'tomita 3')

        self.generic_simulation(self.mk_path('tomita 4.txt'), self.mk_path('t4 opt 15 max'), 'tomita 4')

        self.generic_simulation(self.mk_path('tomita 5.txt'), self.mk_path('t5 opt 15 max'), 'tomita 5')

        self.generic_simulation(self.mk_path('tomita 6.txt'), self.mk_path('t6 opt 15 max'), 'tomita 6')

        self.generic_simulation(self.mk_path('tomita 7.txt'), self.mk_path('t7 opt 15 max'), 'tomita 7')

    def test_simulation_for_other_gramatics(self):
        self.configuration.max_algorithm_steps = 1000
        self.configuration.max_algorithm_runs = 10
        self.generic_simulation(self.mk_path('ab los 200 30'), self.mk_path('ab opt max 15'), 'ab')

        self.generic_simulation(self.mk_path('anbn los 200 15'), self.mk_path('anbn opt 15 max'), 'anbn')

        self.generic_simulation(self.mk_path('bra1 los2 200 30'), self.mk_path('bra1 opt 15 max'), 'bra1')

        self.generic_simulation(self.mk_path('bra3 los 200 30'), self.mk_path('bra3 opt los 65534'), 'bra3')

        self.generic_simulation(self.mk_path('toy los2 200 30'), self.mk_path('toy opt los 65534'), 'toy')

        self.generic_simulation(self.mk_path('pal2 parz los 200'), self.mk_path('pal2 opt parzysty max 15'), 'pal2')


class LongTestSGcsSimulator(LongTestGcsSimulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.algorithm_variant = CykServiceVariationManager(is_stochastic=True)

        self.configuration = self.algorithm_variant.create_default_configuration()

        self.sut = GcsSimulator(self.randomizer, self.algorithm_variant)

        self.set_parameters()

    def set_parameters(self):
        self.configuration.should_run_evolution = True
        self.configuration.evolution.selectors = [
            EvolutionRouletteSelectorConfiguration.create(),
            EvolutionRouletteSelectorConfiguration.create()
        ]

        self.configuration.induction.grammar_correction.should_run = False
        self.configuration.induction.coverage.operators.terminal.chance = 1
        self.configuration.induction.coverage.operators.universal.chance = 0
        self.configuration.induction.coverage.operators.starting.chance = 1
        self.configuration.induction.coverage.operators.starting.adding_hint = \
            AddingRuleStrategyHint.expand_population
        self.configuration.induction.coverage.operators.full.chance = 1
        self.configuration.induction.coverage.operators.full.adding_hint = \
            AddingRuleStrategyHint.expand_population

        self.configuration.max_algorithm_steps = 5000
        self.configuration.rule.max_non_terminal_symbols = 19
        self.configuration.rule.random_starting_population_size = 30
        self.configuration.max_execution_time = 8000
        self.configuration.satisfying_fitness = 1

        self.configuration.evolution.operators.crossover.chance = 0.2
        self.configuration.evolution.operators.mutation.chance = 0.8
        self.configuration.evolution.operators.inversion.chance = 0.8

        self.configuration.induction.coverage.operators.aggressive.chance = 0
        self.configuration.induction.coverage.operators.aggressive.adding_hint = \
            AddingRuleStrategyHint.expand_population

        self.configuration.rule.adding.crowding.factor = 18
        self.configuration.rule.adding.crowding.size = 3
        self.configuration.rule.adding.elitism.is_used = True
        self.configuration.rule.adding.elitism.size = 3
        self.configuration.rule.adding.max_non_terminal_rules = 40


class LongTestAsyncSGcsSimulator(LongTestSGcsSimulator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sut = AsyncGcsSimulator(self.randomizer, self.algorithm_variant)
