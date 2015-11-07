from enum import Enum
from sgcs.factory import Factory
from sgcs.induction.coverage import CoverageOperations
from sgcs.induction.cyk_executors import CykTypeId
from sgcs.induction.cyk_statistics import DummyCykStatistics


class CykService(object):
    def __init__(self, factory, configuration, randomizer, coverage_operations=None,
                 statistics=None):
        self.factory = factory
        self.table_executor = self.factory.create(CykTypeId.table_executor, self)
        self._configuration = configuration
        self._randomizer = randomizer
        self._coverage_operations = coverage_operations \
            if coverage_operations else CoverageOperations()
        self._statistics = statistics if statistics else DummyCykStatistics()

    def perform_cyk(self, rules_population, sentence):
        environment = self.factory.create(CykTypeId.environment, sentence, self.factory)
        result = self.table_executor.execute(environment, rules_population)
        return result

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
