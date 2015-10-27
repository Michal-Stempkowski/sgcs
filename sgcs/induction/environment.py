from sgcs.induction.cyk_executors import CykTypeId


def value_in_bounds(lower_eq, val, greater):
        return lower_eq <= val < greater


class CykTableIndexError(Exception):
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def __str__(self):
        return repr(self.coordinates)


class Environment(object):
    def __init__(self, sentence, factory):
        self.sentence = sentence
        size = self.get_sentence_length()
        self.cyk_table = {
            (x, y): factory.create(CykTypeId.production_pool)
            for x in range(size) for y in range(size)
        }

    def get_symbols(self, absolute_coordinates):
        self.validate_absolute_coordinates(absolute_coordinates)

        cords = absolute_coordinates
        return self.cyk_table[cords].get_effectors()

    def add_production(self, production):
        absolute_coordinates = production.get_coordinates()[:2]
        self.validate_absolute_coordinates(absolute_coordinates)

        self.cyk_table[absolute_coordinates].add_production(production)

    def _left_coord(self, row, col, shift, left_id, right_id):
        return self.get_symbols((shift - 1, col))[left_id]

    def _right_coord(self, row, col, shift, left_id, right_id):
        return self.get_symbols((row - shift, col + shift))[right_id]

    def get_left_parent_symbol_count(self, coordinates_with_shift):
        if len(coordinates_with_shift) != 3:
            raise CykTableIndexError(coordinates_with_shift)

        row, col, shift = coordinates_with_shift
        return len(self.get_symbols((shift - 1, col)))

    def get_right_parent_symbol_count(self, coordinates_with_shift):
        if len(coordinates_with_shift) != 3:
            raise CykTableIndexError(coordinates_with_shift)

        row, col, shift = coordinates_with_shift
        return len(self.get_symbols((row - shift, col + shift)))

    def get_row_length(self, row):
        return self.get_sentence_length() - row

    def get_sentence_length(self):
        return len(self.sentence)

    def validate_absolute_coordinates(self, coordinates):
        if len(coordinates) != 2 \
            or not value_in_bounds(0, coordinates[0], self.get_sentence_length()) \
                or not value_in_bounds(0, coordinates[1], self.get_sentence_length()):
            raise CykTableIndexError(coordinates)

    def get_sentence_symbol(self, index):
        return self.sentence.get_symbol(index)

    def __str__(self):
        return self.__class__.__name__ + '({' + str(self.cyk_table) + "})"

    def get_detector_symbols(self, coord):
        left = self._left_coord(*coord)
        right = self._right_coord(*coord)

        return left, right
