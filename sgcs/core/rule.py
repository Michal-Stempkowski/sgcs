from core.symbol import Symbol


class Rule(object):
    def __init__(self, parent, left_child, right_child=None):
        self._parent = parent
        self.left_child = left_child
        self.right_child = right_child

    @property
    def parent(self):
        return self._parent

    def is_terminal_rule(self):
        return self.right_child is None

    @staticmethod
    def _repr_or_special(symbol, shift, starting, universal):
        if symbol == starting:
            return '<S>'
        elif universal and symbol == universal:
            return '<U>'
        else:
            return symbol.human_friendly_representation(shift)

    def human_friendly_representation(self, shift, starting_symbol, universal_symbol):
        abs_shift = abs(shift)
        left_side = self._repr_or_special(self.parent, abs_shift, starting_symbol, universal_symbol)
        if self.is_terminal_rule():
            return left_side, self.left_child.symbol_id
        else:
            left_child = self._repr_or_special(
                self.left_child, abs_shift, starting_symbol, universal_symbol)
            right_child = self._repr_or_special(
                self.right_child, abs_shift, starting_symbol, universal_symbol)
            return left_side, left_child, right_child

    def __eq__(self, other):
        return self is other or other is not None and\
                                self.parent == other.parent and \
                                self.left_child == other.left_child and \
                                (self.right_child is None and other.right_child is None or
                                 self.right_child == other.right_child)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        res = self.parent.__hash__() << 6 ^ self.left_child.__hash__() << 3
        if self.right_child is not None:
            res = res ^ self.right_child.__hash__()

        return res

    def __str__(self):
        props = [str(self.parent), str(self.left_child), str(self.right_child)]
        return self.__class__.__name__ + '({' + '};{'.join(props) + "})"

    @staticmethod
    def _symbol_id_or_none(inpt):
        return inpt.symbol_id if inpt is not None else None

    @staticmethod
    def _symbol_or_none(inpt):
        return Symbol(inpt) if inpt is not None else None

    def json_coder(self):
        return [self._symbol_id_or_none(x) for x in
                [self._parent, self.left_child, self.right_child]]

    @staticmethod
    def json_decoder(json):
        return Rule(*[Rule._symbol_or_none(x) for x in json])


class TerminalRule(Rule):
    def __init__(self, parent, child):
        super().__init__(parent, child, None)
