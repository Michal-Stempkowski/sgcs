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

    def apply(self, rule, rule_population):
        rule_population.add_rule(rule)


class AddingRuleWithCrowdingStrategy(AddingRuleStrategy):
    def __init__(self):
        super().__init__()
        self.hints.append(AddingRuleStrategyHint.control_population_size)

    def apply(self, rule, rule_population):
        rule_population.add_rule(rule)
