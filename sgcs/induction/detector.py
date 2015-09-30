class Detector(object):
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def generate_production(self, environment):
        environment.get_symbols(self.coordinates)