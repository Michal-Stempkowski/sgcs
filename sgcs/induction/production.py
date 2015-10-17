class Production(object):
    def __init__(self, detector, rule):
        self.detector = detector
        self.rule = rule

    def is_empty(self):
        return self.rule is None

    def is_terminal(self):
        return self.detector is None

    def __eq__(self, other):
        return self.detector == other.detector and self.rule == other.rule

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return (hash(self.detector) << 3) ^ hash(self.rule)


class EmptyProduction(Production):
    def __init__(self, detector):
        super().__init__(detector, None)
        self.detector = detector


class TerminalProduction(Production):
    def __init__(self, rule):
        super().__init__(None, rule)


class ProductionPool(object):
    def __init__(self):
        self.non_empty_productions = []
        self.empty_productions = []
        self.effectors = set()

    def add_production(self, production):
        if production.is_empty():
            self.empty_productions.append(production)
        else:
            self.non_empty_productions.append(production)
            self.effectors.add(production.rule.parent)

    def is_empty(self):
        return not self.non_empty_productions

    def get_effectors(self):
        return self.effectors
