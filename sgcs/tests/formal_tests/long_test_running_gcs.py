import os
import unittest
from random import Random
from unittest.mock import create_autospec

import time
from hamcrest import *

from algorithm.gcs_runner import GcsRunner, AlgorithmConfiguration, FitnessStopCriteria, \
    StepStopCriteria, TimeStopCriteria, CykServiceVariationManager
from datalayer.symbol_translator import SymbolTranslator
from evolution.evolution_configuration import EvolutionRouletteSelectorConfiguration
from grammar_estimator import GrammarEstimator
from induction.cyk_service import CykService, StochasticCykService
from rule_adding import AddingRuleSupervisor, AddingRulesConfiguration, AddingRuleStrategyHint
from statistics.grammar_statistics import GrammarStatistics
from utils import Randomizer


class LongTestRunningGcs(unittest.TestCase):
    def init_data(self):
        self.cyk_variant_manager = CykServiceVariationManager(is_stochastic=self.is_stochastic)
        self.configuration = self.cyk_variant_manager.create_default_configuration()
        self.randomizer = Randomizer(Random())

        self.grammar_estimator = GrammarEstimator()
        self.grammar_statistics = self.cyk_variant_manager.create_grammar_statistics(
            self.randomizer, self.configuration.statistics)

        self.sut = GcsRunner(self.randomizer, self.cyk_variant_manager)

        self.initial_rules = []

        self.set_parameters()

    def create_symbol_translator(self, path):
        return SymbolTranslator.create(path)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_stochastic = False

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
        self.configuration.max_execution_time = 900
        self.configuration.satisfying_fitness = 1

        self.configuration.evolution.operators.crossover.chance = 0.2
        self.configuration.evolution.operators.mutation.chance = 0.8
        self.configuration.evolution.operators.inversion.chance = 0.8

        self.configuration.induction.coverage.operators.aggressive.chance = 0.4
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

    def generic_gcs(self, path):
        print('TEST FOR:', path)

        for i in range(3):
            print('RUN', i)
            self.init_data()
            try:
                symbol_translator = self.create_symbol_translator(path)

                result = self.sut.perform_gcs(self.initial_rules,
                                              list(symbol_translator.get_sentences()),
                                              self.configuration, self.grammar_estimator,
                                              self.grammar_statistics)
                print(result[1].stop_reasoning_message())

                print('Statistics:')
                for sc in self.sut.stop_criteria:
                    print(sc.stop_reasoning_message().split(':')[1])
                # print('fitness:', self.grammar_estimator['fitness'].get_global_max())
                # print('runs:', self.steps_stop_criteria.current_step)
                # print('execution time:', time.clock() - self.time_stop_criteria.start_time)
            except Exception as ex:
                raise ex

    def test_gcs_for_tomita_l1(self):
        self.generic_gcs(self.mk_path('tomita 1.txt'))

    def test_gcs_for_tomita_l2(self):
        self.generic_gcs(self.mk_path('tomita 2.txt'))

    def test_gcs_for_tomita_l3(self):
        self.generic_gcs(self.mk_path('tomita 3.txt'))

    def test_gcs_for_tomita_l4(self):
        self.generic_gcs(self.mk_path('tomita 4.txt'))

    def test_gcs_for_tomita_l5(self):
        self.generic_gcs(self.mk_path('tomita 5.txt'))

    def test_gcs_for_tomita_l6(self):
        self.generic_gcs(self.mk_path('tomita 6.txt'))

    def test_gcs_for_tomita_l7(self):
        self.generic_gcs(self.mk_path('tomita 7.txt'))


class LongTestRunningSGcs(LongTestRunningGcs):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_stochastic = True

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
        self.configuration.max_execution_time = 900
        self.configuration.satisfying_fitness = 1

        self.configuration.evolution.operators.crossover.chance = 0.2
        self.configuration.evolution.operators.mutation.chance = 0.8
        self.configuration.evolution.operators.inversion.chance = 0.8

        self.configuration.induction.coverage.operators.aggressive.chance = 0.4
        self.configuration.induction.coverage.operators.aggressive.adding_hint = \
            AddingRuleStrategyHint.expand_population

        self.configuration.rule.adding.crowding.factor = 18
        self.configuration.rule.adding.crowding.size = 3
        self.configuration.rule.adding.elitism.is_used = True
        self.configuration.rule.adding.elitism.size = 3
        self.configuration.rule.adding.max_non_terminal_rules = 40

    def create_symbol_translator(self, path):
        translator = super().create_symbol_translator(path)
        translator.negative_allowed = False
        return translator
