from datalayer.jsonizer import SimpleJsonNode


class EvolutionConfiguration(SimpleJsonNode):
    @staticmethod
    def create(selectors, inversion_chance, mutation_chance, crossover_chance):
        configuration = EvolutionConfiguration()

        configuration.operators = EvolutionOperatorsConfiguration.create(
            inversion_chance, mutation_chance, crossover_chance)

        configuration.selectors = selectors
        configuration.custom_rule_adding_hint = None

        return configuration

    def __init__(self):
        self.operators = None
        self.selectors = []
        self.custom_rule_adding_hint = None


class EvolutionOperatorsConfiguration(SimpleJsonNode):
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


class EvolutionOperatorConfiguration(SimpleJsonNode):
    @staticmethod
    def create(chance):
        configuration = EvolutionOperatorConfiguration()
        configuration.chance = chance
        return configuration

    def __init__(self):
        self.chance = None


class EvolutionSelectorType(object):
    random = 0
    tournament = 1
    roulette = 2


class EvolutionSelectorConfiguration(SimpleJsonNode):
    def __init__(self):
        self.type = None

    def __eq__(self, other):
        return other is not None and self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.type)


class EvolutionRandomSelectorConfiguration(EvolutionSelectorConfiguration):
    @staticmethod
    def create():
        return EvolutionRandomSelectorConfiguration()

    def __init__(self):
        super().__init__()
        self.type = EvolutionSelectorType.random


class EvolutionTournamentSelectorConfiguration(EvolutionSelectorConfiguration):
    @staticmethod
    def create(tournament_size=3):
        configuration = EvolutionTournamentSelectorConfiguration()
        configuration.tournament_size = tournament_size
        return configuration

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
