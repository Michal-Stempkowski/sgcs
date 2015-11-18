from abc import ABCMeta, abstractmethod, abstractstaticmethod
from enum import Enum


class RuleInfo(object):
    def __init__(self):
        self.fitness = None


class RuleStatistics(metaclass=ABCMeta):
    def __init__(self):
        self._rule_info = dict()

    def has_rule(self, rule):
        return rule in self._rule_info

    def update_fitness(self, grammar_statistics):
        for rule, rule_info in self._rule_info.items():
            rule_info.fitness = grammar_statistics.fitness.calculate(grammar_statistics, rule)

    @abstractmethod
    def get_rule_statistics(self, rule, grammar_statistics):
        pass

    @abstractmethod
    def added_new_rule(self, rule, grammar_statistics):
        pass

    @abstractmethod
    def rule_used(self, rule, usage_info, grammar_statistics):
        pass

    @abstractmethod
    def removed_rule(self, rule, grammar_statistics):
        pass

    @abstractstaticmethod
    def create_usage(grammar_statistics, cyk_result, sentence):
        pass


class PasiekaRuleInfo(RuleInfo):
    def __init__(self):
        super().__init__()
        self.rule_usage = 0


class PasiekaLeftSideInfo(object):
    def __init__(self):
        self.left_side_usage = 0


class PasiekaRuleStatistics(RuleStatistics):
    def __init__(self):
        super().__init__()
        self._left_side_info = dict()

    def get_rule_statistics(self, rule, grammar_statistics):
        return (self._rule_info[rule], self._left_side_info.get(rule.parent)) \
            if rule in self._rule_info else None

    def added_new_rule(self, rule, grammar_statistics):
        info = self._left_side_info.get(rule.parent, PasiekaLeftSideInfo())
        self._left_side_info[rule.parent] = info

        self._rule_info[rule] = PasiekaRuleInfo()

    def rule_used(self, rule, usage_info, grammar_statistics):
        self._left_side_info[rule.parent].left_side_usage += 1
        self._rule_info[rule].rule_usage += 1

    def removed_rule(self, rule, grammar_statistics):
        removed_usage = self._rule_info[rule].rule_usage
        self._left_side_info[rule.parent].left_side_usage -= removed_usage
        del self._rule_info[rule]

    @staticmethod
    def create_usage(grammar_statistics, cyk_result, sentence):
        return None


class Fitness(metaclass=ABCMeta):
    @abstractmethod
    def calculate(self, grammar_statistics, rule):
        pass

    def get(self, grammar_statistics, rule):
        rule_info, *_ = grammar_statistics.get_rule_statistics(rule)
        if rule_info.fitness is None:
            rule_info.fitness = self.calculate(grammar_statistics, rule)
        return rule_info.fitness

    def get_keyfunc_getter(self, grammar_statistics):
        return lambda rule: self.get(grammar_statistics, rule)


class PasiekaFitness(Fitness):
    def calculate(self, grammar_statistics, rule):
        rule_info, _ = grammar_statistics.get_rule_statistics(rule)
        return rule_info.rule_usage


class ClassicRuleInfo(RuleInfo):
    def __init__(self):
        super().__init__()
        self.valid_sentence_usage = 0
        self.invalid_sentence_usage = 0
        self.points_gained_for_valid_sentences = 0
        self.points_gained_for_invalid_sentences = 0

    def points_total(self):
        return self.points_gained_for_valid_sentences - self.points_gained_for_invalid_sentences

    def apply_usage(self, usage_info):
        if usage_info.positive_sentence:
            self.valid_sentence_usage += usage_info.usage_count
            self.points_gained_for_valid_sentences += usage_info.points_gained
        else:
            self.invalid_sentence_usage += usage_info.usage_count
            self.points_gained_for_invalid_sentences += usage_info.points_gained


class ClassicRuleUsageInfo(object):
    def __init__(self, positive_sentence, usage_count, points_gained=1):
        self.positive_sentence = positive_sentence
        self.usage_count = usage_count
        self.points_gained = points_gained


