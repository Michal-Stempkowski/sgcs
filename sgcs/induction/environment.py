class Environment(object):
    def get_symbols(self, coordinates):
        pass

    def get_left_parent_symbol_count(self, coordinates):
        pass

    def get_right_parent_symbol_count(self, coordinates):
        pass


class CykTableIndexError(Exception):
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def __str__(self):
        return repr(self.coordinates)