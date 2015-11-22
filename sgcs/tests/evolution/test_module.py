import copy
import unittest
from itertools import chain
from random import Random
from unittest.mock import MagicMock, create_autospec, call
from hamcrest import *

from core.rule import Rule, TerminalRule
from core.rule_population import RulePopulation
from core.symbol import Symbol
from evolution.evolution_configuration import EvolutionConfiguration, \
    EvolutionOperatorsConfiguration, EvolutionOperatorConfiguration, EvolutionSelectorConfiguration, \
    EvolutionSelectorType, EvolutionRandomSelectorConfiguration, \
    EvolutionRouletteSelectorConfiguration
from evolution.evolution_service import EvolutionService
from rule_adding import AddingRuleSupervisor, AddingRuleWithElitismStrategy, \
    AddingRulesConfiguration, CrowdingConfiguration, ElitismConfiguration, SimpleAddingRuleStrategy, \
    AddingRuleWithCrowdingStrategy
from statistics.grammar_statistics import GrammarStatistics, ClassicRuleStatistics, \
    StatisticsVisitor, ClassicFitness, ClassicRuleUsageInfo
from utils import Randomizer


class TestEvolution(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.randomizer = Randomizer(Random())

        selector_configuration = [
            EvolutionRandomSelectorConfiguration.create(),
            EvolutionRouletteSelectorConfiguration.create()
        ]
        self.configuration = EvolutionConfiguration.create(
            selector_configuration, inversion_chance=0, mutation_chance=0, crossover_chance=0)
        self.create_rule_population()
        self.create_grammar_statistics()
        self.create_rule_adding()

        self.sut = EvolutionService(self.configuration, self.randomizer)

        self.rules = [
            Rule(Symbol('S'), Symbol('NP'), Symbol('VP')),
            Rule(Symbol('VP'), Symbol('VP'), Symbol('PP')),
            Rule(Symbol('VP'), Symbol('V'), Symbol('NP')),
            TerminalRule(Symbol('VP'), Symbol('eats')),
            Rule(Symbol('PP'), Symbol('P'), Symbol('NP')),
            Rule(Symbol('NP'), Symbol('Det'), Symbol('N')),
            TerminalRule(Symbol('NP'), Symbol('she')), TerminalRule(Symbol('V'), Symbol('eats')),
            TerminalRule(Symbol('P'), Symbol('with')), TerminalRule(Symbol('N'), Symbol('fish')),
            TerminalRule(Symbol('N'), Symbol('fork')), TerminalRule(Symbol('Det'), Symbol('a'))
        ]

    def create_rule_population(self):
        self.starting_symbol = Symbol('S')
        self.rule_population = RulePopulation(self.starting_symbol)

    def create_grammar_statistics(self):
        base_fitness = 5
        classical_fitness_weight = 1
        fertility_weight = 1
        positive_weight = 1
        negative_weight = 1
        self.grammar_statistics = GrammarStatistics(
            self.randomizer, ClassicRuleStatistics(),
            ClassicFitness(base_fitness, classical_fitness_weight, fertility_weight,
                           positive_weight, negative_weight))

    def create_rule_adding(self):
        configuration = AddingRulesConfiguration.create(
            crowding_factor=2,
            crowding_size=3,
            elitism_size=2
        )

        adding_strategies = [SimpleAddingRuleStrategy(),
                             AddingRuleWithCrowdingStrategy(),
                             AddingRuleWithElitismStrategy()]

        self.rule_adding = AddingRuleSupervisor(self.randomizer, configuration, adding_strategies)

    def simulate_induction_part_work(self, rules):
        for rule in rules:
            self.rule_adding.add_rule(rule, self.rule_population, self.grammar_statistics)

        for rule in rules:
            rule_usage_info = ClassicRuleUsageInfo(True, 1)
            positive_usages = self.randomizer.randint(1, 4)
            for _ in range(positive_usages):
                self.grammar_statistics.on_rule_usage(rule, rule_usage_info)

            rule_usage_info.positive_sentence = False
            self.grammar_statistics.on_rule_usage(rule, rule_usage_info)

            self.grammar_statistics.fitness.get(self.grammar_statistics, rule)

    def get_symbols_from_rules(self, rules):
        return {y for y in chain.from_iterable(
            (x.parent, x.left_child, x.right_child) for x in rules)}

    def assert_contains_rules(self, rules, rules_pool):
        for rule in rules:
            assert_that(rules_pool, has_item(rule))

    def count_rules_that_has_changed(self, old):
        changed_rules = 0
        for rule in self.rule_population.get_all_non_terminal_rules():
            changed_rules += 1 if rule not in old else 0
        return changed_rules

    def test_given_no_operator_used_rule_population_should_remain_unchanged(self):
        # Given:
        self.simulate_induction_part_work(self.rules)

        old_population = copy.deepcopy(self.rule_population)

        # When:
        self.sut.run_genetic_algorithm(self.grammar_statistics, self.rule_population,
                                       self.rule_adding)

        # Then:
        self.assert_contains_rules(self.rule_population.get_all_non_terminal_rules(),
                                   list(old_population.get_all_non_terminal_rules()))

        old_symbols = self.get_symbols_from_rules(old_population.get_all_non_terminal_rules())
        new_symbols = self.get_symbols_from_rules(self.rule_population.get_all_non_terminal_rules())
        assert_that(old_symbols, has_items(*new_symbols))

    def promote_those_rules_to_elite(self, rules):
        for rule in rules:
            rule_usage_info = ClassicRuleUsageInfo(True, 1)
            positive_usages = 5
            for _ in range(positive_usages):
                self.grammar_statistics.on_rule_usage(rule, rule_usage_info)

    def test_given_high_operator_usage_rule_population_should_expect_some_major_change(self):
        # Given:
        self.configuration.operators.inversion.chance = 1
        self.configuration.operators.mutation.chance = 1
        self.configuration.operators.crossover.chance = 1

        self.simulate_induction_part_work(self.rules)
        self.promote_those_rules_to_elite(self.rules[0:2])

        elite = list(self.rules[0:2])

        old_population = copy.deepcopy(self.rule_population)

        # When:
        self.sut.run_genetic_algorithm(self.grammar_statistics, self.rule_population,
                                       self.rule_adding)

        # Then:
        self.assert_contains_rules(elite, list(old_population.get_all_non_terminal_rules()))

        assert_that(self.count_rules_that_has_changed(old_population.get_all_non_terminal_rules()),
                    is_(greater_than_or_equal_to(2)))

        old_symbols = self.get_symbols_from_rules(old_population.get_all_non_terminal_rules())
        new_symbols = self.get_symbols_from_rules(self.rule_population.get_all_non_terminal_rules())
        assert_that(old_symbols, not_(has_items(*new_symbols)))
