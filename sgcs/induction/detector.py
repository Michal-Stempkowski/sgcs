from sgcs.induction.production import EmptyProduction, Production


class Detector(object):
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def generate_production(self, environment, rule_population):
        symbols = environment.get_detector_symbols(self.coordinates)
        rules = rule_population.get_rules_by_right(symbols)

        return [EmptyProduction(self)] \
            if len(rules) == 0 \
            else [Production(self, rule) for rule in rules]

    def __str__(self):
        return self.__class__.__name__ + '({' + '};{'.join(self.coordinates) + "})"
