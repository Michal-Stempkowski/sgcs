class RulePopulationAccessViolationError(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return ' '.join(self.args)


class RulePopulation(object):
    def __init__(self, previous_instance=None):
        self.rules_by_right = dict()

    def get_rules_by_right(self, pair):
        if len(pair) != 2:
            raise RulePopulationAccessViolationError(
                'Invalid pair arity in get_rules_by_right', pair)

        packed_rules = self.rules_by_right.get(pair)
        return packed_rules.values() if packed_rules else []

    def add_rule(self, rule):
        by_right_key = (rule.left_child, rule.right_child)
        if by_right_key not in self.rules_by_right:
            self.rules_by_right[by_right_key] = dict()

        # if there is allready such an rule, then make mess
        self.rules_by_right[by_right_key][rule.parent] = rule