class ClassicRuleStatistics(RuleStatistics):
    def __init__(self):
        super().__init__()
        self._worst_rule = None
        self.min_fertility = None

        self._best_rule = None
        self.max_fertility = None

    def get_rule_statistics(self, rule, grammar_statistics):
        return self._rule_info.get(rule), self.min_fertility, self.max_fertility

    def update_fertility(self, rule, fertility):
        if not self.min_fertility or fertility < self.min_fertility:
            self._worst_rule = rule
            self.min_fertility = fertility
        if not self.max_fertility or fertility > self.max_fertility:
            self._best_rule = rule
            self.max_fertility = fertility

    def search_for_fertility(self):
        values = list(map(lambda x: x.points_total(),
                          (rule_info for rule_info in self._rule_info.values())))

        self.min_fertility = min(values, default=None)
        self.max_fertility = max(values, default=None)

    def added_new_rule(self, rule, grammar_statistics):
        rule_info = ClassicRuleInfo()
        self._rule_info[rule] = rule_info
        self.update_fertility(rule, rule_info.points_total())

    def rule_used(self, rule, usage_info, grammar_statistics):
        rule_info = self._rule_info[rule]
        rule_info.apply_usage(usage_info)

        if rule == self._worst_rule and usage_info.positive_sentence or \
                rule == self._best_rule and not usage_info.positive_sentence:
            self.search_for_fertility()
        else:
            self.update_fertility(rule, rule_info.points_total())

    def removed_rule(self, rule, grammar_statistics):
        del self._rule_info[rule]

        if rule == self._worst_rule or rule == self._best_rule:
            self.search_for_fertility()

    @staticmethod
    def create_usage(grammar_statistics, cyk_result, sentence):
        price_value = grammar_statistics.fitness.valid_sentence_price \
            if sentence.is_positive_sentence or sentence.is_positive_sentence is None \
            else grammar_statistics.fitness.invalid_sentence_price
        return ClassicRuleUsageInfo(sentence.is_positive_sentence, 1, price_value)


class StatisticsVisitor(object):
    def __call__(self, production, grammar_statistics, sentence, cyk_result, rules_population):
        usage_info = grammar_statistics.rule_statistics.create_usage(grammar_statistics, cyk_result,
                                                                     sentence)
        grammar_statistics.on_rule_usage(production.rule, usage_info)


class ClassicFitness(Fitness):
    def __init__(self, base_fitness, classical_fitness_weight, fertility_weight, positive_weight,
                 negative_weight, valid_sentence_price=1, invalid_sentence_price=1):
        self.base_fitness = base_fitness
        self.classical_fitness_weight = classical_fitness_weight
        self.fertility_weight = fertility_weight
        self.positive_weight = positive_weight
        self.negative_weight = negative_weight
        self.valid_sentence_price = valid_sentence_price
        self.invalid_sentence_price = invalid_sentence_price

    def calculate(self, grammar_statistics, rule):
        rule_info, min_fertility, max_fertility = grammar_statistics.get_rule_statistics(rule)

        fertility = (rule_info.points_gained_for_valid_sentences -
                     rule_info.points_gained_for_invalid_sentences - min_fertility) / \
                    (max_fertility - min_fertility if max_fertility != min_fertility else 1)

        if rule_info.valid_sentence_usage + rule_info.invalid_sentence_usage == 0:
            classic_fitness = self.base_fitness
        else:
            classic_fitness = (self.positive_weight * rule_info.valid_sentence_usage) / \
                              (self.positive_weight * rule_info.valid_sentence_usage +
                               self.negative_weight * rule_info.invalid_sentence_usage)

        fitness = \
            (self.classical_fitness_weight * classic_fitness + self.fertility_weight * fertility) /\
            (self.classical_fitness_weight + self.fertility_weight)

        return fitness


class DummyCykStatistics(object):
    def get_rule_statistics(self, rule):
        return None

    def on_added_new_rule(self, rule):
        pass

    def on_rule_usage(self, rule, usage_info=None):
        pass

    def on_rule_removed(self, rule):
        pass

    def update_fitness(self):
        pass


class GrammarStatistics(DummyCykStatistics):
    def __init__(self, randomizer, rule_statistics, statistics_visitors, fitness):
        self.randomizer = randomizer
        self.rule_statistics = rule_statistics
        self.statistics_visitors = statistics_visitors
        self.fitness = fitness

    def get_rule_statistics(self, rule):
        return self.rule_statistics.get_rule_statistics(rule, self)

    def on_added_new_rule(self, rule):
        self.rule_statistics.added_new_rule(rule, self)

    def on_rule_usage(self, rule, usage_info=None):
        if self.rule_statistics.has_rule(rule):
            self.rule_statistics.rule_used(rule, usage_info, self)

    def on_rule_removed(self, rule):
        self.rule_statistics.removed_rule(rule, self)

    def update_fitness(self):
        self.rule_statistics.update_fitness(self)
