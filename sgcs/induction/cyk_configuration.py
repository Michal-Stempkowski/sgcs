from datalayer.jsonizer import SimpleJsonNode


class CykConfiguration(SimpleJsonNode):
    def __init__(self):
        self._coverage = None
        self._grammar_correction = None

    @staticmethod
    def create(should_correct_grammar, terminal_chance, universal_chance, aggressive_chance,
               starting_chance, full_chance):
        configuration = CykConfiguration()
        configuration.coverage = CoverageConfiguration.create(
            terminal_chance, universal_chance, aggressive_chance, starting_chance, full_chance)
        configuration.grammar_correction = GrammarCorrection.create(should_correct_grammar)
        return configuration

    @property
    def coverage(self):
        return self._coverage

    @coverage.setter
    def coverage(self, value):
        self._coverage = value

    @property
    def grammar_correction(self):
        return self._grammar_correction

    @grammar_correction.setter
    def grammar_correction(self, value):
        self._grammar_correction = value


class CoverageConfiguration(SimpleJsonNode):
    def __init__(self):
        self._operators = None

    @staticmethod
    def create(*args):
        configuration = CoverageConfiguration()
        configuration.operators = CoverageOperatorsConfiguration.create(*args)
        return configuration

    @property
    def operators(self):
        return self._operators

    @operators.setter
    def operators(self, value):
        self._operators = value


class CoverageOperatorsConfiguration(SimpleJsonNode):
    def __init__(self):
        self._terminal = None
        self._universal = None
        self._aggressive = None
        self._starting = None
        self._full = None

    @staticmethod
    def create(terminal_chance, universal_chance, aggressive_chance, starting_chance, full_chance):
        configuration = CoverageOperatorsConfiguration()

        configuration.terminal = CoverageOperatorConfiguration.create(terminal_chance, None)

        configuration.universal = CoverageOperatorConfiguration.create(universal_chance, None)

        configuration.aggressive = CoverageOperatorConfiguration.create(aggressive_chance, None)

        configuration.starting = CoverageOperatorConfiguration.create(starting_chance, None)

        configuration.full = CoverageOperatorConfiguration.create(full_chance, None)

        return configuration

    @property
    def terminal(self):
        return self._terminal

    @terminal.setter
    def terminal(self, value):
        self._terminal = value

    @property
    def universal(self):
        return self._universal

    @universal.setter
    def universal(self, value):
        self._universal = value

    @property
    def aggressive(self):
        return self._aggressive

    @aggressive.setter
    def aggressive(self, value):
        self._aggressive = value

    @property
    def starting(self):
        return self._starting

    @starting.setter
    def starting(self, value):
        self._starting = value

    @property
    def full(self):
        return self._full

    @full.setter
    def full(self, value):
        self._full = value


class CoverageOperatorConfiguration(SimpleJsonNode):
    def __init__(self):
        self._chance = None
        self.adding_hint = None

    @staticmethod
    def create(chance, adding_hint):
        configuration = CoverageOperatorConfiguration()
        configuration.chance = chance
        configuration.adding_hint = adding_hint
        return configuration

    @property
    def chance(self):
        return self._chance

    @chance.setter
    def chance(self, value):
        self._chance = value


class GrammarCorrection(SimpleJsonNode):
    def __init__(self):
        self.should_run = False

    @staticmethod
    def create(should_run):
        configuration = GrammarCorrection()
        configuration.should_run = should_run
        return configuration


class InvalidCykConfigurationError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return repr(self.error)
