import json
import os
from random import Random

from algorithm.gcs_runner import AlgorithmConfiguration, RuleConfiguration, AlgorithmVariant, \
    CykServiceVariationManager
from algorithm.gcs_simulator import AsyncGcsSimulator
from core.rule import Rule
from core.rule_population import RulePopulation, StochasticRulePopulation
from core.symbol import Symbol
from datalayer.jsonizer import BasicJsonizer, RulePopulationJsonizer
from datalayer.symbol_translator import SymbolTranslator
from evolution.evolution_configuration import EvolutionConfiguration, EvolutionOperatorConfiguration, \
    EvolutionOperatorsConfiguration, EvolutionSelectorConfiguration, \
    EvolutionRandomSelectorConfiguration, EvolutionTournamentSelectorConfiguration, \
    EvolutionRouletteSelectorConfiguration
from gui.proxy.simulator_proxy import PyQtAwareAsyncGcsSimulator
from induction.cyk_configuration import CoverageConfiguration, CoverageOperatorConfiguration, \
    CoverageOperatorsConfiguration, CykConfiguration, GrammarCorrection
from rule_adding import AddingRulesConfiguration, CrowdingConfiguration, ElitismConfiguration
from statistics.grammar_statistics import ClassicalStatisticsConfiguration
from utils import Randomizer


class SimulationExecutor(object):
    POPULATION_EXT = ".pop"
    GRAMMAR_ESTIMATOR_EXT = ".grest"
    RUN_SUMMARY_EXT = ".txt"

    def __init__(self):
        self.configuration_serializer = BasicJsonizer([
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
        self.population_serializer = RulePopulationJsonizer(
            RulePopulationJsonizer.make_binding_map(
                [
                    RulePopulation,
                    StochasticRulePopulation
                ]
            )
        )

        self.randomizer = Randomizer(Random())

    def prepare_simulation(self, runner, task_no, data_path, config_path, population_path=None):
        with open(config_path) as f:
            configuration = self.configuration_serializer.from_json(json.load(f))

        is_stochastic = configuration.algorithm_variant == AlgorithmVariant.sgcs
        algorithm_variant = CykServiceVariationManager(is_stochastic)
        learning_set_path, testing_set_path = self.load_input_config(data_path)

        learning_set = SymbolTranslator.create(learning_set_path)
        learning_set.negative_allowed = not algorithm_variant.is_stochastic

        testing_set = SymbolTranslator.create(testing_set_path)
        testing_set.negative_allowed = True

        return lambda conf: self._perform_simulation(
            algorithm_variant, learning_set, testing_set, conf, runner, task_no), configuration

    def _perform_simulation(self, algorithm_variant, learning_set, testing_set, configuration,
                            runner, task_no):
        algorithm_simulator = PyQtAwareAsyncGcsSimulator(self.randomizer, algorithm_variant,
                                                         task_no, runner.input_queue)

        result, ngen, grammar_estimator, population = algorithm_simulator.perform_simulation(
            learning_set, testing_set, configuration)

        print(result)
        print('NGen:', ngen)

        return result, ngen, grammar_estimator, population

    @staticmethod
    def _artifact_file(path, name, extension, mode='r'):
        return open(os.path.join(path, name + extension), mode)

    def save_population(self, rule_population, path, name):
        serialized_population = self.population_serializer.to_json(rule_population)
        with self._artifact_file(path, name, self.POPULATION_EXT, 'w+') as pop_file:
            json.dump(serialized_population, pop_file, sort_keys=True, indent=4)

    def load_population(self, path, name, *pop_args, **pop_kwargs):
        with self._artifact_file(path, name, self.POPULATION_EXT) as pop_file:
            serialized_population = json.load(pop_file)
            return self.population_serializer.from_json(serialized_population,
                                                        self.randomizer, *pop_args, **pop_kwargs)

    def save_grammar_estimator(self, grammar_estimator, path, name):
        serialized_grammar_estimator = grammar_estimator.json_coder()
        with self._artifact_file(path, name, self.POPULATION_EXT, 'w+') as est_file:
            json.dump(serialized_grammar_estimator, est_file, sort_keys=True, indent=4)

    @staticmethod
    def load_input_config(config_path):
        with open(config_path) as file:
            deserialized = json.loads('\n'.join(file.readlines()))

            return deserialized['learning'], deserialized['testing']

    def save_execution_summary(self, run_estimator, ngen, path, name):
        with self._artifact_file(path, name, self.RUN_SUMMARY_EXT, 'w+') as summary_f:
            summary_f.write('{0}\n'.format(run_estimator))
            summary_f.write('Ngen: {0}\n'.format(ngen))
