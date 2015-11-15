import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.rule import Rule, TerminalRule
from core.rule_population import RulePopulation
from core.symbol import Symbol
from sgcs.induction.coverage.rule_adding import SimpleAddingRuleStrategy, AddingRuleStrategyHint, \
    AddingRuleWithCrowdingStrategy, AddingRuleSupervisor, AddingRuleStrategy
from sgcs.induction.cyk_configuration import CrowdingConfiguration, AddingRulesConfiguration, \
    CykConfiguration
from sgcs.induction.cyk_service import CykService
from statistics.cyk_statistics import PasiekaFitness, GrammarStatistics


class TestAddingRuleStrategyCommon(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = None
        self.rule = self.mk_rule('A', 'B', 'C')
        self.terminal_rule = TerminalRule(hash('A'), hash('a'))
        self.rule_population_mock = create_autospec(RulePopulation)

        self.crowding_settings_mock = create_autospec(CrowdingConfiguration)
        self.crowding_settings_mock.configure_mock(factor=2, size=3)

        self.fitness_mock = create_autospec(PasiekaFitness)

        self.cyk_service_mock = create_autospec(CykService)
        self.cyk_service_mock.configure_mock(configuration=create_autospec(CykConfiguration),
                                             fitness=self.fitness_mock,
                                             statistics=create_autospec(GrammarStatistics))
        self.cyk_service_mock.configuration.configure_mock(
            rule_adding=create_autospec(AddingRulesConfiguration))
        self.cyk_service_mock.configuration.rule_adding.configure_mock(
            crowding=self.crowding_settings_mock)

    @staticmethod
    def mk_rule(parent, left, right):
        return Rule(Symbol(hash(parent)), Symbol(hash(left)), Symbol(hash(right)))


class TestSimpleAddingRuleStrategy(TestAddingRuleStrategyCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = SimpleAddingRuleStrategy()

    def test_should_know_if_strategy_is_applicable(self):
        assert_that(self.sut.is_applicable(AddingRuleStrategyHint.expand_population), is_(True))
        assert_that(self.sut.is_applicable(AddingRuleStrategyHint.control_population_size),
                    is_(False))

    def test_should_be_able_to_apply_strategy(self):
        self.sut.apply(self.cyk_service_mock, self.rule, self.rule_population_mock)
        self.rule_population_mock.add_rule.assert_called_once_with(self.rule)
        self.cyk_service_mock.statistics.on_added_new_rule.\
            assert_called_once_with(self.rule)


class TestAddingRuleWithCrowdingStrategy(TestAddingRuleStrategyCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = AddingRuleWithCrowdingStrategy()

    def test_should_know_if_strategy_is_applicable(self):
        assert_that(self.sut.is_applicable(AddingRuleStrategyHint.expand_population), is_(False))
        assert_that(self.sut.is_applicable(AddingRuleStrategyHint.control_population_size),
                    is_(True))

    def fitness_get_keyfunc_dummy(self, _):
        return lambda r: 0 \
            if r == self.mk_rule('A', 'G', 'C') \
            else 1000

    def test_should_be_able_to_apply_strategy_for_terminal_production(self):
        # Given:
        rule_to_be_replaced = self.mk_rule('A', 'G', 'C')
        self.rule_population_mock.get_random_rules.side_effect = [
            [rule_to_be_replaced, self.mk_rule('T', 'E', 'C'), self.mk_rule('A', 'E', 'W')],
            [self.mk_rule('A', 'W', 'H'), self.mk_rule('T', 'B', 'W'), self.mk_rule('G', 'W', 'C')]
        ]
        self.fitness_mock.get_keyfunc_getter.side_effect = self.fitness_get_keyfunc_dummy

        # When:
        self.sut.apply(self.cyk_service_mock, self.rule, self.rule_population_mock)

        # Then:
        assert_that(self.rule_population_mock.get_random_rules.call_count, is_(equal_to(2)))
        self.rule_population_mock.remove_rule.assert_called_once_with(rule_to_be_replaced)
        self.cyk_service_mock.statistics.on_rule_removed.\
            assert_called_once_with(rule_to_be_replaced)
        self.rule_population_mock.add_rule.assert_called_once_with(self.rule)
        self.cyk_service_mock.statistics.on_added_new_rule.\
            assert_called_once_with(self.rule)


class TestAddingRuleSupervisor(TestAddingRuleStrategyCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.expanding_strategy_mock = create_autospec(AddingRuleStrategy)
        self.expanding_strategy_mock.is_applicable.side_effect = \
            lambda x: x == AddingRuleStrategyHint.expand_population

        self.controlling_strategy_mock = create_autospec(AddingRuleStrategy)
        self.controlling_strategy_mock.is_applicable.side_effect = \
            lambda x: x == AddingRuleStrategyHint.control_population_size

        self.sut = AddingRuleSupervisor()
        self.sut.strategies = [self.expanding_strategy_mock, self.controlling_strategy_mock]

    def test_valid_rule_strategies_should_be_used(self):
        self.sut.add_rule(self.rule, self.rule_population_mock, self.cyk_service_mock)
        self.expanding_strategy_mock.apply.assert_called_once_with(
            self.cyk_service_mock, self.rule, self.rule_population_mock)

        self.sut.add_rule(self.rule, self.rule_population_mock, self.cyk_service_mock,
                          AddingRuleStrategyHint.control_population_size)
        self.controlling_strategy_mock.apply.assert_called_once_with(
            self.cyk_service_mock, self.rule, self.rule_population_mock)
