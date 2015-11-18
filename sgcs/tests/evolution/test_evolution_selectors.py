import unittest
from unittest.mock import MagicMock, create_autospec, call
from hamcrest import *

from core.rule import Rule
from core.rule_population import RulePopulation
from core.symbol import Symbol
from evolution.evolution_configuration import EvolutionConfiguration, \
    EvolutionTournamentSelectorConfiguration
from evolution.evolution_selectors import RandomSelector, TournamentSelector, RouletteSelector
from evolution.evolution_service import EvolutionService
from sgcs.statistics.grammar_statistics import GrammarStatistics, Fitness
from utils import Randomizer


class TestSelectorCommon(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configuration = EvolutionConfiguration()

        self.randomizer_mock = create_autospec(Randomizer)

        self.service_mock = create_autospec(EvolutionService)
        self.service_mock.configure_mock(randomizer=self.randomizer_mock,
                                         configuration=self.configuration)

        self.fitness_mock = create_autospec(Fitness)
        self.fitness_mock.get_keyfunc_getter.return_value = self.fitness_dummy_keyfunc

        self.grammar_statistics_mock = create_autospec(GrammarStatistics)
        self.grammar_statistics_mock.configure_mock(fitness=self.fitness_mock)

        self.rule_population_mock = create_autospec(RulePopulation)

        self.expected_rule = Rule(Symbol('A'), Symbol('B'), Symbol('C'))
        self.rule_2 = Rule(Symbol('D'), Symbol('E'), Symbol('F'))
        self.rule_3 = Rule(Symbol('G'), Symbol('H'), Symbol('I'))

        self.sut = None

    def fitness_dummy_keyfunc(self, rule):
        if rule == self.expected_rule:
            return 5
        elif rule == self.rule_2:
            return 1
        else:
            return 2


class TestRandomSelector(TestSelectorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = RandomSelector()

    def test_random_selection_should_work(self):
        # Given:
        self.rule_population_mock.get_random_rules.return_value = [self.expected_rule]

        # When:
        selected_rule = self.sut.select(
            self.service_mock, self.grammar_statistics_mock, self.rule_population_mock)

        # Then:
        assert_that(selected_rule, is_(equal_to(self.expected_rule)))
        self.rule_population_mock.get_random_rules.assert_called_once_with(
            self.randomizer_mock, False, 1)


class TestTournamentSelector(TestSelectorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tournament_size = 3

        tournament_selector_configuration = EvolutionTournamentSelectorConfiguration()
        self.configuration.selectors.append(tournament_selector_configuration)
        tournament_selector_configuration.tournament_size = self.tournament_size

        self.sut = TournamentSelector()

    def test_tournament_selection_should_work(self):
        # Given:
        self.rule_population_mock.get_random_rules.return_value = [
            self.expected_rule, self.rule_2, self.rule_3]

        # When:
        selected_rule = self.sut.select(
            self.service_mock, self.grammar_statistics_mock, self.rule_population_mock)

        # Then:
        assert_that(selected_rule, is_(equal_to(self.expected_rule)))
        self.rule_population_mock.get_random_rules.assert_called_once_with(
            self.randomizer_mock, False, self.tournament_size)
        self.fitness_mock.get_keyfunc_getter.assert_called_once_with(self.grammar_statistics_mock)


class TestRouletteSelector(TestSelectorCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = RouletteSelector()

    def test_roulette_selection_should_work(self):
        # Given:
        self.rule_population_mock.get_all_non_terminal_rules.return_value = [
            self.expected_rule, self.rule_2, self.rule_3]
        self.randomizer_mock.uniform.return_value = 2.22

        # When:
        selected_rule = self.sut.select(
            self.service_mock, self.grammar_statistics_mock, self.rule_population_mock)

        # Then:
        assert_that(selected_rule, is_(equal_to(self.expected_rule)))
        self.rule_population_mock.get_all_non_terminal_rules.assert_called_once_with()
        self.fitness_mock.get_keyfunc_getter.assert_called_once_with(self.grammar_statistics_mock)
        self.randomizer_mock.uniform.assert_called_once_with(0, 8)
