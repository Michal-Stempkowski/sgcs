from sgcs.induction.symbol import Symbol


class RulePopulationAccessViolationError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ' '.join(self.args)


class RulePopulation(object):
    def __init__(self, starting_symbol, universal_symbol=None, previous_instance=None):
        self.all_non_terminal_rules = set()
        self.rules_by_right = dict()
        self.terminal_rules = dict()
        self._starting_symbol = starting_symbol
        self._universal_symbol = universal_symbol

    @property
    def starting_symbol(self):
        return self._starting_symbol

    @property
    def universal_symbol(self):
        return self._universal_symbol

    @property
    def max_non_terminal_symbols(self):
        return 32

    def get_rules_by_right(self, pair):
        if len(pair) != 2:
            raise RulePopulationAccessViolationError(
                'Invalid pair arity in get_rules_by_right', pair)

        packed_rules = self.rules_by_right.get(pair)
        return packed_rules.values() if packed_rules else []

    def add_rule(self, rule):
        if rule.is_terminal_rule():
            self._add_terminal_rule(rule)
        else:
            self._add_non_terminal_rule(rule)
            self.all_non_terminal_rules.add(rule)

    def _add_non_terminal_rule(self, rule):
        by_right_key = (rule.left_child, rule.right_child)
        if by_right_key not in self.rules_by_right:
            self.rules_by_right[by_right_key] = dict()

        # if there is already such an rule, then make mess
        self.rules_by_right[by_right_key][rule.parent] = rule

    def _add_terminal_rule(self, rule):
        if rule.left_child not in self.terminal_rules:
            self.terminal_rules[rule.left_child] = dict()

        # if there is already such an rule, then make mess
        self.terminal_rules[rule.left_child][rule.parent] = rule

    def get_terminal_rules(self, symbol):
        packed_rules = self.terminal_rules.get(symbol)
        return packed_rules.values() if packed_rules else []

    def get_random_non_terminal_symbol(self, randomizer):
        return Symbol(randomizer.randint(1, self.max_non_terminal_symbols))

    def get_random_rules(self, randomizer, terminal, size):
        return randomizer.sample(self.all_non_terminal_rules, size)

    def remove_rule(self, rule):
        right_key = rule.left_child, rule.right_child \
            if not rule.is_terminal_rule() \
            else rule.left_child
        del self.rules_by_right[right_key][rule.parent]
