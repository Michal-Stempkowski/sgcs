import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *

from sgcs.induction.cyk_service import CykService
from sgcs.induction.cyk_statistics import RuleStatistics, CykStatistics, PasiekaFitness, RuleInfo, \
    LeftSideInfo
from sgcs.induction.rule import Rule
from sgcs.induction.symbol import Symbol


class TestRuleStatistics(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = RuleStatistics()
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

    def test_for_unknown_rule_no_statistics_should_be_provided(self):
        assert_that(self.sut.get_rule_statistics(self.rule), is_(None))

    def test_should_be_able_to_add_new_rule(self):
        # Given:
        self.sut.added_new_rule(self.rule)

        # When:
        rule_info = self.sut.get_rule_statistics(self.rule)

        # Then:
        assert_that(rule_info, is_not(None))
        assert_that(rule_info[0].rule_usage, is_(equal_to(0)))
        assert_that(rule_info[1].left_side_usage, is_(equal_to(0)))

    def test_should_be_able_to_count_rule_usage(self):
        # Given:
        self.sut.added_new_rule(self.rule)
        another_rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('G')))
        self.sut.added_new_rule(another_rule)

        # When:
        self.sut.rule_used(self.rule)
        self.sut.rule_used(self.rule)
        self.sut.rule_used(another_rule)

        # Then:
        rule_info = self.sut.get_rule_statistics(self.rule)
        assert_that(rule_info, is_not(None))
        assert_that(rule_info[0].rule_usage, is_(equal_to(2)))
        assert_that(rule_info[1].left_side_usage, is_(equal_to(3)))

        another_rule_info = self.sut.get_rule_statistics(another_rule)
        assert_that(another_rule_info, is_not(None))
        assert_that(another_rule_info[0].rule_usage, is_(equal_to(1)))
        assert_that(another_rule_info[1].left_side_usage, is_(equal_to(3)))


class TestCykStatistics(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rule_statistics_mock = create_autospec(RuleStatistics)
        self.sut = CykStatistics(self.rule_statistics_mock)
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

    def test_should_be_able_to_get_rule_statistics(self):
        self.rule_statistics_mock.get_rule_statistics.return_value = 44
        assert_that(self.sut.get_rule_statistics(self.rule), is_(equal_to(44)))

    def test_should_be_able_to_add_new_rule(self):
        self.sut.on_added_new_rule(self.rule)
        self.rule_statistics_mock.added_new_rule.assert_called_once_with(self.rule)

    def test_should_be_able_to_add_rule_usage(self):
        self.sut.on_rule_usage(self.rule)
        self.rule_statistics_mock.rule_used.assert_called_once_with(self.rule)


class TestPasiekaFitness(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = PasiekaFitness()
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

        self.statistics_mock = create_autospec(CykStatistics)
        self.cyk_service_mock = create_autospec(CykService)
        self.cyk_service_mock.configure_mock(statistics=self.statistics_mock)

    def test_fitness_should_be_calculated_properly(self):
        rule_info = RuleInfo()
        rule_info.rule_usage = 4

        left_side_info = LeftSideInfo()
        left_side_info.left_side_usage = 5

        self.statistics_mock.get_rule_statistics.return_value = rule_info, left_side_info
        assert_that(self.sut.calculate_value(self.cyk_service_mock, self.rule), is_(equal_to(0.8)))
