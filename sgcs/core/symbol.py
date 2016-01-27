from datalayer.jsonizer import SimpleJsonNode
from utils import RunTimes


class Symbol(SimpleJsonNode):
    ALPHABET_SIZE = ord('z') - ord('a')

    def __init__(self, symbol_id=None):
        self.symbol_id = symbol_id

    def human_friendly_representation(self, abs_shift):
        remainder = self.symbol_id - abs_shift + 1
        result = []

        run_one_more_time = RunTimes(1)
        while remainder > self.ALPHABET_SIZE or run_one_more_time():
            letter = chr(remainder % self.ALPHABET_SIZE + ord('a'))
            result.append(letter.upper())
            remainder //= self.ALPHABET_SIZE

        return ''.join(reversed(result))

    @staticmethod
    def from_human_friendly_representation(human_repr, abs_shift):
        acc = 0
        for letter in human_repr:
            acc = acc * Symbol.ALPHABET_SIZE + (ord(letter.lower()) - ord('a'))

        return Symbol(acc + abs_shift - 1)

    def __eq__(self, other):
        return self.symbol_id == other.symbol_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.symbol_id.__hash__()

    def __repr__(self):
        return self.__class__.__name__ + '({' + str(self.symbol_id) + "})"


class Sentence(object):
    def __init__(self, symbols, is_positive_sentence=None):
        self.symbols = symbols
        self.is_positive_sentence = is_positive_sentence

    def __len__(self):
        return len(self.symbols)

    def get_symbol(self, index):
        return self.symbols[index]

    def __eq__(self, other):
        return len(self.symbols) == len(other.symbols) and \
            all(self.symbols[i] == other.symbols[i] for i in range(len(self.symbols)))

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.symbols.__hash__()

    def __str__(self):
        return self.__class__.__name__ + '({' + \
               ', '.join(str(x.symbol_id) for x in self.symbols) + "})"
