from enum import Enum


class EvolutionConfiguration(object):
    def __init__(self):
        self.operators = None
        self.selectors = []


class EvolutionOperatorsConfiguration(object):
    def __init__(self):
        self.inversion = None
        self.mutation = None
        self.crossover = None


class EvolutionOperatorConfiguration(object):
    def __init__(self):
        self.chance = None


class EvolutionSelectorType(Enum):
    random = 0
    tournament = 1
    roulette = 2


class EvolutionSelectorConfiguration(object):
    def __init__(self):
        self.type = None


class EvolutionTournamentSelectorConfiguration(EvolutionSelectorConfiguration):
    def __init__(self):
        super().__init__()
        self.type = EvolutionSelectorType.tournament
        self.tournament_size = None
