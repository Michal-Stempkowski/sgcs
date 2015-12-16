import logging

from factory import Factory
from induction import cyk_executors
from induction.coverage_operators import CoverageOperations
from induction.environment import Environment
from induction.grammar_corrector import GrammarCorrector
from induction.production import ProductionPool
from induction.traceback import Traceback, ThoroughTraceback, StochasticBestTreeTraceback
from sgcs.induction.cyk_executors import CykTypeId
from statistics.grammar_statistics import DummyCykStatistics


class CykService(object):
    @staticmethod
    def default(randomizer, adding_rule_supervisor):
        factory = Factory({
            CykTypeId.symbol_pair_executor: cyk_executors.CykSymbolPairExecutor,
            CykTypeId.parent_combination_executor: cyk_executors.CykParentCombinationExecutor,
            CykTypeId.cell_executor: cyk_executors.CykCellExecutor,
            CykTypeId.row_executor:
                lambda table_executor, row, executor_factory:
                cyk_executors.CykRowExecutor(table_executor, row, executor_factory) if row > 0
                else cyk_executors.CykFirstRowExecutor(table_executor, row, executor_factory),
            CykTypeId.table_executor: cyk_executors.CykTableExecutor,
            CykTypeId.production_pool: ProductionPool,
            CykTypeId.environment: Environment,
            CykTypeId.cyk_result: cyk_executors.CykResult,
            CykTypeId.terminal_cell_executor: cyk_executors.CykTerminalCellExecutor
        })

        coverage_operations = CoverageOperations.create_default_set()
        traceback_creator = Traceback

        return CykService(
            factory,
            randomizer,
            adding_rule_supervisor,
            coverage_operations,
            traceback_creator
        )

    def __init__(self, factory, randomizer, adding_rule_supervisor=None,
                 coverage_operations=None, traceback_creator=None,
                 grammar_corrector=None):
        self.factory = factory
        self.table_executor = self.factory.create(CykTypeId.table_executor, self)
        self._configuration = None
        self._randomizer = randomizer
        self._coverage_operations = coverage_operations \
            if coverage_operations else CoverageOperations()
        self._statistics = None
        self._rule_adding = adding_rule_supervisor
        self._traceback_creator = traceback_creator
        self._traceback = None
        self.grammar_corrector = GrammarCorrector() if grammar_corrector is None \
            else grammar_corrector

    def perform_cyk(self, rules_population, sentence):
        logging.debug(str(sentence))
        environment = self.factory.create(CykTypeId.environment, sentence, self.factory)
        result = self.table_executor.execute(environment, rules_population)
        self.traceback.perform_traceback(self, environment, result, rules_population)
        return result

    def perform_cyk_for_all_sentences(self, rule_population, sentences, evolution_step_estimator,
                                      configuration, statistics):
        self.configuration = configuration
        self.statistics = statistics
        self.traceback = self._traceback_creator(self.statistics.statistics_visitors)

        if self.configuration.grammar_correction.should_run:
            self.grammar_corrector.correct_grammar(rule_population, self.statistics)

        cnt = 0
        for sentence in sentences:
            cnt += 1
            result = self.perform_cyk(rule_population, sentence)
            evolution_step_estimator.append_result(result)

        self.statistics.update_fitness()

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self._configuration = value

    @property
    def randomizer(self):
        return self._randomizer

    @property
    def coverage_operations(self):
        return self._coverage_operations

    @property
    def statistics(self):
        return self._statistics

    @statistics.setter
    def statistics(self, value):
        self._statistics = value

    @property
    def rule_adding(self):
        return self._rule_adding

    @property
    def fitness(self):
        return self._fitness

    @fitness.setter
    def fitness(self, value):
        self._fitness = value

    @property
    def traceback(self):
        return self._traceback

    @traceback.setter
    def traceback(self, value):
        self._traceback = value


class StochasticCykService(CykService):
    @staticmethod
    def default(randomizer, adding_rule_supervisor):
        factory = Factory({
            CykTypeId.symbol_pair_executor: cyk_executors.CykStochasticSymbolPairExecutor,
            CykTypeId.parent_combination_executor: cyk_executors.CykParentCombinationExecutor,
            CykTypeId.cell_executor: cyk_executors.CykCellExecutor,
            CykTypeId.row_executor:
                lambda table_executor, row, executor_factory:
                cyk_executors.CykRowExecutor(table_executor, row, executor_factory) if row > 0
                else cyk_executors.CykFirstRowExecutor(table_executor, row, executor_factory),
            CykTypeId.table_executor: cyk_executors.CykStochasticTableExecutor,
            CykTypeId.production_pool: ProductionPool,
            CykTypeId.environment: Environment.with_viterbi_approach,
            CykTypeId.cyk_result: cyk_executors.CykResult,
            CykTypeId.terminal_cell_executor: cyk_executors.CykStochasticTerminalCellExecutor
        })

        coverage_operations = CoverageOperations.create_default_set()
        traceback_creator = StochasticBestTreeTraceback

        return StochasticCykService(
            factory,
            randomizer,
            adding_rule_supervisor,
            coverage_operations,
            traceback_creator
        )

    def perform_cyk_for_all_sentences(self, rule_population, sentences, evolution_step_estimator,
                                      configuration, statistics):
        super().perform_cyk_for_all_sentences(rule_population, sentences, evolution_step_estimator,
                                              configuration, statistics)
        rule_population.perform_probability_estimation(
            statistics.fitness.get_keyfunc_getter(statistics))
