def value_in_bounds(lower_eq, val, greater):
        return lower_eq <= val < greater


class CykTableIndexError(Exception):
    def __init__(self, coordinates):
        self.coordinates = coordinates

    def __str__(self):
        return repr(self.coordinates)


class Environment(object):
    def __init__(self, sentence):
        self.sentence = sentence
        self.cyk_table = [
            [
                set() for _ in range(len(self.sentence))
            ] for _ in range(len(self.sentence))
        ]

    def get_symbols(self, absolute_coordinates):
        self.validate_absolute_coordinates(absolute_coordinates)

        row, col = absolute_coordinates
        return self.cyk_table[row][col]

    def add_symbols(self, absolute_coordinates, symbols):
        self.validate_absolute_coordinates(absolute_coordinates)

        row, col = absolute_coordinates
        self.cyk_table[row][col].update(symbols)

    def get_left_parent_symbol_count(self, coordinates_with_shift):
        if len(coordinates_with_shift) != 3:
            raise CykTableIndexError(coordinates_with_shift)

        row, col, shift = coordinates_with_shift
        return len(self.get_symbols((shift, col)))

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
