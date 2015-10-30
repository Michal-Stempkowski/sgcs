from abc import abstractmethod
from sgcs.induction.production import TerminalProduction
from sgcs.induction.rule import TerminalRule


class CoverageOperator(object):
    def __init__(self, cyk_service, chance):
        self.cyk_service = cyk_service
        self.chance = chance

    def cover(self, environment, rule_population, coordinates):
        if self.cyk_service.randomizer.perform_with_chance(self.chance):
            return self.cover_impl(environment, rule_population, coordinates)

        return TerminalProduction(None, coordinates)

    @abstractmethod
    def cover_impl(self, environment, rule_population, coordinates):
        pass


class TerminalCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        parent = rule_population.get_random_terminal_symbol(self.cyk_service.randomizer)
        return TerminalProduction(
            TerminalRule(parent, environment.get_sentence_symbol(coordinates[1])),
            coordinates)


class UniversalCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        child = environment.get_sentence_symbol(coordinates[1])
        return TerminalProduction(
            TerminalRule(rule_population.universal_symbol, child),
            coordinates)


class StartingCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        if environment.get_sentence_length() == 1 and environment.is_sentence_positive():
            only_symbol = environment.get_sentence_symbol(0)
            return TerminalProduction(
                TerminalRule(rule_population.starting_symbol, only_symbol),
                coordinates)
        else:
            return TerminalProduction(None, coordinates)


class AggressiveCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance)

    def cover_impl(self, environment, rule_population, coordinates):
        if environment.is_sentence_positive():
            return True
        else:
            return TerminalProduction(None, coordinates)
