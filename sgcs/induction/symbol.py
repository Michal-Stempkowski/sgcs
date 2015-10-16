class Symbol(object):
    def __init__(self, symbol_id):
        self.symbol_id = symbol_id


class Sentence(object):
    def __init__(self, symbols):
        self.symbols = symbols

    def __len__(self):
        return len(self.symbols)
