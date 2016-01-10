import json
from random import Random

from algorithm.gcs_runner import AlgorithmConfiguration, RuleConfiguration, AlgorithmVariant, \
    CykServiceVariationManager
from algorithm.gcs_simulator import AsyncGcsSimulator
from core.symbol import Symbol
from datalayer.jsonizer import ConfigurationJsonizer
from datalayer.symbol_translator import SymbolTranslator
from evolution.evolution_configuration import EvolutionConfiguration, EvolutionOperatorConfiguration, \
    EvolutionOperatorsConfiguration, EvolutionSelectorConfiguration, \
    EvolutionRandomSelectorConfiguration, EvolutionTournamentSelectorConfiguration, \
    EvolutionRouletteSelectorConfiguration
from induction.cyk_configuration import CoverageConfiguration, CoverageOperatorConfiguration, \
    CoverageOperatorsConfiguration, CykConfiguration, GrammarCorrection
from rule_adding import AddingRulesConfiguration, CrowdingConfiguration, ElitismConfiguration
from statistics.grammar_statistics import ClassicalStatisticsConfiguration
from utils import Randomizer


class SimulationExecutor(object):
    def __init__(self):
        self.configuration_serializer = ConfigurationJsonizer([
            AddingRulesConfiguration,
            CrowdingConfiguration,
            ElitismConfiguration,
            AlgorithmConfiguration,
            RuleConfiguration,
            Symbol,
            EvolutionConfiguration,
            EvolutionOperatorConfiguration,
            EvolutionOperatorsConfiguration,
            EvolutionSelectorConfiguration,
            CoverageConfiguration,
            CoverageOperatorConfiguration,
            CoverageOperatorsConfiguration,
            CykConfiguration,
            GrammarCorrection,
            ClassicalStatisticsConfiguration,
            EvolutionRandomSelectorConfiguration,
            EvolutionTournamentSelectorConfiguration,
            EvolutionRouletteSelectorConfiguration
        ])
        self.randomizer = Randomizer(Random())

    def prepare_simulation(self, data_path, config_path, population_path=None):
        with open(config_path) as f:
            configuration = self.configuration_serializer.from_json(json.load(f))

        is_stochastic = configuration.algorithm_variant == AlgorithmVariant.sgcs

        learning_set_path, testing_set_path = self.load_input_config(data_path)
        learning_set = SymbolTranslator.create(learning_set_path)
        learning_set.negative_allowed = not is_stochastic

        testing_set = SymbolTranslator.create(testing_set_path)
        testing_set.negative_allowed = True

        algorithm_variant = CykServiceVariationManager(is_stochastic)

        return lambda conf: self._perform_simulation(
            algorithm_variant, learning_set, testing_set, conf), configuration

    def _perform_simulation(self, algorithm_variant, learning_set, testing_set, configuration):
        algorithm_simulator = AsyncGcsSimulator(self.randomizer, algorithm_variant)

        result, ngen = algorithm_simulator.perform_simulation(
            learning_set, testing_set, configuration)

        print(result)
        print('NGen:', ngen)

    @staticmethod
    def load_input_config(config_path):
        with open(config_path) as file:
            deserialized = json.loads('\n'.join(file.readlines()))

            return deserialized['learning'], deserialized['testing']
