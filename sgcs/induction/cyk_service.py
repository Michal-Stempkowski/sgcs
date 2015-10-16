from enum import Enum
from sgcs.factory import Factory
from sgcs.induction.cyk_executors import CykTypeId


class CykService(object):
    def __init__(self, factory):
        self.factory = factory
        self.table_executor = self.factory.create(CykTypeId.table_executor, self.factory)

    def perform_cyk(self, rules_population, sentence):
        environment = self.factory.create(CykTypeId.environment, sentence)
        result = self.table_executor.execute(environment, rules_population)
        return result
