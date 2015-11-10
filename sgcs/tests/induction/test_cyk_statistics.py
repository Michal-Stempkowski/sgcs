import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *

from sgcs.induction.cyk_service import CykService
from sgcs.induction.cyk_statistics import PasiekaRuleStatistics, CykStatistics, PasiekaFitness, PasiekaRuleInfo, \
    PasiekaLeftSideInfo, ClassicRuleStatistics, ClassicRuleUsageInfo
from sgcs.induction.rule import Rule
from sgcs.induction.symbol import Symbol


class TestPasiekaRuleStatistics(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = PasiekaRuleStatistics()
        self.cyk_service_mock = create_autospec(CykService)
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

    def test_for_unknown_rule_no_statistics_should_be_provided(self):
        assert_that(self.sut.get_rule_statistics(self.rule, self.cyk_service_mock), is_(None))

    def test_should_be_able_to_add_new_rule(self):
        # Given:
        self.sut.added_new_rule(self.rule, self.cyk_service_mock)

        # When:
        rule_info = self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)

        # Then:
        assert_that(rule_info, is_not(None))
        assert_that(rule_info[0].rule_usage, is_(equal_to(0)))
        assert_that(rule_info[1].left_side_usage, is_(equal_to(0)))

    def two_rules_with_common_parent_setup(self, rule, another_rule):
        # Given:
        self.sut.added_new_rule(rule, self.cyk_service_mock)
        self.sut.added_new_rule(another_rule, self.cyk_service_mock)

        # When:
        self.sut.rule_used(rule, None, self.cyk_service_mock)
        self.sut.rule_used(rule, None, self.cyk_service_mock)
        self.sut.rule_used(another_rule, None, self.cyk_service_mock)

    def test_should_be_able_to_count_rule_usage(self):
        # Given:
        another_rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('G')))

        # When:
        self.two_rules_with_common_parent_setup(self.rule, another_rule)

        # Then:
        rule_info = self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)
        assert_that(rule_info, is_not(None))
        assert_that(rule_info[0].rule_usage, is_(equal_to(2)))
        assert_that(rule_info[1].left_side_usage, is_(equal_to(3)))

        another_rule_info = self.sut.get_rule_statistics(another_rule, self.cyk_service_mock)
        assert_that(another_rule_info, is_not(None))
        assert_that(another_rule_info[0].rule_usage, is_(equal_to(1)))
        assert_that(another_rule_info[1].left_side_usage, is_(equal_to(3)))

    def test_should_be_able_to_remove_rule(self):
        # Given:
        another_rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('G')))
        self.two_rules_with_common_parent_setup(self.rule, another_rule)

        # When:
        self.sut.removed_rule(self.rule, self.cyk_service_mock)

        # Then:
        rule_info = self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)
        assert_that(rule_info, is_(None))

        another_rule_info = self.sut.get_rule_statistics(another_rule, self.cyk_service_mock)
        assert_that(another_rule_info, is_not(None))
        assert_that(another_rule_info[0].rule_usage, is_(equal_to(1)))
        assert_that(another_rule_info[1].left_side_usage, is_(equal_to(1)))


