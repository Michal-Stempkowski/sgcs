import os
import unittest
from random import Random
from unittest.mock import create_autospec

from hamcrest import *

from algorithm.gcs_runner import GcsRunner, AlgorithmConfiguration
from datalayer.symbol_translator import SymbolTranslator
from evolution.evolution_configuration import EvolutionRouletteSelectorConfiguration
from induction.cyk_service import CykService
from rule_adding import AddingRuleSupervisor, AddingRulesConfiguration
from statistics.grammar_statistics import GrammarStatistics
from utils import Randomizer


class LongTestRunningGcs(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configuration = AlgorithmConfiguration.default()
        self.randomizer = Randomizer(Random())

        self.sut = GcsRunner(self.configuration, self.randomizer)

        self.initial_rules = []

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
        self.configuration.induction.coverage.operators.full.chance = 1
        self.configuration.max_algorithm_steps = 1
        self.configuration.rule.max_non_terminal_symbols = 40
        self.configuration.evolution.operators.crossover = 0.2
        self.configuration.evolution.operators.mutation = 0.8
        self.configuration.evolution.operators.inversion = 0.8
        self.configuration.induction.coverage.operators.aggressive.chance = 1
        self.configuration.rule.adding.crowding.factor = 18
        self.configuration.rule.adding.crowding.size = 3
        self.configuration.rule.adding.elitism.is_used = True
        self.configuration.rule.adding.elitism.size = 3

        self.sut.grammar_statistics.fitness.positive_weight = 1
        self.sut.grammar_statistics.fitness.negative_weight = 2
        self.sut.grammar_statistics.fitness.classical_fitness_weight = 1
        self.sut.grammar_statistics.fitness.fertility_weight = 0
        self.sut.grammar_statistics.fitness.base_fitness = 0.5

    def test_gcs_for_tomita_l1(self):
        symbol_translator = SymbolTranslator.create(self.mk_path('tomita 1.txt'))

        self.sut.perform_gcs(self.initial_rules, symbol_translator)
