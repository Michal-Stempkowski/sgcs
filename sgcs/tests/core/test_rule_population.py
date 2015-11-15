import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.rule import Rule, TerminalRule
from core.rule_population import RulePopulation, RulePopulationAccessViolationError
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

    def add_rules(self):
        for rule in self.rules:
            self.sut.add_rule(rule)

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
        self.sut.add_rule(rule_a)
        self.sut.add_rule(rule_b)

        assert_that(self.sut.rules_by_right, is_(empty()))
        assert_that(self.sut.get_terminal_rules(Symbol('a')), only_contains(rule_a, rule_b))
        assert_that(self.sut.get_terminal_rules(Symbol('b')), is_(empty()))
        assert_that(self.sut.get_terminal_rules(), only_contains(rule_a, rule_b))

    def test_universal_symbol_should_work_properly(self):
        # Given:
        rule_a = TerminalRule(self.sut.universal_symbol, Symbol('a'))
        rule_b = TerminalRule(self.sut.universal_symbol, Symbol('b'))

        # When:
        self.sut.add_rule(rule_a)
        self.sut.add_rule(rule_b)
        tmp = self.sut.get_terminal_rules()

        # Then:
        assert_that(self.sut.rules_by_right, is_(empty()))
        assert_that(self.sut.get_terminal_rules(Symbol('a')), only_contains(rule_a))
        assert_that(self.sut.get_terminal_rules(Symbol('b')), only_contains(rule_b))
        assert_that(self.sut.get_terminal_rules(), only_contains(rule_a, rule_b))

    def test_should_be_able_to_obtain_random_population(self):
        # Given:
        self.add_rules()

        randomizer_mock = create_autospec(Randomizer)
        randomizer_mock.sample.return_value = [Rule('A', 'J', 'C'), Rule('D', 'B', 'C')]

        # When:
        rules = self.sut.get_random_rules(randomizer_mock, False, 2)

        # Then:
        assert_that(rules, only_contains(Rule('D', 'B', 'C'), Rule('A', 'J', 'C')))
        assert_that(randomizer_mock.sample.called)

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

