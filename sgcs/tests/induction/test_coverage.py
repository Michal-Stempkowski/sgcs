from enum import Enum
from random import shuffle
import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *
from sgcs.induction.coverage import TerminalCoverageOperator, UniversalCoverageOperator, \
    StartingCoverageOperator, AggressiveCoverageOperator, FullCoverageOperator, CoverageOperations, \
    CoverageOperator, CoverageType
from sgcs.induction.cyk_configuration import CykConfiguration, CoverageConfiguration, \
    CoverageOperatorsConfiguration, InvalidCykConfigurationError
from sgcs.induction.cyk_service import CykService
from sgcs.induction.detector import Detector
from sgcs.induction.environment import Environment
from sgcs.induction.production import Production, EmptyProduction
from sgcs.induction.rule import TerminalRule, Rule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol
from sgcs.utils import Randomizer


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
            self.sut.cover(self.cyk_service_mock, self.environment_mock,
                           self.rule_population_mock, self.coordinates),
            is_(EmptyProduction(Detector(self.coordinates))))

        assert_that(
            self.sut.cover(self.cyk_service_mock, self.environment_mock,
                           self.rule_population_mock, self.coordinates),
            is_not(EmptyProduction(Detector(self.coordinates))))


class TestTerminalCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = TerminalCoverageOperator()

        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))
        self.rule_population_mock.get_random_non_terminal_symbol.return_value = Symbol(hash('A'))

    def test_operators_execute_with_some_chance(self):
        self.rule_population_mock.get_random_non_terminal_symbol.return_value = Symbol(hash('C'))
        self.operator_executes_with_some_chance_scenario()

    def test_given_unknown_terminal_symbol_should_cover_it(self):
        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(equal_to(Production(
            Detector(self.coordinates),
            TerminalRule(Symbol(hash('A')), Symbol(hash('a')))))))


class TestUniversalCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = UniversalCoverageOperator()

        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))

    def test_operators_execute_with_some_chance(self):
        self.operator_executes_with_some_chance_scenario()

    def test_given_unknown_terminal_symbol_should_cover_it(self):
        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(equal_to(Production(
            Detector(self.coordinates),
            TerminalRule(Symbol(hash('U')), Symbol(hash('a')))))))

    def test_if_universal_symbol_unset_in_rule_population_error_should_be_raised(self):
        type(self.rule_population_mock).universal_symbol = PropertyMock(Symbol, return_value=None)

        assert_that(calling(self.sut.cover).with_args(
            self.cyk_service_mock,
            self.environment_mock,
            self.rule_population_mock,
            self.coordinates), raises(InvalidCykConfigurationError))


class TestStartingCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = StartingCoverageOperator()

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
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_positivity_of_sentence_unknown__no_coverage_should_occur(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = None

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_negative_sentence__no_coverage_should_occur(self):
        # Given:
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = False

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_positive_sentence_of_length_1__coverage_should_occur(self):
        # Given:
        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))
        self.environment_mock.get_sentence_length.return_value = 1
        self.environment_mock.is_sentence_positive.return_value = True

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(equal_to(Production(
            Detector(self.coordinates),
            TerminalRule(self.rule_population_mock.starting_symbol, Symbol(hash('a')))))))


class TestAggressiveCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = AggressiveCoverageOperator()

    def setup_system_for_successful_rule_selection(self):
        detectors = [Detector((2, 2, 1, 0, 1)), Detector((2, 2, 2, 0, 1))]
        selected_detector = detectors[1]
        self.environment_mock.get_unsatisfied_detectors.return_value = detectors
        self.cyk_service_mock.randomizer.choice.return_value = selected_detector
        self.environment_mock.get_detector_symbols.return_value = \
            Symbol(hash('A')), Symbol(hash('B'))
        self.rule_population_mock.get_random_non_terminal_symbol.return_value = \
            Symbol(hash('C'))

        return selected_detector

    def test_operators_execute_with_some_chance(self):
        self.setup_system_for_successful_rule_selection()
        self.operator_executes_with_some_chance_scenario()

    def test_given_sentence_of_unknown_positivity__coverage_should_not_occur(self):
        self.environment_mock.is_sentence_positive.return_value = None

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_negative_sentence__coverage_should_not_occur(self):
        self.environment_mock.is_sentence_positive.return_value = False

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_positive_sentence__coverage_should_occur(self):
        # Given:
        selected_detector = self.setup_system_for_successful_rule_selection()

        # When:
        result = self.sut.cover(
            self.cyk_service_mock,
            self.environment_mock,
            self.rule_population_mock,
            selected_detector.coordinates[:2])

        # Then:
        assert_that(result, is_(Production(
            selected_detector,
            Rule(Symbol(hash('C')), Symbol(hash('A')), Symbol(hash('B'))))))
        self.environment_mock.get_detector_symbols.assert_called_once_with(
            selected_detector.coordinates)

    def test_given_positive_sentence_but_no_valid_detector_coverage_should_not_occur(self):
        # Given:
        selected_detector = self.setup_system_for_successful_rule_selection()
        self.environment_mock.get_unsatisfied_detectors.return_value = []

        # When:
        result = self.sut.cover(
            self.cyk_service_mock,
            self.environment_mock,
            self.rule_population_mock,
            selected_detector.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(selected_detector)))


