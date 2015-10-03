class Production(object):
    def __init__(self, detector, rule):
        self.detector = detector
        self.rule = rule

    def is_empty(self):
        return self.rule is None


class EmptyProduction(Production):
    def __init__(self, detector):
        super().__init__(detector, None)
        self.detector = detector


class ProductionPool(object):
    def __init__(self):
        self.pool = []
        self.proposals = []

    def add_production(self, production):
        self.pool.append(production)
