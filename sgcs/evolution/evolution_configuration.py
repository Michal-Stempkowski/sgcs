from enum import Enum


class EvolutionConfiguration(object):
    @staticmethod
    def create(selectors, inversion_chance, mutation_chance, crossover_chance):
        configuration = EvolutionConfiguration()
        configuration.operators = EvolutionOperatorsConfiguration.create(
            inversion_chance, mutation_chance, crossover_chance)
        configuration.selectors = selectors
        return configuration

    def __init__(self):
        self.operators = None
        self.selectors = []


class EvolutionOperatorsConfiguration(object):
    @staticmethod
    def create(inversion_chance, mutation_chance, crossover_chance):
        configuration = EvolutionOperatorsConfiguration()
        configuration.inversion = EvolutionOperatorConfiguration.create(inversion_chance)
        configuration.mutation = EvolutionOperatorConfiguration.create(mutation_chance)
        configuration.crossover = EvolutionOperatorConfiguration.create(crossover_chance)
        return configuration

    def __init__(self):
        self.inversion = None
        self.mutation = None
        self.crossover = None


class EvolutionOperatorConfiguration(object):
    @staticmethod
    def create(chance):
        configuration = EvolutionOperatorConfiguration()
        configuration.chance = chance
        return configuration

    def __init__(self):
        self.chance = None


class EvolutionSelectorType(Enum):
    random = 0
    tournament = 1
    roulette = 2


class EvolutionSelectorConfiguration(object):
    def __init__(self):
        self.type = None


class EvolutionRandomSelectorConfiguration(EvolutionSelectorConfiguration):
    @staticmethod
    def create():
        return EvolutionRandomSelectorConfiguration()

    def __init__(self):
        super().__init__()
        self.type = EvolutionSelectorType.random


class EvolutionTournamentSelectorConfiguration(EvolutionSelectorConfiguration):
    @staticmethod
    def create(tournament_size):
        configuration = EvolutionTournamentSelectorConfiguration()
        configuration.tournament_size = tournament_size

    def __init__(self):
        super().__init__()
        self.type = EvolutionSelectorType.tournament
        self.tournament_size = None


class EvolutionRouletteSelectorConfiguration(EvolutionSelectorConfiguration):
    @staticmethod
    def create():
        return EvolutionRouletteSelectorConfiguration()

    def __init__(self):
        super().__init__()
        self.type = EvolutionSelectorType.roulette