class TestFullCoverageOperator(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = FullCoverageOperator()

    def setup_system_for_successful_rule_selection(self):
        detectors = [Detector((2, 2, 1, 0, 1)), Detector((2, 2, 2, 0, 1))]
        selected_detector = detectors[1]
        self.environment_mock.get_unsatisfied_detectors.return_value = detectors
        self.cyk_service_mock.randomizer.choice.return_value = selected_detector
        self.environment_mock.get_detector_symbols.return_value = \
            Symbol(hash('A')), Symbol(hash('B'))

        return selected_detector

    def test_operators_execute_with_some_chance(self):
        self.setup_system_for_successful_rule_selection()
        self.operator_executes_with_some_chance_scenario()

    def test_given_sentence_of_unknown_positivity__coverage_should_not_occur(self):
        self.environment_mock.is_sentence_positive.return_value = None

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_negative_sentence__coverage_should_not_occur(self):
        self.environment_mock.is_sentence_positive.return_value = False

        # When:
        result = self.sut.cover(self.cyk_service_mock, self.environment_mock,
                                self.rule_population_mock, self.coordinates)

        # Then:
        assert_that(result, is_(EmptyProduction(Detector(self.coordinates))))

    def test_given_positive_sentence__coverage_should_occur(self):
        # Given:
        selected_detector = self.setup_system_for_successful_rule_selection()

        # When:
        result = self.sut.cover(
            self.cyk_service_mock,
            self.environment_mock,
            self.rule_population_mock,
            selected_detector.coordinates[:2])

        # Then:
        assert_that(result, is_(Production(
            selected_detector,
            Rule(Symbol(hash('S')), Symbol(hash('A')), Symbol(hash('B'))))))
        self.environment_mock.get_detector_symbols.assert_called_once_with(
            selected_detector.coordinates)


class TestCoverageOperations(CoverageOperatorTestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = CoverageOperations()

        self.create_operators_mock()
        self.sut.operators = self.all_operators

    def create_operator_mock(self, coverage_type):
        operator_mock = create_autospec(CoverageOperator)
        operator_mock.configure_mock(coverage_type=coverage_type)
        operator_mock.cover.return_value = EmptyProduction(Detector(self.coordinates))
        return operator_mock

    def create_operators_mock(self):
        self.terminal_operator_1 = self.create_operator_mock(CoverageType.unknown_terminal_symbol)
        self.terminal_operator_2 = self.create_operator_mock(CoverageType.unknown_terminal_symbol)

        self.effector_operator_1 = self.create_operator_mock(CoverageType.no_effector_found)
        self.effector_operator_2 = self.create_operator_mock(CoverageType.no_effector_found)

        self.starting_operator_1 = self.create_operator_mock(CoverageType.no_starting_symbol)
        self.starting_operator_2 = self.create_operator_mock(CoverageType.no_starting_symbol)

        self.terminal_operators = [self.terminal_operator_1, self.terminal_operator_2]
        self.effector_operators = [self.effector_operator_1, self.effector_operator_2]
        self.starting_operators = [self.starting_operator_1, self.starting_operator_2]

        self.all_operators = self.terminal_operators + \
                             self.effector_operators + \
                             self.starting_operators
        shuffle(self.all_operators)

    def clean_all_calls(self):
        for operator in self.all_operators:
            operator.reset_mock()

    def assert_called_times(self, *operator_call_pairs):
        for pair in operator_call_pairs:
            assert_that(pair[0].cover.call_count, is_(equal_to(pair[1])))

        self.clean_all_calls()

    def test_only_operators_of_given_type_should_be_called(self):
        self.sut.perform_coverage(
            self.cyk_service_mock,
            CoverageType.unknown_terminal_symbol,
            self.environment_mock,
            self.rule_population_mock,
            self.coordinates)

        self.assert_called_times(
            (self.terminal_operator_1, 1),
            (self.terminal_operator_2, 1),
            (self.effector_operator_1, 0),
            (self.effector_operator_2, 0),
            (self.starting_operator_1, 0),
            (self.starting_operator_2, 0)
        )

        self.sut.perform_coverage(
            self.cyk_service_mock,
            CoverageType.no_effector_found,
            self.environment_mock,
            self.rule_population_mock,
            self.coordinates)

        self.assert_called_times(
            (self.terminal_operator_1, 0),
            (self.terminal_operator_2, 0),
            (self.effector_operator_1, 1),
            (self.effector_operator_2, 1),
            (self.starting_operator_1, 0),
            (self.starting_operator_2, 0)
        )

        self.sut.perform_coverage(
            self.cyk_service_mock,
            CoverageType.no_starting_symbol,
            self.environment_mock,
            self.rule_population_mock,
            self.coordinates)

        self.assert_called_times(
            (self.terminal_operator_1, 0),
            (self.terminal_operator_2, 0),
            (self.effector_operator_1, 0),
            (self.effector_operator_2, 0),
            (self.starting_operator_1, 1),
            (self.starting_operator_2, 1)
        )

        assert_that(self.rule_population_mock.add_rule.called, is_(False))
        assert_that(self.environment_mock.add_production.called, is_(False))

        expected_rule = TerminalRule(Symbol(hash('A')), Symbol(hash('a')))
        expected_production = Production(Detector(self.coordinates), expected_rule)
        self.terminal_operator_1.cover.return_value = expected_production

        self.sut.perform_coverage(
            self.cyk_service_mock,
            CoverageType.unknown_terminal_symbol,
            self.environment_mock,
            self.rule_population_mock,
            self.coordinates)

        self.rule_population_mock.add_rule.assert_called_once_with(expected_rule)
        self.environment_mock.add_production.assert_called_once_with(expected_production)
        self.cyk_service_mock.statistics.on_added_new_rule.assert_called_once_with(expected_rule)
