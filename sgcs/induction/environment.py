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
        self.size = self.get_sentence_length()
        self.cyk_table = {
            (x, y): factory.create(CykTypeId.production_pool)
            for x in range(self.size) for y in range(self.size)
        }

    def get_symbols(self, absolute_coordinates):
        return self._get_production_pool(absolute_coordinates).get_effectors()

    def _get_production_pool(self, absolute_coordinates):
        self.validate_absolute_coordinates(absolute_coordinates)

        return self.cyk_table[absolute_coordinates]

    def add_production(self, production):
        absolute_coordinates = production.get_coordinates()[:2]
        self.validate_absolute_coordinates(absolute_coordinates)

        self.cyk_table[absolute_coordinates].add_production(production)

    @staticmethod
    def _left_coord(row, col, shift, left_id, right_id):
        return shift - 1, col

    @staticmethod
    def _right_coord(row, col, shift, left_id, right_id):
        return row - shift, col + shift

    def _terminal_parent_symbols(self, col):
        return self.sentence.get_symbol(col)

    def _left_parent_symbols(self, row, col, shift, left_id, right_id):
        return self.get_symbols(self._left_coord(row, col, shift, left_id, right_id))[left_id]

    def _right_parent_symbols(self, row, col, shift, left_id, right_id):
        return self.get_symbols(self._right_coord(row, col, shift, left_id, right_id))[right_id]

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

    def is_sentence_positive(self):
        return self.sentence.is_positive_sentence

    def validate_absolute_coordinates(self, coordinates):
        if len(coordinates) != 2 \
            or not value_in_bounds(0, coordinates[0], self.get_sentence_length()) \
                or not value_in_bounds(0, coordinates[1], self.get_sentence_length()):
            raise CykTableIndexError(coordinates)

    def get_sentence_symbol(self, index):
        return self.sentence.get_symbol(index)

    def get_last_cell_productions(self):
        return self.cyk_table[self.size - 1, 0].get_non_empty_productions()

    def __str__(self):
        return self.__class__.__name__ + '({' + str(self.cyk_table) + "})"

    def get_detector_symbols(self, coord):
        row = coord[0]
        if row > 0:
            left = self._left_parent_symbols(*coord)
            right = self._right_parent_symbols(*coord)

            return left, right
        else:
            col = coord[1]
            return self._terminal_parent_symbols(col),

    def get_unsatisfied_detectors(self, coordinates):
        production_pool = self.cyk_table[coordinates]
        return production_pool.get_unsatisfied_detectors()

    def has_no_productions(self, coordinates):
        production_pool = self.cyk_table[coordinates]
        return production_pool.is_empty()

    def get_child_productions(self, production):
        result = []
        if not production.rule.is_terminal_rule():
            parent_detector = production.detector
            left_child_symbol = production.rule.left_child
            right_child_symbol = production.rule.right_child

            for production in self._child_production_generator(
                    self._left_coord(*parent_detector.coordinates), left_child_symbol):
                result.append(production)

            for production in self._child_production_generator(
                    self._right_coord(*parent_detector.coordinates), right_child_symbol):
                result.append(production)

        return result

    def _child_production_generator(self, coordinates, symbol):
        production_pool = self._get_production_pool(coordinates)

        return (p for p in production_pool.find_non_empty_productions(
            lambda x: x.rule.parent == symbol))
