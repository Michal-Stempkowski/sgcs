from sgcs.induction.rule import TerminalRule
from sgcs.induction.symbol import Symbol


class TerminalCoverageOperator(object):
    def __init__(self, cyk_service):
        self.cyk_service = cyk_service

    def cover(self, environment, rule_population, coordinates):
        chance = self.cyk_service.configuration.coverage.operators.terminal.chance
        if self.cyk_service.randomizer.perform_with_chance(chance):
            parent = rule_population.get_random_terminal_symbol(self.cyk_service.randomizer)
            return TerminalRule(parent, environment.get_sentence_symbol(coordinates[1]))

        return None
