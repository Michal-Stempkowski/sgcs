class Rule(object):
    def __init__(self, parent, left_child, right_child):
        self._parent = parent
        self.left_child = left_child
        self.right_child = right_child

    @property
    def parent(self):
        return self._parent


class TerminalRule(Rule):
    def __init__(self, parent, child):
        super().__init__(parent, child, None)
