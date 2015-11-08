from enum import Enum


class AddingRuleStrategyHint(Enum):
    expand_population = 0
    control_population_size = 1


class AddingRuleStrategy(object):
    def __init__(self):
        self.hints = []

    def is_applicable(self, strategy_hint):
        return strategy_hint in self.hints


class SimpleAddingRuleStrategy(AddingRuleStrategy):
    def __init__(self):
        super().__init__()
        self.hints.append(AddingRuleStrategyHint.expand_population)

    def apply(self, cyk_service, rule, rule_population):
        rule_population.add_rule(rule)


class AddingRuleWithCrowdingStrategy(AddingRuleStrategy):
    def __init__(self):
        super().__init__()
        self.hints.append(AddingRuleStrategyHint.control_population_size)

    @staticmethod
    def rule_affinity(left, right):
        return \
            (1 if left.parent == right.parent else 0) + \
            (1 if left.left_child == right.left_child else 0) + \
            (1 if left.right_child == right.right_child else 0)

    def apply(self, cyk_service, rule, rule_population):
        weak_rules = set()
        for _ in range(cyk_service.configuration.rule_adding.crowding.factor):
            subpopulation = rule_population.get_random_rules(
                cyk_service.randomizer, False, cyk_service.configuration.rule_adding.crowding.size)

            worst_rule = min(subpopulation, key=cyk_service.fitness.get_keyfunc(cyk_service))
            weak_rules.add(worst_rule)

        most_related_rule = max(weak_rules, key=lambda x: self.rule_affinity(rule, x))
        rule_population.add_rule(rule)
