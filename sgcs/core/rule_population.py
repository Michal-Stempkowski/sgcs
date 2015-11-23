from core.symbol import Symbol


class RulePopulationAccessViolationError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ' '.join(self.args)


class RulePopulation(object):
    def __init__(self, starting_symbol, universal_symbol=None, previous_instance=None,
                 max_non_terminal_symbols=32):
        self.all_non_terminal_rules = set()
        self.rules_by_right = dict()
        self.terminal_rules = dict()
        self._starting_symbol = starting_symbol
        self._universal_symbol = universal_symbol
        self._max_non_terminal_symbols = max_non_terminal_symbols

    @property
    def starting_symbol(self):
        return self._starting_symbol

    @property
    def universal_symbol(self):
        return self._universal_symbol

    @property
    def max_non_terminal_symbols(self):
        return self._max_non_terminal_symbols

    def get_rules_by_right(self, pair):
        if len(pair) != 2:
            raise RulePopulationAccessViolationError(
                'Invalid pair arity in get_rules_by_right', pair)

        packed_rules = self.rules_by_right.get(pair)
        return packed_rules.values() if packed_rules else []

    def get_all_non_terminal_rules(self):
        return (x for y in self.rules_by_right.values() for x in y.values())

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

    def get_terminal_rules(self, symbol=None):
        if symbol is None:
            return (x for y in self.terminal_rules.values() for x in y.values())
        else:
            packed_rules = self.terminal_rules.get(symbol)
            return packed_rules.values() if packed_rules else []

    def get_random_non_terminal_symbol(self, randomizer):
        return Symbol(randomizer.randint(101, 101 + self.max_non_terminal_symbols))

    def get_random_rules(self, randomizer, terminal, size):
        real_size = min(size, len(self.all_non_terminal_rules))
        return randomizer.sample(self.all_non_terminal_rules, real_size)

    def remove_rule(self, rule):
        terminal = rule.is_terminal_rule()
        if not terminal:
            right_key = rule.left_child, rule.right_child
            self.all_non_terminal_rules.remove(rule)
        else:
            right_key = rule.left_child
        del self.rules_by_right[right_key][rule.parent]
        if not self.rules_by_right[right_key]:
            del self.rules_by_right[right_key]

    def get_random_rules_matching_filter(self, randomizer, terminal, size, filter):
        filtered_rules = [x for x in self.get_all_non_terminal_rules() if filter(x)]
        real_size = min(size, len(filtered_rules))
        return randomizer.sample(filtered_rules, real_size)

    def has_rule(self, rule):
        return rule in (self.terminal_rules if rule.is_terminal_rule()
                        else self.all_non_terminal_rules)
