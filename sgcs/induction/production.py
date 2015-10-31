class Production(object):
    def __init__(self, detector, rule):
        self.detector = detector
        self.rule = rule

    def is_empty(self):
        return self.rule is None

    def is_terminal(self):
        return self.detector is None

    def get_coordinates(self):
        return self.detector.coordinates

    def __eq__(self, other):
        return other is not None and \
               self.detector == other.detector and \
               self.rule == other.rule

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return (hash(self.detector) << 3) ^ hash(self.rule)

    def __str__(self):
        props = [str(self.get_coordinates()), str(self.rule)]
        return self.__class__.__name__ + '({' + '};{'.join(props) + "})"

    def __repr__(self):
        return self.__str__()


class EmptyProduction(Production):
    def __init__(self, detector):
        super().__init__(detector, None)
        self.detector = detector


class ProductionPool(object):
    def __init__(self):
        self.non_empty_productions = []
        self.empty_productions = []
        self.effectors = list()

    def add_production(self, production):
        if production.is_empty():
            self.empty_productions.append(production)
        else:
            self.non_empty_productions.append(production)
            effector = production.rule.parent
            if effector not in self.effectors:
                self.effectors.append(effector)

    def is_empty(self):
        return not self.non_empty_productions

    def get_effectors(self):
        return self.effectors

    def __str__(self):
        return "PP[" + "; ".join(map(lambda x: repr(x), self.get_effectors())) + "]"

    def __repr__(self):
        return self.__str__()
