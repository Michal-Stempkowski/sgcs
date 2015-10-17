import unittest
from hamcrest import *
from sgcs.induction.rule import Rule, TerminalRule
from sgcs.induction.rule_population import RulePopulation, RulePopulationAccessViolationError
from sgcs.induction.symbol import Symbol


class TestRulePopulation(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sut = RulePopulation()

        self.rules = [
            Rule('A', 'B', 'C'),
            Rule('D', 'B', 'C'),
            Rule('A', 'J', 'C'),
            Rule('A', 'B', 'J')
        ]

    def test_adding_production_should_result_in_storing_it(self):
        # Given:
        for rule in self.rules:
            self.sut.add_rule(rule)

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