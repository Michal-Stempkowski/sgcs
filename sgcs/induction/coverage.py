from abc import abstractmethod
from sgcs.induction.rule import TerminalRule


class CoverageOperator(object):
    def __init__(self, cyk_service, chance):
        self.cyk_service = cyk_service
        self.chance = chance

    def cover(self, environment, rule_population, coordinates):
        if self.cyk_service.randomizer.perform_with_chance(self.chance):
            return self.cover_impl(environment, rule_population, coordinates)

        return None

    @abstractmethod
    def cover_impl(self, environment, rule_population, coordinates):
        pass


class TerminalCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        parent = rule_population.get_random_terminal_symbol(self.cyk_service.randomizer)
        return TerminalRule(parent, environment.get_sentence_symbol(coordinates[1]))


class UniversalCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        return True


class StartingCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        return True
