from sgcs.induction.coverage.coverage_operators import CoverageOperations
from sgcs.induction.coverage.rule_adding import AddingRuleSupervisor
from sgcs.induction.cyk_executors import CykTypeId
from sgcs.induction.cyk_statistics import DummyCykStatistics, PasiekaFitness, ClassicFitness


class CykService(object):
    def __init__(self, factory, configuration, randomizer, coverage_operations=None,
                 statistics=None, fitness=None):
        self.factory = factory
        self.table_executor = self.factory.create(CykTypeId.table_executor, self)
        self._configuration = configuration
        self._randomizer = randomizer
        self._coverage_operations = coverage_operations \
            if coverage_operations else CoverageOperations()
        self._statistics = statistics if statistics else DummyCykStatistics()
        self._fitness = fitness
        self._rule_adding = AddingRuleSupervisor()

    def perform_cyk(self, rules_population, sentence):
        environment = self.factory.create(CykTypeId.environment, sentence, self.factory)
        result = self.table_executor.execute(environment, rules_population)
        return result

    def perform_cyk_for_all_sentences(self, rule_population, sentences):
        for sentence in sentences:
            result = self.perform_cyk(rule_population, sentence)
            # if result

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
