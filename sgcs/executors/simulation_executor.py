import json
import os
from random import Random

import math

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

from algorithm.gcs_runner import AlgorithmConfiguration, RuleConfiguration, AlgorithmVariant, \
    CykServiceVariationManager
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
from statistics.grammar_statistics import ClassicalStatisticsConfiguration, \
    PasiekaStatisticsConfiguration
from utils import Randomizer


class GrammarCriteriaPainter(object):
    DIAGRAM_EXT = '.png'
    DIAGRAM_EXT2 = '.pdf'

    def __init__(self, criteria, out_name=None):
        self.criteria = criteria
        self.out_name = out_name if out_name else self.criteria

    def paint(self, grammar_estimator, path, configuration):
        data = grammar_estimator[self.criteria]
        steps = range(configuration.max_algorithm_steps)

        x = []
        y = []

        x_min = []
        y_min = []

        x_max = []
        y_max = []

        for step in steps:
            value = data.get(step)
            min_value = data.get_min(step)
            max_value = data.get_max(step)
            if not math.isnan(value):
                y.append(value)
                x.append(step)
            if not math.isnan(min_value):
                y_min.append(min_value)
                x_min.append(step)
            if not math.isnan(max_value):
                y_max.append(max_value)
                x_max.append(step)

        fig = Figure()
        canvas = FigureCanvasAgg(fig)

        ax = fig.add_axes([.1, .1, .8, .8], title='{0}/steps'.format(self.criteria))
        self._plot_line(ax, x_min, y_min, 'dashed', self.criteria + '_min',
                        no_points=True, color='cyan')
        self._plot_line(ax, x_max, y_max, 'dashed', self.criteria + '_max',
                        no_points=True, color='cyan')
        self._plot_line(ax, x, y, 'solid', self.criteria)

        font_p = FontProperties()
        font_p.set_size('small')
        ax.legend(prop=font_p, loc='best')

        if not x:
            ax.text(0, 0, 'No data to generate valid diagram', style='italic',
                    bbox={'facecolor': 'red', 'alpha': 0.5, 'pad': 10})

        fig.set_size_inches(22, 12)
        fig.savefig(os.path.join(path, self.out_name + self.DIAGRAM_EXT), dpi=60)

    @staticmethod
    def _plot_line(ax, x_axis, y_axis, linestyle, name, no_points=False, color='blue'):
        ax.plot(x_axis, y_axis, color=color, linestyle=linestyle, label=name, marker='')
        if not no_points:
            ax.scatter(x_axis, y_axis, marker='+')


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
            PasiekaStatisticsConfiguration,
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

        self.diagram_painter = [
            GrammarCriteriaPainter('missrate'),
            GrammarCriteriaPainter('fallout'),
            GrammarCriteriaPainter('sensitivity'),
            GrammarCriteriaPainter('specificity'),
            GrammarCriteriaPainter('accuracy'),
            GrammarCriteriaPainter('precision'),
            GrammarCriteriaPainter('falseomission'),
            GrammarCriteriaPainter('falsediscovery'),
            GrammarCriteriaPainter('negpredictive')
        ]

        self.randomizer = Randomizer(Random())

    def prepare_simulation(self, runner, task_no, data_path, config_path, population_path=None):
        with open(config_path) as f:
            configuration = self.configuration_serializer.from_json(json.load(f))

        is_stochastic = configuration.algorithm_variant == AlgorithmVariant.sgcs
        algorithm_variant = CykServiceVariationManager(is_stochastic)
        learning_set_path, testing_set_path = self.load_input_config(data_path)

        learning_set = SymbolTranslator.create(learning_set_path)
        learning_set.negative_allowed = configuration.statistics.negative_sentence_learning

        testing_set = SymbolTranslator.create(testing_set_path)
        testing_set.negative_allowed = True

        return (lambda conf: self._perform_simulation(
            algorithm_variant, learning_set, testing_set, conf, runner, task_no),
            configuration,
            self._mk_population_printer(learning_set)
        )

    @staticmethod
    def _mk_population_printer(translator):
        return lambda x: translator.rule_population_to_string(x)

    def _perform_simulation(self, algorithm_variant, learning_set, testing_set, configuration,
                            runner, task_no):
        algorithm_simulator = PyQtAwareAsyncGcsSimulator(self.randomizer, algorithm_variant,
                                                         task_no, runner.input_queue)

        result, ngen, gener_grammar_estimator, population, grammar_estimator = \
            algorithm_simulator.perform_simulation(learning_set, testing_set, configuration)

        return result, ngen, grammar_estimator, population, gener_grammar_estimator

    @staticmethod
    def _artifact_file(path, name, extension, mode='r'):
        return open(os.path.join(path, name + extension), mode)

    def save_population(self, rule_population, population_printer, path, name):
        self.save_population_data(rule_population, path, name)
        with self._artifact_file(path, name + '_view', self.RUN_SUMMARY_EXT, 'w+') as pop_view_file:
            pop_view_file.write('{0}\n'.format(population_printer(rule_population)))

    def save_population_data(self, rule_population, path, name):
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
        with self._artifact_file(path, name, self.GRAMMAR_ESTIMATOR_EXT, 'w+') as est_file:
            json.dump(serialized_grammar_estimator, est_file, sort_keys=True, indent=4)

    @staticmethod
    def load_input_config(config_path):
        with open(config_path) as file:
            deserialized = json.loads('\n'.join(file.readlines()))

            return deserialized['learning'], deserialized['testing']

    def save_execution_summary(self, run_estimator, ngen, generalisation_data, path, name):
        with self._artifact_file(path, name, self.RUN_SUMMARY_EXT, 'w+') as summary_f:
            summary_f.write('{0}\n'.format(run_estimator))
            summary_f.write('Ngen: {0}\n'.format(ngen))

            for criteria, value in generalisation_data.criterias.items():
                summary_f.write('{0}: {1}\n'.format(criteria, value.get(0)))

    def generate_grammar_estimation_diagrams(self, grammar_estimator, path, configuration):
        for painter in self.diagram_painter:
            painter.paint(grammar_estimator, path, configuration)