class TestClassicRuleStatistics(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = ClassicRuleStatistics()
        self.cyk_service_mock = create_autospec(CykService)
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

    def test_for_unknown_rule_no_statistics_should_be_provided(self):
        rule_statistics, _, _ = self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)
        assert_that(rule_statistics, is_(None))

    def assert_rule_statistics(self, rule_info, valid_sentence_usage, invalid_sentence_usage,
                               points_gained_for_valid_sentences,
                               points_gained_for_invalid_sentences):
        assert_that(rule_info, is_not(None))
        assert_that(rule_info.valid_sentence_usage, is_(equal_to(valid_sentence_usage)))
        assert_that(rule_info.invalid_sentence_usage, is_(equal_to(invalid_sentence_usage)))
        assert_that(rule_info.points_gained_for_valid_sentences,
                    is_(equal_to(points_gained_for_valid_sentences)))
        assert_that(rule_info.points_gained_for_invalid_sentences,
                    is_(equal_to(points_gained_for_invalid_sentences)))

    def test_should_be_able_to_add_new_rule(self):
        # Given:
        self.sut.added_new_rule(self.rule, self.cyk_service_mock)

        # When:
        rule_info, min_fertility, max_fertility = \
            self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)

        # Then:
        self.assert_rule_statistics(rule_info, 0, 0, 0, 0)
        assert_that(min_fertility, is_(equal_to(0)))
        assert_that(max_fertility, is_(equal_to(0)))

    def rule_with_usage_scenario(self):
        # Given:
        self.sut.added_new_rule(self.rule, self.cyk_service_mock)
        usage_info_1 = ClassicRuleUsageInfo(True, 4, 3)
        usage_info_2 = ClassicRuleUsageInfo(False, 2)

        # When:
        self.sut.rule_used(self.rule, usage_info_1, self.cyk_service_mock)
        self.sut.rule_used(self.rule, usage_info_2, self.cyk_service_mock)

    def test_should_be_able_to_count_rule_usage(self):
        # Given/When:
        self.rule_with_usage_scenario()

        # Then:
        rule_info, min_fertility, max_fertility = \
            self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)

        self.assert_rule_statistics(rule_info, 4, 2, 3, 1)
        assert_that(min_fertility, is_(equal_to(2)))
        assert_that(max_fertility, is_(equal_to(2)))

    def test_should_be_able_to_handle_many_rules_well(self):
        # Given:
        self.sut.added_new_rule(self.rule, self.cyk_service_mock)
        usage_info_1 = ClassicRuleUsageInfo(True, 4, 2)
        self.sut.rule_used(self.rule, usage_info_1, self.cyk_service_mock)

        best_rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('G')))
        self.sut.added_new_rule(best_rule, self.cyk_service_mock)
        usage_info_2 = ClassicRuleUsageInfo(True, 4, 3)
        self.sut.rule_used(best_rule, usage_info_2, self.cyk_service_mock)

        worst_rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('J')))
        self.sut.added_new_rule(worst_rule, self.cyk_service_mock)
        usage_info_3 = ClassicRuleUsageInfo(False, 4, 3)
        self.sut.rule_used(worst_rule, usage_info_3, self.cyk_service_mock)

        # When:
        rule_info_1, min_fertility, max_fertility = \
            self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)
        rule_info_2, _, _ = \
            self.sut.get_rule_statistics(best_rule, self.cyk_service_mock)
        rule_info_3, _, _ = \
            self.sut.get_rule_statistics(worst_rule, self.cyk_service_mock)

        # Then:
        rule_info, min_fertility, max_fertility = \
            self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)

        self.assert_rule_statistics(rule_info_1, 4, 0, 2, 0)
        self.assert_rule_statistics(rule_info_2, 4, 0, 3, 0)
        self.assert_rule_statistics(rule_info_3, 0, 4, 0, 3)
        assert_that(min_fertility, is_(equal_to(-3)))
        assert_that(max_fertility, is_(equal_to(3)))

    def test_should_be_able_to_remove_rule(self):
        # Given:
        self.rule_with_usage_scenario()

        # When:
        self.sut.removed_rule(self.rule, self.cyk_service_mock)

        # Then:
        rule_info, min_fertility, max_fertility = \
            self.sut.get_rule_statistics(self.rule, self.cyk_service_mock)

        assert_that(rule_info, is_(None))
        assert_that(min_fertility, is_(None))
        assert_that(max_fertility, is_(None))


class TestCykStatistics(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rule_statistics_mock = create_autospec(PasiekaRuleStatistics)
        self.cyk_service_mock = create_autospec(CykService)
        self.sut = CykStatistics(self.rule_statistics_mock, self.cyk_service_mock)
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

    def test_should_be_able_to_get_rule_statistics(self):
        self.rule_statistics_mock.get_rule_statistics.return_value = 44
        assert_that(self.sut.get_rule_statistics(self.rule), is_(equal_to(44)))

    def test_should_be_able_to_add_new_rule(self):
        self.sut.on_added_new_rule(self.rule)
        self.rule_statistics_mock.added_new_rule.assert_called_once_with(
            self.rule, self.cyk_service_mock)

    def test_should_be_able_to_add_rule_usage(self):
        self.sut.on_rule_usage(self.rule, None)
        self.rule_statistics_mock.rule_used.assert_called_once_with(
            self.rule, None, self.cyk_service_mock)

    def test_should_be_able_to_remove_rule(self):
        self.sut.on_rule_removed(self.rule)
        self.rule_statistics_mock.removed_rule.assert_called_once_with(
            self.rule, self.cyk_service_mock)


class TestPasiekaFitness(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = PasiekaFitness()
        self.rule = Rule(Symbol(hash('A')), Symbol(hash('B')), Symbol(hash('C')))

        self.statistics_mock = create_autospec(CykStatistics)
        self.cyk_service_mock = create_autospec(CykService)
        self.cyk_service_mock.configure_mock(statistics=self.statistics_mock)

    def test_fitness_should_be_calculated_properly(self):
        rule_info = PasiekaRuleInfo()
        rule_info.rule_usage = 4

        left_side_info = PasiekaLeftSideInfo()
        left_side_info.left_side_usage = 5

        self.statistics_mock.get_rule_statistics.return_value = rule_info, left_side_info
        assert_that(self.sut.calculate(self.cyk_service_mock, self.rule), is_(equal_to(4)))
