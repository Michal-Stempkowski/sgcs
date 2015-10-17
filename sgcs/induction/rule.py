class Rule(object):
    def __init__(self, parent, left_child, right_child):
        self._parent = parent
        self.left_child = left_child
        self.right_child = right_child

    @property
    def parent(self):
        return self._parent

    def is_terminal_rule(self):
        return self.right_child is None

    def __eq__(self, other):
        return self.parent == other.parent and \
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


class TerminalRule(Rule):
    def __init__(self, parent, child):
        super().__init__(parent, child, None)
