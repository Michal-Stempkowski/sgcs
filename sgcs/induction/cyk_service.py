from enum import Enum
from sgcs.factory import Factory
from sgcs.induction.cyk_executors import CykTypeId


class CykService(object):
    def __init__(self, factory, configuration, randomizer):
        self.factory = factory
        self.table_executor = self.factory.create(CykTypeId.table_executor, self.factory)
        self._configuration = configuration
        self._randomizer = randomizer

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
