from enum import Enum
import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *
from sgcs.induction.coverage import TerminalCoverageOperator, UniversalCoverageOperator, \
    StartingCoverageOperator, AggressiveCoverageOperator
from sgcs.induction.cyk_configuration import CykConfiguration, CoverageConfiguration, \
    CoverageOperators
from sgcs.induction.cyk_service import CykService
from sgcs.induction.detector import Detector
from sgcs.induction.environment import Environment
from sgcs.induction.production import Production, EmptyProduction
from sgcs.induction.rule import TerminalRule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol
from sgcs.utils import Randomizer


class CykReasoningStatus(Enum):
    unknown_terminal_symbol = 0
    no_effector_found = 1
    no_starting_symbol = 2


class CoverageOperatorTestCommon(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cyk_service_mock = create_autospec(CykService)

        self.cyk_configuration_mock = create_autospec(CykConfiguration)

        self.cyk_service_mock.randomizer = create_autospec(Randomizer)
        self.cyk_service_mock.configuration.return_value = self.cyk_configuration_mock

        self.environment_mock = create_autospec(Environment)

        self.rule_population_mock = create_autospec(RulePopulation)

        type(self.rule_population_mock).universal_symbol = \
            PropertyMock(Symbol, return_value=Symbol(hash('U')))
        type(self.rule_population_mock).starting_symbol = \
            PropertyMock(Symbol, return_value=Symbol(hash('S')))

        self.coordinates = 0, 2

        self.sut = None

    def operator_executes_with_some_chance_scenario(self):
        # Given:
        self.cyk_service_mock.randomizer.perform_with_chance.side_effect = [False, True]

        # When/Then:
        assert_that(
            self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates),
            is_(EmptyProduction(Detector(self.coordinates))))

        assert_that(
            self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates),
            is_not(EmptyProduction(Detector(self.coordinates))))


class TestTerminalCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = TerminalCoverageOperator(self.cyk_service_mock)

        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))
        self.rule_population_mock.get_random_terminal_symbol.return_value = Symbol(hash('A'))

    def test_operators_execute_with_some_chance(self):
        self.operator_executes_with_some_chance_scenario()

    def test_given_unknown_terminal_symbol_should_cover_it(self):
        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(equal_to(Production(
            Detector(self.coordinates),
            TerminalRule(Symbol(hash('A')), Symbol(hash('a')))))))


class TestUniversalCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = UniversalCoverageOperator(self.cyk_service_mock)

        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))

    def test_operators_execute_with_some_chance(self):
        self.operator_executes_with_some_chance_scenario()

    def test_given_unknown_terminal_symbol_should_cover_it(self):
        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(equal_to(Production(
            Detector(self.coordinates),
            TerminalRule(Symbol(hash('U')), Symbol(hash('a')))))))


class TestStartingCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = StartingCoverageOperator(self.cyk_service_mock)

    def test_operators_execute_with_some_chance(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = True

        # When/Then:
        self.operator_executes_with_some_chance_scenario()

    def test_given_sentence_of_length_greater_than_1_should_not_cover_it(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 5

        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_positivity_of_sentence_unknown__no_coverage_should_occur(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = None

        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_negative_sentence__no_coverage_should_occur(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = False

        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_positive_sentence_of_length_1__coverage_should_occur(self):
        # Given:
        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = True

        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(equal_to(Production(
            Detector(self.coordinates),
            TerminalRule(self.rule_population_mock.starting_symbol, Symbol(hash('a')))))))


class TestAggressiveCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = AggressiveCoverageOperator(self.cyk_service_mock)

        # self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))

    def test_operators_execute_with_some_chance(self):
        self.operator_executes_with_some_chance_scenario()

    def test_given_sentence_of_unknown_positivity__coverage_should_not_occur(self):
        self.environment_mock.is_sentence_positive.return_value = None

        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_negative_sentence__coverage_should_not_occur(self):
        self.environment_mock.is_sentence_positive.return_value = False

        # When:
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    # def test_given_positive_sentence__coverage_should_occur(self):
    #     self.environment_mock.is_sentence_positive.return_value = True
    #
    #     # When:
    #     result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)
    #
    #     # Then:
    #     assert_that(result, is_(None))

    # def test_given_unknown_terminal_symbol_should_cover_it(self):
    #     # When:
    #     result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)
    #
    #     # Then:
    #     assert_that(
    #         result,
    #         is_(equal_to(TerminalRule(Symbol(hash('U')), Symbol(hash('a'))))))
