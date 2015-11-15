import unittest
from itertools import count
from unittest.mock import MagicMock, create_autospec, call
from hamcrest import *

from core.rule import Rule
from core.rule_population import RulePopulation
from core.symbol import Symbol
from evolution.evolution_configuration import EvolutionConfiguration, \
    EvolutionOperatorsConfiguration, EvolutionOperatorConfiguration
from evolution.evolution_operators import InversionOperator, InvalidArityException, ParentMutationOperator, \
    LeftChildMutationOperator, RightChildMutationOperator, CrossoverOperator
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

        self.configuration.operators.mutation = EvolutionOperatorConfiguration()
        self.configuration.operators.mutation.chance = 0.2

        self.configuration.operators.crossover = EvolutionOperatorConfiguration()
        self.configuration.operators.crossover.chance = 0.3

        self.rule_population_mock = create_autospec(RulePopulation)

        self.service_mock = create_autospec(EvolutionService)
        self.service_mock.configure_mock(randomizer=self.randomizer_mock,
                                         configuration=self.configuration)

        self.rule_1 = Rule(Symbol('A'), Symbol('B'), Symbol('C'))
        self.rule_2 = Rule(Symbol('D'), Symbol('E'), Symbol('F'))

        self.sut = None

    def operator_executes_with_some_chance_scenario(self, chance, rules):
        # Given:
        self.randomizer_mock.perform_with_chance.side_effect = \
            (False if i == 0 else True for i in count())

        # When/Then:
        rule_new = self.sut.apply(self.service_mock, self.rule_population_mock, *rules)
        assert_that(rule_new, only_contains(*rules))

        rule_new = self.sut.apply(self.service_mock, self.rule_population_mock, *rules)
        assert_that(rule_new, is_not(has_items(*rules)))

    def operator_raises_exception_on_invalid_arity_scenario(self, to_low, to_high):
        assert_that(calling(self.sut.apply).with_args(*tuple(range(to_low + 2))),
                    raises(InvalidArityException))

        assert_that(calling(self.sut.apply).with_args(*(tuple(range(to_high + 2)))),
                    raises(InvalidArityException))


class TestInversion(TestOperatorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = InversionOperator()

    def test_inversion_should_behave_like_evolution_operator(self):
        self.operator_executes_with_some_chance_scenario(
            self.configuration.operators.inversion.chance, [self.rule_1])
        self.operator_raises_exception_on_invalid_arity_scenario(0, 2)

    def test_inversion_changes_order_of_right_side_of_the_rule(self):
        # Given:
        self.randomizer_mock.perform_with_chance.return_value = True

        # When/Then:
        rule_new, = self.sut.apply(self.service_mock, self.rule_population_mock, self.rule_1)
        assert_that(rule_new, is_(equal_to(Rule(Symbol('A'), Symbol('C'), Symbol('B')))))

        self.randomizer_mock.perform_with_chance.assert_called_once_with(
            self.configuration.operators.inversion.chance)


class TestMutation(TestOperatorCommon):
    def mutation_behaviour_scenario(self):
        self.rule_population_mock.get_random_non_terminal_symbol.return_value = Symbol('Q')
        self.operator_executes_with_some_chance_scenario(
            self.configuration.operators.mutation.chance, [self.rule_1])
        self.operator_raises_exception_on_invalid_arity_scenario(0, 2)

    def mutation_change_scenario(self, expected_result):
        # Given:
        self.randomizer_mock.perform_with_chance.return_value = True
        self.rule_population_mock.get_random_non_terminal_symbol.return_value = Symbol('Q')

        # When/Then:
        rule_new, = self.sut.apply(self.service_mock, self.rule_population_mock, self.rule_1)
        assert_that(rule_new, is_(equal_to(expected_result)))

        self.randomizer_mock.perform_with_chance.assert_has_calls([
            call(self.configuration.operators.mutation.chance),
            call(self.configuration.operators.mutation.chance)
        ])
        self.rule_population_mock.get_random_non_terminal_symbol.assert_has_calls([
            call(self.randomizer_mock)
        ])


class TestParentMutation(TestMutation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = ParentMutationOperator()

    def test_parent_mutation_should_behave_like_evolution_operator(self):
        self.mutation_behaviour_scenario()

    def test_parent_mutation_changes_parent(self):
        self.mutation_change_scenario(Rule(Symbol('Q'), Symbol('B'), Symbol('C')))


class TestLeftChildMutation(TestMutation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = LeftChildMutationOperator()

    def test_left_child_mutation_should_behave_like_evolution_operator(self):
        self.mutation_behaviour_scenario()

    def test_left_child_mutation_changes_left_child(self):
        self.mutation_change_scenario(Rule(Symbol('A'), Symbol('Q'), Symbol('C')))


class TestRightChildMutation(TestMutation):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = RightChildMutationOperator()

    def test_right_child_mutation_should_behave_like_evolution_operator(self):
        self.mutation_behaviour_scenario()

    def test_right_child_mutation_changes_right_child(self):
        self.mutation_change_scenario(Rule(Symbol('A'), Symbol('B'), Symbol('Q')))


class TestCrossover(TestOperatorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = CrossoverOperator()

    def test_crossover_should_behave_like_evolution_operator(self):
        self.operator_executes_with_some_chance_scenario(
            self.configuration.operators.inversion.chance, [self.rule_1, self.rule_2])
        self.operator_raises_exception_on_invalid_arity_scenario(1, 3)

    def test_crossover_mixes_two_given_rules_into_two_new_ones(self):
        # Given:
        self.randomizer_mock.perform_with_chance.return_value = True

        # When/Then:
        rule_1_new, rule_2_new = self.sut.apply(self.service_mock, self.rule_population_mock,
                                                self.rule_1, self.rule_2)
        assert_that(rule_1_new, is_(equal_to(Rule(Symbol('D'), Symbol('E'), Symbol('C')))))
        assert_that(rule_2_new, is_(equal_to(Rule(Symbol('A'), Symbol('B'), Symbol('F')))))

        self.randomizer_mock.perform_with_chance.assert_has_calls([
            call(self.configuration.operators.crossover.chance),
            call(0.5)
        ])

    def test_crossover_mixes_two_given_rules_into_two_new_ones_another_combination(self):
        # Given:
        self.randomizer_mock.perform_with_chance.side_effect = [True, False]

        # When/Then:
        rule_1_new, rule_2_new = self.sut.apply(self.service_mock, self.rule_population_mock,
                                                self.rule_1, self.rule_2)
        assert_that(rule_1_new, is_(equal_to(Rule(Symbol('D'), Symbol('B'), Symbol('F')))))
        assert_that(rule_2_new, is_(equal_to(Rule(Symbol('A'), Symbol('E'), Symbol('C')))))

        self.randomizer_mock.perform_with_chance.assert_has_calls([
            call(self.configuration.operators.crossover.chance),
            call(0.5)
        ])
