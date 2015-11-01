from abc import abstractmethod, ABCMeta
from enum import Enum
from sgcs.induction.detector import Detector
from sgcs.induction.production import Production, EmptyProduction
from sgcs.induction.rule import TerminalRule, Rule


class CoverageType(Enum):
    unknown_terminal_symbol = 0
    no_effector_found = 1
    no_starting_symbol = 2


class CoverageOperations(object):
    def __init__(self):
        self.operators = []

    def perform_coverage(self, coverage_type, environment, rule_population, coordinates):
        for operator in self.operators:
            if operator.coverage_type == coverage_type:
                production = operator.cover(environment, rule_population, coordinates)
                if not production.is_empty():
                    rule_population.add_rule(production.rule)
                    environment.add_production(production)


class CoverageOperator(object, metaclass=ABCMeta):
    @staticmethod
    def empty_production(coordinates):
        return EmptyProduction(Detector(coordinates))

    @staticmethod
    def production(coordinates, rule):
        return Production(Detector(coordinates), rule)

    def __init__(self, cyk_service, chance, coverage_type):
        self.cyk_service = cyk_service
        self.chance = chance
        self._coverage_type = coverage_type

    @property
    def coverage_type(self):
        return self._coverage_type

    def cover(self, environment, rule_population, coordinates):
        if self.cyk_service.randomizer.perform_with_chance(self.chance):
            return self.cover_impl(environment, rule_population, coordinates)

        return self.empty_production(coordinates)

    @abstractmethod
    def cover_impl(self, environment, rule_population, coordinates):
        pass


class TerminalCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.terminal.chance,
                         CoverageType.unknown_terminal_symbol)

    def cover_impl(self, environment, rule_population, coordinates):
        parent = rule_population.get_random_non_terminal_symbol(self.cyk_service.randomizer)
        return self.production(
            coordinates,
            TerminalRule(parent, environment.get_sentence_symbol(coordinates[1])))


class UniversalCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.universal.chance,
                         CoverageType.unknown_terminal_symbol)

    def cover_impl(self, environment, rule_population, coordinates):
        child = environment.get_sentence_symbol(coordinates[1])
        return self.production(
            coordinates,
            TerminalRule(rule_population.universal_symbol, child))


class StartingCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.starting.chance,
                         CoverageType.no_starting_symbol)

    def cover_impl(self, environment, rule_population, coordinates):
        if environment.get_sentence_length() == 1 and environment.is_sentence_positive():
            only_symbol = environment.get_sentence_symbol(0)
            return self.production(
                coordinates,
                TerminalRule(rule_population.starting_symbol, only_symbol))
        else:
            return self.empty_production(coordinates)


class AggressiveCoverageOperator(CoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service,
                         cyk_service.configuration.coverage.operators.aggressive.chance,
                         CoverageType.no_effector_found)

    def select_detector(self, environment, rule_population, coordinates):
        unsatisfied_detectors = environment.get_unsatisfied_detectors(coordinates)
        return self.cyk_service.randomizer.choice(unsatisfied_detectors)

    def select_parent(self, rule_population):
        return rule_population.get_random_non_terminal_symbol(self.cyk_service.randomizer)

    def cover_impl(self, environment, rule_population, coordinates):
        if environment.is_sentence_positive():
            selected_detector = self.select_detector(environment, rule_population, coordinates)

            children = environment.get_detector_symbols(selected_detector.coordinates)

            parent = self.select_parent(rule_population)
            return Production(
                selected_detector,
                Rule(parent, *children))
        else:
            return self.empty_production(coordinates)


# noinspection PyAbstractClass
class FullCoverageOperator(AggressiveCoverageOperator):
    def __init__(self, cyk_service):
        super().__init__(cyk_service)
        self.chance = cyk_service.configuration.coverage.operators.full.chance
        self._coverage_type = CoverageType.no_starting_symbol

    def select_parent(self, rule_population):
        return rule_population.starting_symbol
