import unittest
from unittest.mock import create_autospec, call
from hamcrest import *

from core.rule import Rule, TerminalRule
from core.rule_population import RulePopulation, RulePopulationAccessViolationError, \
    StochasticRulePopulation
from core.symbol import Symbol
from sgcs.utils import Randomizer


class TestRulePopulation(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sut = RulePopulation('S')

        self.rules = [
            Rule('A', 'B', 'C'),
            Rule('D', 'B', 'C'),
            Rule('A', 'J', 'C'),
            Rule('A', 'B', 'J')
        ]

        self.randomizer_mock = create_autospec(Randomizer)

    def add_rules(self):
        for rule in self.rules:
            self.sut.add_rule(rule, self.randomizer_mock)

        assert_that(self.sut.get_all_non_terminal_rules(), contains_inanyorder(*self.rules))

    def test_adding_rule_should_result_in_storing_it(self):
        # Given:
        self.add_rules()

        # When/Then:
        assert_that(self.sut.get_rules_by_right(('B', 'C')),
                    only_contains(self.rules[0], self.rules[1]))
        assert_that(self.sut.get_rules_by_right(('B', 'B')), is_(empty()))
        assert_that(self.sut.get_rules_by_right(('A', 'B')), is_(empty()))
        assert_that(calling(self.sut.get_rules_by_right).with_args(('A',)),
                    raises(RulePopulationAccessViolationError))
        assert_that(calling(self.sut.get_rules_by_right).with_args(('A', 'B', 'J')),
                    raises(RulePopulationAccessViolationError))

    def test_should_be_able_to_add_terminal_rule(self):
        rule_a = TerminalRule(Symbol('A'), Symbol('a'))
        rule_b = TerminalRule(Symbol('B'), Symbol('a'))
        self.sut.add_rule(rule_a, self.randomizer_mock)
        self.sut.add_rule(rule_b, self.randomizer_mock)

        assert_that(self.sut._rules_by_right, is_(empty()))
        assert_that(self.sut.get_terminal_rules(Symbol('a')), only_contains(rule_a, rule_b))
        assert_that(self.sut.get_terminal_rules(Symbol('b')), is_(empty()))
        assert_that(self.sut.get_terminal_rules(), only_contains(rule_a, rule_b))

    def test_universal_symbol_should_work_properly(self):
        # Given:
        rule_a = TerminalRule(self.sut.universal_symbol, Symbol('a'))
        rule_b = TerminalRule(self.sut.universal_symbol, Symbol('b'))

        # When:
        self.sut.add_rule(rule_a, self.randomizer_mock)
        self.sut.add_rule(rule_b, self.randomizer_mock)

        # Then:
        assert_that(self.sut._rules_by_right, is_(empty()))
        assert_that(self.sut.get_terminal_rules(Symbol('a')), only_contains(rule_a))
        assert_that(self.sut.get_terminal_rules(Symbol('b')), only_contains(rule_b))
        assert_that(self.sut.get_terminal_rules(), only_contains(rule_a, rule_b))

    def test_should_be_able_to_obtain_random_population(self):
        # Given:
        self.add_rules()

        self.randomizer_mock.sample.return_value = [Rule('A', 'J', 'C'), Rule('D', 'B', 'C')]

        # When:
        rules = self.sut.get_random_rules(self.randomizer_mock, False, 2)

        # Then:
        assert_that(rules, only_contains(Rule('D', 'B', 'C'), Rule('A', 'J', 'C')))
        assert_that(self.randomizer_mock.sample.called)

    def test_should_be_able_to_remove_a_rule(self):
        # Given:
        self.add_rules()
        assert_that(
            self.sut.get_rules_by_right((self.rules[0].left_child, self.rules[0].right_child)),
            only_contains(self.rules[0], self.rules[1])
        )

        # When:
        self.sut.remove_rule(self.rules[0])

        # Then:
        assert_that(
            self.sut.get_rules_by_right((self.rules[0].left_child, self.rules[0].right_child)),
            only_contains(self.rules[1])
        )

    def test_should_be_able_to_obtain_random_population_matching_filter(self):
        # Given:
        self.add_rules()

        filter = lambda x: x.right_child == 'C'

        self.randomizer_mock.sample.return_value = [Rule('A', 'J', 'C'), Rule('D', 'B', 'C')]

        # When:
        rules = self.sut.get_random_rules_matching_filter(self.randomizer_mock, False, 2, filter)

        # Then:
        assert_that(rules, only_contains(Rule('D', 'B', 'C'), Rule('A', 'J', 'C')))
        assert_that(self.randomizer_mock.sample.call_count, is_(equal_to(1)))

    def test_should_know_if_rule_already_exists(self):
        # Given:
        self.add_rules()
        not_added_rule = Rule('J', 'J', 'J')

        # When:
        for rule in self.rules:
            assert_that(self.sut.has_rule(rule))
        assert_that(not_(self.sut.has_rule(not_added_rule)))


class TestStochasticRulePopulation(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = StochasticRulePopulation('S')
        self.new_rule = self.mk_rule('A', 'B', 'C')
        self.another_rule_with_parent_a = self.mk_rule('A', 'E', 'F')
        self.randomizer_mock = create_autospec(Randomizer)

    @staticmethod
    def mk_rule(parent, left_child, right_child):
        return Rule(hash(parent), hash(left_child), hash(right_child))

    def test_adding_new_rule_should_result_in_generating_probability_for_it(self):
        # Given:
        self.randomizer_mock.uniform.return_value = 0.3

        # When:
        self.sut.add_rule(self.new_rule, self.randomizer_mock)

        # Then:
        self.randomizer_mock.uniform.assert_called_once_with(0.01, 1)
        assert_that(self.sut.has_rule(self.new_rule))
        assert_that(self.sut.get_normalized_rule_probability(self.new_rule), is_(equal_to(1)))

    def test_not_existing_rule_should_have_0_probability(self):
        assert_that(self.sut.get_normalized_rule_probability(self.new_rule), is_(equal_to(0)))

    def test_normalization_should_be_performed_after_rule_adding(self):
        # Given:
        self.randomizer_mock.uniform.side_effect = [0.1, 0.3]

        # When:
        self.sut.add_rule(self.new_rule, self.randomizer_mock)
        self.sut.add_rule(self.another_rule_with_parent_a, self.randomizer_mock)

        # Then:
        self.randomizer_mock.uniform.assert_has_calls([call(0.01, 1), call(0.01, 1)])
        assert_that(self.sut.has_rule(self.new_rule))
        assert_that(self.sut.has_rule(self.another_rule_with_parent_a))
        assert_that(self.sut.get_normalized_rule_probability(self.new_rule), is_(close_to(0.25, delta=0.01)))
        assert_that(self.sut.get_normalized_rule_probability(self.another_rule_with_parent_a),
                    is_(close_to(0.75, delta=0.01)))

    def test_normalization_should_be_performed_after_rule_removal(self):
        # Given:
        self.randomizer_mock.uniform.side_effect = [0.1, 0.3]
        self.sut.add_rule(self.new_rule, self.randomizer_mock)
        self.sut.add_rule(self.another_rule_with_parent_a, self.randomizer_mock)

        # When:
        self.sut.remove_rule(self.new_rule)

        # Then:
        assert_that(self.sut.has_rule(self.new_rule), is_(False))
        assert_that(self.sut.has_rule(self.another_rule_with_parent_a))
        assert_that(self.sut.get_normalized_rule_probability(self.new_rule), is_(equal_to(0)))
        assert_that(self.sut.get_normalized_rule_probability(self.another_rule_with_parent_a),
                    is_(close_to(1, delta=0.01)))

    @staticmethod
    def create_fitness_getter_mock(rule_usages):
        return lambda rule: rule_usages[rule]

    def test_probability_estimation_should_work(self):
        # Given:
        self.randomizer_mock.uniform.side_effect = [0.1, 0.3]
        self.sut.add_rule(self.new_rule, self.randomizer_mock)
        self.sut.add_rule(self.another_rule_with_parent_a, self.randomizer_mock)

        rule_usages = dict()
        rule_usages[self.new_rule] = 1
        rule_usages[self.another_rule_with_parent_a] = 2
        fitness_getter = self.create_fitness_getter_mock(rule_usages)

        # When:
        self.sut.perform_probability_estimation(fitness_getter)

        # Then:
        assert_that(self.sut.rule_probabilities[self.new_rule],
                    is_(close_to(0.33, delta=0.01)))
        assert_that(self.sut.get_normalized_rule_probability(self.new_rule),
                    is_(close_to(0.33, delta=0.01)))
        assert_that(self.sut.get_normalized_rule_probability(self.another_rule_with_parent_a),
                    is_(close_to(0.67, delta=0.01)))
        assert_that(self.sut.rule_probabilities[self.another_rule_with_parent_a],
                    is_(close_to(0.67, delta=0.01)))
        assert_that(self.sut.left_side_probabilities[self.new_rule.parent],
                    is_(close_to(1, delta=0.01)))
