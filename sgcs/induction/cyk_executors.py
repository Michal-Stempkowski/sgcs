from sgcs.induction.detector import Detector


class CykParentCombinationExecutor(object):
    def __init__(self):
        pass

    @property
    def current_row(self):
        return None

    @property
    def current_col(self):
        return None

    @property
    def shift(self):
        return None


class CykSymbolPairExecutor(object):
    def __init__(self, parent_executor, left_id, right_id):
        self.parent_executor = parent_executor
        self.left_id = left_id
        self.right_id = right_id

    def execute(self, environment, rule_population, production_pool):
        coordinates = self.get_coordinates()

        detector = Detector(coordinates)

        for production in detector.generate_production(environment, rule_population):
            production_pool.add_production(production)

    def get_coordinates(self):
        return (self.parent_executor.current_row,
                self.parent_executor.current_col,
                self.parent_executor.shift,
                self.left_id,
                self.right_id)

    def __str__(self):
        return self.__class__.__name__ + '({' + '};{'.join(self.get_coordinates()) + "})"
