from abc import ABCMeta, abstractmethod
from enum import Enum


class AddingRuleStrategyHint(Enum):
    expand_population = 0
    control_population_size = 1


class AddingRuleStrategy(object, metaclass=ABCMeta):
    def __init__(self):
        self.hints = []

    @abstractmethod
    def apply(self, adding_supervisor, statistics, rule, rule_population):
        pass

    def is_applicable(self, strategy_hint):
        return strategy_hint in self.hints


class SimpleAddingRuleStrategy(AddingRuleStrategy):
    def __init__(self):
        super().__init__()
        self.hints.append(AddingRuleStrategyHint.expand_population)

    def apply(self, adding_supervisor, statistics, rule, rule_population):
        rule_population.add_rule(rule)
        statistics.on_added_new_rule(rule)


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
    def replace_rule(old, new, rule_population, statistics):
        rule_population.remove_rule(old)
        statistics.on_rule_removed(old)

        rule_population.add_rule(new)
        statistics.on_added_new_rule(new)

    def apply(self, adding_supervisor, statistics, rule, rule_population):
        weak_rules = set()
        for _ in range(adding_supervisor.configuration.crowding.factor):
            subpopulation = rule_population.get_random_rules(
                adding_supervisor.randomizer, False, adding_supervisor.configuration.crowding.size)

            adding_supervisor.randomizer.shuffle(subpopulation)

            worst_rule = min(subpopulation, key=statistics.fitness.get_keyfunc_getter(statistics))
            weak_rules.add(worst_rule)

        most_related_rule = max(weak_rules, key=lambda x: self.rule_affinity(rule, x))
        self.replace_rule(most_related_rule, rule, rule_population, statistics)


class AddingRuleSupervisor(object):
    def __init__(self, randomizer, configuration, strategies):
        self.strategies = strategies
        self.randomizer = randomizer
        self.configuration = configuration

    def add_rule(self, rule, rule_population, statistics,
                 strategy_hint=AddingRuleStrategyHint.expand_population):
        strategy_to_be_used = next(filter(
            lambda strategy: strategy.is_applicable(strategy_hint), self.strategies))

        strategy_to_be_used.apply(self, statistics, rule, rule_population)


class AddingRulesConfiguration(object):
    def __init__(self):
        self._crowding = None

    @property
    def crowding(self):
        return self._crowding

    @crowding.setter
    def crowding(self, value):
        self._crowding = value


class CrowdingConfiguration(object):
    def __init__(self):
        self._factor = None
        self._size = None

    @property
    def factor(self):
        return self._factor

    @factor.setter
    def factor(self, value):
        self._factor = value

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        self._size = value
