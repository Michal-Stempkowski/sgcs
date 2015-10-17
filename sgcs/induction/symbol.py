class Symbol(object):
    def __init__(self, symbol_id):
        self.symbol_id = symbol_id

    def __eq__(self, other):
        return self.symbol_id == other.symbol_id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.symbol_id.__hash__()


class Sentence(object):
    def __init__(self, symbols):
        self.symbols = symbols

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
