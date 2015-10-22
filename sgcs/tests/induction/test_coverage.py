from enum import Enum
import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.induction.coverage import TerminalCoverageOperator
from sgcs.induction.cyk_configuration import CykConfiguration, CoverageConfiguration, \
    CoverageOperators
from sgcs.induction.cyk_service import CykService
from sgcs.induction.environment import Environment
from sgcs.induction.rule import TerminalRule
from sgcs.induction.rule_population import RulePopulation
from sgcs.induction.symbol import Symbol
from sgcs.utils import Randomizer


class CykReasoningStatus(Enum):
    unknown_terminal_symbol = 0
    no_effector_found = 1
    no_starting_symbol = 2


class TestTerminalCoverageOperator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cyk_service_mock = create_autospec(CykService)

        self.cyk_configuration_mock = create_autospec(CykConfiguration)

        self.cyk_service_mock.randomizer = create_autospec(Randomizer)
        self.cyk_service_mock.configuration.return_value = self.cyk_configuration_mock

        self.sut = TerminalCoverageOperator(self.cyk_service_mock)

        self.environment_mock = create_autospec(Environment)
        self.environment_mock.get_sentence_symbol.return_value = Symbol(hash('a'))

        self.rule_population_mock = create_autospec(RulePopulation)
        self.rule_population_mock.get_random_terminal_symbol.return_value = Symbol(hash('A'))

        self.coordinates = 0, 2

    def test_operators_execute_with_some_chance(self):
        self.cyk_service_mock.randomizer.perform_with_chance.side_effect = [False, True]
        assert_that(
            self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates),
            is_(None))

        assert_that(
            self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates),
            is_not(None))

    def test_given_unknown_terminal_symbol_should_announce_terminal_rule_creation(self):
        result = self.sut.cover(self.environment_mock, self.rule_population_mock, self.coordinates)
        assert_that(
            result,
            is_(equal_to(TerminalRule(Symbol(hash('A')), Symbol(hash('a'))))))
