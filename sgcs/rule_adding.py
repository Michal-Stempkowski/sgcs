from abc import ABCMeta, abstractmethod
from enum import Enum


class AddingRuleStrategyHint(object):
    expand_population = 0
    control_population_size = 1
    control_population_size_with_elitism = 2


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

    @staticmethod
    def _get_worst_rule(adding_supervisor, statistics, subpopulation):
        adding_supervisor.randomizer.shuffle(subpopulation)
        return min(subpopulation, key=statistics.fitness.get_keyfunc_getter(statistics))

    def _replace_most_related_rule(self, statistics, rule_population, weak_rules, rule):
        most_related_rule = max(weak_rules, key=lambda x: self.rule_affinity(rule, x))
        self.replace_rule(most_related_rule, rule, rule_population, statistics)

    def apply(self, adding_supervisor, statistics, rule, rule_population):
        if rule_population.has_rule(rule):
            return
        weak_rules = set()
        for _ in range(adding_supervisor.configuration.crowding.factor):
            subpopulation = rule_population.get_random_rules(
                adding_supervisor.randomizer, False, adding_supervisor.configuration.crowding.size)

            weak_rules.add(self._get_worst_rule(adding_supervisor, statistics, subpopulation))

        self._replace_most_related_rule(statistics, rule_population, weak_rules, rule)


# noinspection PyAbstractClass
class AddingRuleWithElitismStrategy(AddingRuleWithCrowdingStrategy):
    def __init__(self):
        super().__init__()
        self.hints = [AddingRuleStrategyHint.control_population_size_with_elitism]
        self.elite = []

    def generate_elite(self, adding_supervisor, statistics, rule_population):
        rules = rule_population.get_all_non_terminal_rules()
        rules_by_fitness = sorted(rules,
                                  key=statistics.fitness.get_keyfunc_getter(statistics),
                                  reverse=True)

        self.elite = rules_by_fitness[:adding_supervisor.configuration.elitism.size]

    def apply(self, adding_supervisor, statistics, rule, rule_population):
        if rule_population.has_rule(rule):
            return

        weak_rules = set()

        for _ in range(adding_supervisor.configuration.crowding.factor):
            subpopulation = rule_population.get_random_rules_matching_filter(
                adding_supervisor.randomizer, False, adding_supervisor.configuration.crowding.size,
                lambda x: x not in self.elite)

            weak_rules.add(self._get_worst_rule(adding_supervisor, statistics, subpopulation))

        self._replace_most_related_rule(statistics, rule_population, weak_rules, rule)


class AddingRuleSupervisor(object):
    @staticmethod
    def default(randomizer):
        return AddingRuleSupervisor(randomizer,
                                    AddingRulesConfiguration.create(
                                        crowding_factor=0,
                                        crowding_size=0,
                                        elitism_size=0),
                                    AddingRuleSupervisor.get_default_strategies())

    @staticmethod
    def get_default_strategies():
        return [
            SimpleAddingRuleStrategy(),
            AddingRuleWithCrowdingStrategy(),
            AddingRuleWithElitismStrategy()
        ]

    def __init__(self, randomizer, configuration, strategies):
        self.strategies = strategies
        self.randomizer = randomizer
        self.configuration = configuration

    def add_rule(self, rule, rule_population, statistics,
                 strategy_hint=AddingRuleStrategyHint.expand_population):
        strategy_to_be_used = next(filter(
            lambda strategy: strategy.is_applicable(strategy_hint), self.strategies))

        strategy_to_be_used.apply(self, statistics, rule, rule_population)

    def update_elite_if_supported(self, rule_population, statistics):
        for strategy in filter(
            lambda s: s.is_applicable(
                AddingRuleStrategyHint.control_population_size_with_elitism), self.strategies):
            strategy.generate_elite(self, statistics, rule_population)


class AddingRulesConfiguration(object):
    @staticmethod
    def create(crowding_factor, crowding_size, elitism_size):
        configuration = AddingRulesConfiguration()
        configuration.crowding = CrowdingConfiguration.create(crowding_factor, crowding_size)
        configuration.elitism = ElitismConfiguration.create(elitism_size)
        return configuration

    def __init__(self):
        self._crowding = None
        self.elitism = None

    @property
    def crowding(self):
        return self._crowding

    @crowding.setter
    def crowding(self, value):
        self._crowding = value


class CrowdingConfiguration(object):
    @staticmethod
    def create(crowding_factor, crowding_size):
        configuration = CrowdingConfiguration()
        configuration.factor = crowding_factor
        configuration.size = crowding_size
        return configuration

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


class ElitismConfiguration(object):
    @staticmethod
    def create(elitism_size):
        configuration = ElitismConfiguration()
        configuration.size = elitism_size
        configuration.is_used = True if elitism_size > 0 else False
        return configuration

    def __init__(self):
        self.is_used = False
        self.size = None
