class CykConfiguration(object):
    def __init__(self):
        self._coverage = None
        self._rule_adding = None
        self._grammar_correction = None

    @property
    def coverage(self):
        return self._coverage

    @coverage.setter
    def coverage(self, value):
        self._coverage = value

    @property
    def rule_adding(self):
        return self._rule_adding

    @rule_adding.setter
    def rule_adding(self, value):
        self._rule_adding = value

    @property
    def grammar_correction(self):
        return self._grammar_correction

    @grammar_correction.setter
    def grammar_correction(self, value):
        self._grammar_correction = value


class CoverageConfiguration(object):
    def __init__(self):
        self._operators = None

    @property
    def operators(self):
        return self._operators

    @operators.setter
    def operators(self, value):
        self._operators = value


class CoverageOperatorsConfiguration(object):
    def __init__(self):
        self._terminal = None
        self._universal = None
        self._aggressive = None
        self._starting = None
        self._full = None

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


class CoverageOperatorConfiguration(object):
    def __init__(self):
        self._chance = None

    @property
    def chance(self):
        return self._chance

    @chance.setter
    def chance(self, value):
        self._chance = value


class AddingRulesConfiguration(object):
    def __init__(self):
        self._crowding = None

    @property
    def crowding(self):
        return self._crowding

    @crowding.setter
    def crowding(self, value):
        self._crowding = value


class CrowdingConfiguration(object):
    def __init__(self):
        self._factor = None
        self._size = None

    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, value):
        self._factor = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value


class GrammarCorrection(object):
    def __init__(self):
        self.should_run = False


class InvalidCykConfigurationError(Exception):
    def __init__(self, error):
        self.error = error

    def __str__(self):
        return repr(self.error)
