from abc import abstractmethod, ABCMeta
from enum import Enum

from core.rule import TerminalRule, Rule
from rule_adding import AddingRuleStrategyHint
from sgcs.induction.cyk_configuration import InvalidCykConfigurationError
from sgcs.induction.detector import Detector
from sgcs.induction.production import Production, EmptyProduction


class CoverageType(object):
    unknown_terminal_symbol = 0
    no_effector_found = 1
    no_starting_symbol = 2


class CoverageOperations(object):
    @staticmethod
    def create_default_set():
        coverage_operations = CoverageOperations()
        coverage_operations.operators = [
            TerminalCoverageOperator(),
            UniversalCoverageOperator(),
            AggressiveCoverageOperator(),
            StartingCoverageOperator(),
            FullCoverageOperator()
        ]

        return coverage_operations

    def __init__(self):
        self.operators = []

    def perform_coverage(self, cyk_service, coverage_type, environment, rule_population, coordinates):
        for operator in self.operators:
            if operator.coverage_type == coverage_type:
                production = operator.cover(cyk_service, environment, rule_population, coordinates)
                if not production.is_empty():
                    # rule_population.add_rule(production.rule)
                    # cyk_service.statistics.on_added_new_rule(production.rule)
                    cyk_service.rule_adding.add_rule(production.rule, rule_population,
                                                     cyk_service.statistics,
                                                     operator.adding_rule_strategy_type(
                                                         cyk_service))
                    environment.add_production(production)


class CoverageOperator(object, metaclass=ABCMeta):
    @staticmethod
    def empty_production(coordinates):
        return EmptyProduction(Detector(coordinates))

    @staticmethod
    def production(coordinates, rule):
        return Production(Detector(coordinates), rule)

    def __init__(self, coverage_type,
                 adding_rule_strategy_type=AddingRuleStrategyHint.expand_population):
        self._coverage_type = coverage_type
        self._adding_rule_strategy_type = adding_rule_strategy_type

    @property
    def coverage_type(self):
        return self._coverage_type

    def adding_rule_strategy_type(self, cyk_service):
        custom_strategy = self.get_custom_adding_strategy(cyk_service)
        return self._adding_rule_strategy_type if custom_strategy is None else custom_strategy

    def cover(self, cyk_service, environment, rule_population, coordinates):
        if cyk_service.randomizer.perform_with_chance(self.get_chance(cyk_service)):
            return self.cover_impl(cyk_service, environment, rule_population, coordinates)

        return self.empty_production(coordinates)

    @abstractmethod
    def cover_impl(self, cyk_service, environment, rule_population, coordinates):
        pass

    @abstractmethod
    def get_chance(self, cyk_service):
        pass

    @abstractmethod
    def get_custom_adding_strategy(self, cyk_service):
        pass


class TerminalCoverageOperator(CoverageOperator):
    def __init__(self):
        super().__init__(CoverageType.unknown_terminal_symbol)

    def get_custom_adding_strategy(self, cyk_service):
        return cyk_service.configuration.coverage.operators.terminal.adding_hint

    def cover_impl(self, cyk_service, environment, rule_population, coordinates):
        parent = rule_population.get_random_non_terminal_symbol(cyk_service.randomizer)
        return self.production(
            coordinates,
            TerminalRule(parent, environment.get_sentence_symbol(coordinates[1])))

    def get_chance(self, cyk_service):
        return cyk_service.configuration.coverage.operators.terminal.chance


class UniversalCoverageOperator(CoverageOperator):
    def __init__(self):
        super().__init__(CoverageType.unknown_terminal_symbol)

    def get_custom_adding_strategy(self, cyk_service):
        return cyk_service.configuration.coverage.operators.universal.adding_hint

    def cover_impl(self, cyk_service, environment, rule_population, coordinates):
        child = environment.get_sentence_symbol(coordinates[1])

        if rule_population.universal_symbol is None:
            raise InvalidCykConfigurationError(
                'Universal symbol coverage triggered;' +
                ' yet universal_symbol unset in rule_population')

        return self.production(
            coordinates,
            TerminalRule(rule_population.universal_symbol, child))

    def get_chance(self, cyk_service):
        return cyk_service.configuration.coverage.operators.universal.chance


class StartingCoverageOperator(CoverageOperator):
    def __init__(self):
        super().__init__(CoverageType.no_starting_symbol,
                         AddingRuleStrategyHint.control_population_size)

    def get_custom_adding_strategy(self, cyk_service):
        return cyk_service.configuration.coverage.operators.starting.adding_hint

    def cover_impl(self, cyk_service, environment, rule_population, coordinates):
        if environment.get_sentence_length() == 1 and environment.is_sentence_positive():
            only_symbol = environment.get_sentence_symbol(0)
            return self.production(
                coordinates,
                TerminalRule(rule_population.starting_symbol, only_symbol))
        else:
            return self.empty_production(coordinates)

    def get_chance(self, cyk_service):
        return cyk_service.configuration.coverage.operators.starting.chance


class AggressiveCoverageOperator(CoverageOperator):
    def __init__(self):
        super().__init__(CoverageType.no_effector_found,
                         AddingRuleStrategyHint.control_population_size)

    def get_custom_adding_strategy(self, cyk_service):
        return cyk_service.configuration.coverage.operators.aggressive.adding_hint

    @staticmethod
    def _select_detector(cyk_service, environment, rule_population, coordinates):
        unsatisfied_detectors = environment.get_unsatisfied_detectors(coordinates)
        return cyk_service.randomizer.choice(unsatisfied_detectors) if unsatisfied_detectors \
            else None

    def _select_parent(self, cyk_service, rule_population):
        return rule_population.get_random_non_terminal_symbol(cyk_service.randomizer)

    def cover_impl(self, cyk_service, environment, rule_population, coordinates):
        if environment.is_sentence_positive():
            selected_detector = self._select_detector(
                cyk_service, environment, rule_population, coordinates)

            if selected_detector:
                children = environment.get_detector_symbols(selected_detector.coordinates)

                parent = self._select_parent(cyk_service, rule_population)
                return Production(
                    selected_detector,
                    Rule(parent, *children))

        return self.empty_production(coordinates)

    def get_chance(self, cyk_service):
        return cyk_service.configuration.coverage.operators.aggressive.chance


# noinspection PyAbstractClass
class FullCoverageOperator(AggressiveCoverageOperator):
    def __init__(self):
        super().__init__()
        self._coverage_type = CoverageType.no_starting_symbol

    def get_custom_adding_strategy(self, cyk_service):
        return cyk_service.configuration.coverage.operators.full.adding_hint

    def _select_parent(self, cyk_service, rule_population):
        return rule_population.starting_symbol

    def get_chance(self, cyk_service):
        return cyk_service.configuration.coverage.operators.full.chance
