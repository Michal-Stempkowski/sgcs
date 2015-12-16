from core.symbol import Symbol


class RulePopulationAccessViolationError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ' '.join(self.args)


class RulePopulation(object):
    def __init__(self, starting_symbol, universal_symbol=None, previous_instance=None,
                 max_non_terminal_symbols=32):
        self._all_non_terminal_rules = set()
        self._all_terminal_rules = set()
        self._rules_by_right = dict()
        self._terminal_rules = dict()
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

    @staticmethod
    def symbol_shift():
        return 101

    @property
    def terminal_rule_count(self):
        return len(self._all_terminal_rules)

    @property
    def non_terminal_rule_count(self):
        return len(self._all_non_terminal_rules)

    def get_rules_by_right(self, pair):
        if len(pair) != 2:
            raise RulePopulationAccessViolationError(
                'Invalid pair arity in get_rules_by_right', pair)

        packed_rules = self._rules_by_right.get(pair)
        return packed_rules.values() if packed_rules else []

    def get_all_non_terminal_rules(self):
        return self._all_non_terminal_rules

    def add_rule(self, rule, randomizer):
        if rule.is_terminal_rule():
            self._add_terminal_rule(rule, randomizer)
            self._all_terminal_rules.add(rule)
        else:
            self._add_non_terminal_rule(rule, randomizer)
            self._all_non_terminal_rules.add(rule)

    def _add_non_terminal_rule(self, rule, randomizer):
        by_right_key = (rule.left_child, rule.right_child)
        if by_right_key not in self._rules_by_right:
            self._rules_by_right[by_right_key] = dict()

        # if there is already such an rule, then make mess
        self._rules_by_right[by_right_key][rule.parent] = rule

    def _add_terminal_rule(self, rule, randomizer):
        if rule.left_child not in self._terminal_rules:
            self._terminal_rules[rule.left_child] = dict()

        # if there is already such an rule, then make mess
        self._terminal_rules[rule.left_child][rule.parent] = rule

    def get_terminal_rules(self, symbol=None):
        if symbol is None:
            return (x for y in self._terminal_rules.values() for x in y.values())
        else:
            packed_rules = self._terminal_rules.get(symbol)
            return packed_rules.values() if packed_rules else []

    def get_random_non_terminal_symbol(self, randomizer):
        return Symbol(randomizer.randint(self.symbol_shift(),
                                         self.symbol_shift() + self.max_non_terminal_symbols))

    def get_random_rules(self, randomizer, terminal, size):
        real_size = min(size, len(self._all_non_terminal_rules))
        return randomizer.sample(self._all_non_terminal_rules, real_size)

    def remove_rule(self, rule):
        terminal = rule.is_terminal_rule()
        if not terminal:
            right_key = rule.left_child, rule.right_child
            self._all_non_terminal_rules.remove(rule)
        else:
            right_key = rule.left_child
            self._all_terminal_rules.remove(rule)
        del self._rules_by_right[right_key][rule.parent]
        if not self._rules_by_right[right_key]:
            del self._rules_by_right[right_key]

    def get_random_rules_matching_filter(self, randomizer, terminal, size, filter):
        filtered_rules = [x for x in self.get_all_non_terminal_rules() if filter(x)]
        real_size = min(size, len(filtered_rules))
        return randomizer.sample(filtered_rules, real_size)

    def has_rule(self, rule):
        return rule in (self._terminal_rules if rule.is_terminal_rule()
                        else self._all_non_terminal_rules)


class StochasticRulePopulation(RulePopulation):
    def __init__(self, starting_symbol, universal_symbol=None, previous_instance=None,
                 max_non_terminal_symbols=32):
        super().__init__(starting_symbol, universal_symbol, previous_instance,
                         max_non_terminal_symbols)
        self.rule_probabilities = dict()
        self.left_side_probabilities = dict()

    def add_rule(self, rule, randomizer):
        super().add_rule(rule, randomizer)
        new_rule_probability = randomizer.uniform(0.01, 1)
        self._add_new_rule_probability(rule, new_rule_probability)

    def _add_new_rule_probability(self, rule, new_rule_probability):
        self.rule_probabilities[rule] = new_rule_probability

        if rule.parent not in self.left_side_probabilities:
            self.left_side_probabilities[rule.parent] = new_rule_probability
        else:
            self.left_side_probabilities[rule.parent] += new_rule_probability

    def remove_rule(self, rule):
        super().remove_rule(rule)
        probability_of_removed = self.rule_probabilities[rule]
        del self.rule_probabilities[rule]
        self.left_side_probabilities[rule.parent] -= probability_of_removed

    def get_normalized_rule_probability(self, rule):
        left_side_probability = self.left_side_probabilities.get(rule.parent, 1)
        return self.rule_probabilities.get(rule, 0) / \
            left_side_probability if left_side_probability > 0 else 1

    def perform_probability_estimation(self, fitness_getter):
        for parent in self.left_side_probabilities:
            self.left_side_probabilities[parent] = 0

        for rule in self.get_all_non_terminal_rules():
            fitness = fitness_getter(rule)
            self._add_new_rule_probability(rule, fitness)
        for rule in self.get_terminal_rules():
            fitness = fitness_getter(rule)
            self._add_new_rule_probability(rule, fitness)

        for rule in self.rule_probabilities:
            self.rule_probabilities[rule] = self.get_normalized_rule_probability(rule)
        for parent in self.left_side_probabilities:
            self.left_side_probabilities[parent] = 1
