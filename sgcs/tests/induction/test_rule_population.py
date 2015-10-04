import unittest
from hamcrest import *
from sgcs.induction.rule import Rule
from sgcs.induction.rule_population import RulePopulation, RulePopulationAccessViolationError


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
