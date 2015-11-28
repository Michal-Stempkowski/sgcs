from factory import Factory
from induction import cyk_executors
from induction.coverage_operators import CoverageOperations
from induction.environment import Environment
from induction.grammar_corrector import GrammarCorrector
from induction.production import ProductionPool
from induction.traceback import Traceback
from sgcs.induction.cyk_executors import CykTypeId
from statistics.grammar_statistics import DummyCykStatistics


class CykService(object):
    @staticmethod
    def default(configuration, randomizer, adding_rule_supervisor, grammar_statistics):
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
        traceback = Traceback(grammar_statistics.statistics_visitors)

        return CykService(
            factory,
            configuration,
            randomizer,
            adding_rule_supervisor,
            grammar_statistics,
            coverage_operations,
            traceback
        )

    def __init__(self, factory, configuration, randomizer, adding_rule_supervisor=None,
                 statistics=None, coverage_operations=None, traceback=None,
                 grammar_corrector=None):
        self.factory = factory
        self.table_executor = self.factory.create(CykTypeId.table_executor, self)
        self._configuration = configuration
        self._randomizer = randomizer
        self._coverage_operations = coverage_operations \
            if coverage_operations else CoverageOperations()
        self._statistics = statistics if statistics else DummyCykStatistics()
        self._rule_adding = adding_rule_supervisor
        self._traceback = Traceback([]) if traceback is None else traceback
        self.grammar_corrector = GrammarCorrector() if grammar_corrector is None \
            else grammar_corrector

    def perform_cyk(self, rules_population, sentence):
        environment = self.factory.create(CykTypeId.environment, sentence, self.factory)
        result = self.table_executor.execute(environment, rules_population)
        self.traceback.perform_traceback(self, environment, result, rules_population)
        return result

    def perform_cyk_for_all_sentences(self, rule_population, sentences, evolution_step_estimator):
        if self.configuration.grammar_correction.should_run:
            self.grammar_corrector.correct_grammar(rule_population, self.statistics)

        for sentence in sentences:
            result = self.perform_cyk(rule_population, sentence)
            evolution_step_estimator.append_result(result)

        self.statistics.update_fitness()

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self.configuration = value

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
