import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *

from sgcs.induction.rule import Rule
from sgcs.induction.rule_adding import SimpleAddingRuleStrategy, AddingRuleStrategyHint
from sgcs.induction.rule_population import RulePopulation


class TestAddingRuleStrategyCommon(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = None
        self.rule = Rule(hash('A'), hash('B'), hash('C'))
        self.rule_population_mock = create_autospec(RulePopulation)


class TestSimpleAddingRuleStrategy(TestAddingRuleStrategyCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = SimpleAddingRuleStrategy()

    def test_should_know_if_strategy_is_applicable(self):
        assert_that(self.sut.is_applicable(AddingRuleStrategyHint.expand_population), is_(True))
        assert_that(self.sut.is_applicable(AddingRuleStrategyHint.control_population_size),
                    is_(False))

    def test_should_be_able_to_apply_strategy(self):
        self.sut.apply(self.rule, self.rule_population_mock)
        self.rule_population_mock.add_rule.assert_called_once_with(self.rule)
