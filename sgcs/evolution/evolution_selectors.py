from abc import ABCMeta, abstractmethod
from itertools import accumulate

from evolution.evolution_configuration import EvolutionSelectorType


class Selector(metaclass=ABCMeta):
    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def select(self, service, grammar_statistics, rule_population):
        pass


class RandomSelector(Selector):
    def type(self):
        return EvolutionSelectorType.random

    def select(self, service, grammar_statistics, rule_population):
        return rule_population.get_random_rules(service.randomizer, False, 1)[0]


class TournamentSelector(Selector):
    def type(self):
        return EvolutionSelectorType.tournament

    def select(self, service, grammar_statistics, rule_population):
        configuration = next(x for x in service.configuration.selectors if x.type == self.type())
        tournament_size = configuration.tournament_size
        tournament = rule_population.get_random_rules(service.randomizer, False, tournament_size)
        return max(*tournament,
                   key=grammar_statistics.fitness.get_keyfunc_getter(grammar_statistics))


class RouletteSelector(Selector):
    def type(self):
        return EvolutionSelectorType.roulette

    @staticmethod
    def _create_roulette(grammar_statistics, rule_population, rules):
        fitnesses = map(grammar_statistics.fitness.get_keyfunc_getter(grammar_statistics), rules)
        roulette = list(accumulate(fitnesses))
        roulette_size = roulette[-1]
        return roulette, roulette_size

    def select(self, service, grammar_statistics, rule_population):
        rules = rule_population.get_all_non_terminal_rules()
        roulette, roulette_size = self._create_roulette(grammar_statistics, rule_population, rules)
        roulette_value = service.randomizer.uniform(0, roulette_size)
        return rules[next(i for i, f in enumerate(roulette) if roulette_value < f)]
