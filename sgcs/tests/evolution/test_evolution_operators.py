import unittest
from unittest.mock import MagicMock, create_autospec, call
from hamcrest import *

from core.rule import Rule
from core.symbol import Symbol
from evolution.evolution_configuration import EvolutionConfiguration, \
    EvolutionOperatorsConfiguration, EvolutionOperatorConfiguration
from evolution.evolution_operators import InversionOperator, InvalidArityException
from evolution.evolution_service import EvolutionService
from utils import Randomizer


class TestOperatorCommon(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.randomizer_mock = create_autospec(Randomizer)

        self.configuration = EvolutionConfiguration()
        self.configuration.operators = EvolutionOperatorsConfiguration()

        self.configuration.operators.inversion = EvolutionOperatorConfiguration()
        self.configuration.operators.inversion.chance = 0.5

        self.service_mock = create_autospec(EvolutionService)
        self.service_mock.configure_mock(randomizer=self.randomizer_mock,
                                         configuration=self.configuration)

        self.sut = None

    def operator_executes_with_some_chance_scenario(self, chance):
        # Given:
        rule = Rule(Symbol('A'), Symbol('B'), Symbol('C'))
        self.randomizer_mock.perform_with_chance.side_effect = [False, True]

        # When/Then:
        rule_new, = self.sut.apply(self.service_mock, rule)
        assert_that(rule_new, is_(equal_to(rule)))

        rule_new, = self.sut.apply(self.service_mock, rule)
        assert_that(rule_new, is_not(equal_to(rule)))

        self.randomizer_mock.perform_with_chance.assert_has_calls([call(chance), call(chance)])

    def operator_raises_exception_on_invalid_arity_scenario(self, to_low, to_high):
        assert_that(calling(self.sut.apply).with_args(tuple(range(to_low + 1))),
                    raises(InvalidArityException))

        assert_that(calling(self.sut.apply).with_args((tuple(range(to_high + 1)))),
                    raises(InvalidArityException))


class TestInversion(TestOperatorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = InversionOperator()

    def test_inversion_should_behave_like_evolution_operator(self):
        self.operator_executes_with_some_chance_scenario(
            self.configuration.operators.inversion.chance)
        self.operator_raises_exception_on_invalid_arity_scenario(0, 2)

    def test_inversion_changes_order_of_right_side_of_the_rule(self):
        # Given:
        rule = Rule(Symbol('A'), Symbol('B'), Symbol('C'))
        self.randomizer_mock.perform_with_chance.return_value = True

        # When/Then:
        rule_new, = self.sut.apply(self.service_mock, rule)
        assert_that(rule_new, is_(equal_to(Rule(Symbol('A'), Symbol('C'), Symbol('B')))))

        self.randomizer_mock.perform_with_chance.assert_called_once_with(
            self.configuration.operators.inversion.chance)
