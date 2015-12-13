class Production(object):
    def __init__(self, detector, rule):
        self.detector = detector
        self.rule = rule
        self.probability = None

    def is_empty(self):
        return self.rule is None

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
        self.all_productions = []
        self.effectors = list()
        self.effector_probabilities = dict()

    def add_production(self, production, child_productions, probability_approach):
        self.all_productions.append(production)
        if production.is_empty():
            self.empty_productions.append(production)
        else:
            self.non_empty_productions.append(production)
            effector = production.rule.parent
            if effector not in self.effectors:
                self.effectors.append(effector)
                self.effector_probabilities[effector] = 0

            if probability_approach is not None:
                self.effector_probabilities[effector] = probability_approach(
                    self.effector_probabilities[effector],
                    production,
                    child_productions)

    def is_empty(self):
        return not self.non_empty_productions

    def get_effectors(self):
        return self.effectors

    def get_unsatisfied_detectors(self):
        return list(map(lambda prod: prod.detector, self.empty_productions))

    def get_non_empty_productions(self):
        return self.non_empty_productions

    def __str__(self):
        return "PP[" + "; ".join(map(lambda x: repr(x), self.get_effectors())) + "]"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.all_productions[item]

    def find_non_empty_productions(self, predicate):
        return filter(predicate, self.non_empty_productions)
