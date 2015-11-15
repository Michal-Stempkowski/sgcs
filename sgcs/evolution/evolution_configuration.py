class EvolutionConfiguration(object):
    def __init__(self):
        self.operators = None


class EvolutionOperatorsConfiguration(object):
    def __init__(self):
        self.inversion = None
        self.mutation = None
        self.crossover = None


class EvolutionOperatorConfiguration(object):
    def __init__(self):
        self.chance = None
