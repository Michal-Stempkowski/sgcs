from abc import ABCMeta, abstractmethod
from enum import Enum


class AddingRuleStrategyHint(Enum):
    expand_population = 0
    control_population_size = 1


class AddingRuleStrategy(object, metaclass=ABCMeta):
    def __init__(self):
        self.hints = []

    @abstractmethod
    def apply(self, cyk_service, rule, rule_population):
        pass

    def is_applicable(self, strategy_hint):
        return strategy_hint in self.hints


class SimpleAddingRuleStrategy(AddingRuleStrategy):
    def __init__(self):
        super().__init__()
        self.hints.append(AddingRuleStrategyHint.expand_population)

    def apply(self, cyk_service, rule, rule_population):
        rule_population.add_rule(rule)
        cyk_service.statistics.on_added_new_rule(rule)


class AddingRuleWithCrowdingStrategy(AddingRuleStrategy):
    def __init__(self):
        super().__init__()
        self.hints.append(AddingRuleStrategyHint.control_population_size)

    @staticmethod
    def rule_affinity(left, right):
        if left.is_terminal_rule() and right.is_terminal_rule() or \
                not (left.is_terminal_rule() or right.is_terminal_rule()):
            return \
                (1 if left and right and left.parent == right.parent else 0) + \
                (1 if left and right and left.left_child == right.left_child else 0) + \
                (1 if left and right and left.right_child == right.right_child else 0)
        else:
            return -1

    @staticmethod
    def replace_rule(old, new, rule_population, cyk_service):
        rule_population.remove_rule(old)
        cyk_service.statistics.on_rule_removed(old)

        rule_population.add_rule(new)
        cyk_service.statistics.on_added_new_rule(new)

    def apply(self, cyk_service, rule, rule_population):
        weak_rules = set()
        for _ in range(cyk_service.configuration.rule_adding.crowding.factor):
            subpopulation = rule_population.get_random_rules(
                cyk_service.randomizer, False, cyk_service.configuration.rule_adding.crowding.size)

            cyk_service.randomizer.shuffle(subpopulation)

            worst_rule = min(subpopulation, key=cyk_service.fitness.get_keyfunc(cyk_service))
            weak_rules.add(worst_rule)

        most_related_rule = max(weak_rules, key=lambda x: self.rule_affinity(rule, x))
        self.replace_rule(most_related_rule, rule, rule_population, cyk_service)


class AddingRuleSupervisor(object):
    def __init__(self):
        self.strategies = []

    def add_rule(self, rule, rule_population, cyk_service,
                 strategy_hint=AddingRuleStrategyHint.expand_population):
        strategy_to_be_used = next(filter(
            lambda strategy: strategy.is_applicable(strategy_hint), self.strategies))

        strategy_to_be_used.apply(cyk_service, rule, rule_population)
