import time
from abc import ABCMeta, abstractmethod

from core.rule_population import RulePopulation
from core.symbol import Symbol
from evolution.evolution_configuration import EvolutionConfiguration
from evolution.evolution_service import EvolutionService
from grammar_estimator import EvolutionStepEstimator
from induction.cyk_configuration import CykConfiguration
from induction.cyk_service import CykService
from rule_adding import AddingRulesConfiguration, AddingRuleSupervisor
from statistics.grammar_statistics import GrammarStatistics


class AlgorithmConfiguration(object):
    @staticmethod
    def default():
        ga_selectors_configuration = []
        evolution_configuration = EvolutionConfiguration.create(
            selectors=ga_selectors_configuration,
            inversion_chance=0,
            mutation_chance=0,
            crossover_chance=0
        )

        induction_configuration = CykConfiguration.create(
            should_correct_grammar=False,
            terminal_chance=0,
            universal_chance=0,
            aggressive_chance=0,
            starting_chance=0,
            full_chance=0
        )

        rule_configuration = RuleConfiguration.create(
            crowding_factor=0,
            crowding_size=0,
            elitism_size=0,
            starting_symbol=1,
            universal_symbol=None,
            max_non_terminal_symbols=32
        )

        configuration = AlgorithmConfiguration.create(
            induction_configuration, evolution_configuration, rule_configuration,
            max_algorithm_steps=1,
            should_run_evolution=True,
            max_execution_time=900,
            satisfying_fitness=1
        )

        return configuration

    @staticmethod
    def create(induction_configuration, evolution_configuration, rule_configuration,
               max_algorithm_steps, should_run_evolution, max_execution_time, satisfying_fitness):
        configuration = AlgorithmConfiguration()
        configuration.induction = induction_configuration
        configuration.evolution = evolution_configuration
        configuration.rule = rule_configuration
        configuration.max_algorithm_steps = max_algorithm_steps
        configuration.max_execution_time = max_execution_time
        configuration.satisfying_fitness = satisfying_fitness
        configuration.should_run_evolution = should_run_evolution
        return configuration

    def __init__(self):
        self.induction = None
        self.evolution = None
        self.rule = None
        self.max_algorithm_steps = None
        self.max_execution_time = None
        self.satisfying_fitness = None
        self.should_run_evolution = None


class RuleConfiguration(object):
    @staticmethod
    def create(crowding_factor, crowding_size, elitism_size, starting_symbol, universal_symbol,
               max_non_terminal_symbols):
        configuration = RuleConfiguration()
        configuration.adding = AddingRulesConfiguration.create(
            crowding_factor, crowding_size, elitism_size)
        configuration.starting_symbol = Symbol(starting_symbol)
        configuration.universal_symbol = Symbol(universal_symbol) if universal_symbol else None
        configuration.max_non_terminal_symbols = max_non_terminal_symbols
        return configuration

    def __init__(self):
        self.adding = None
        self.starting_symbol = None
        self.universal_symbol = None
        self.max_non_terminal_symbols = None


class StopCriteria(metaclass=ABCMeta):
    def __call__(self, *args, **kwargs):
        self.update_state()
        return self.has_been_fulfilled()

    @abstractmethod
    def has_been_fulfilled(self):
        pass

    def update_state(self):
        pass

    @abstractmethod
    def stop_reasoning_message(self):
        return "Reasoning stopped. Cause: "


class NoStopCriteriaSpecifiedError(Exception):
    pass


class NoStopCriteriaSpecified(StopCriteria):
    def has_been_fulfilled(self):
        raise NoStopCriteriaSpecifiedError()

    def stop_reasoning_message(self):
        pass


class StepStopCriteria(StopCriteria):
    def __init__(self, configuration):
        self.configuration = configuration
        self.current_step = 0

    def update_state(self):
        self.current_step += 1

    def has_been_fulfilled(self):
        return self.current_step > self.configuration.max_algorithm_steps

    def stop_reasoning_message(self):
        return super().stop_reasoning_message() + \
                'evolution step {0} reached'.format(self.current_step)


class TimeStopCriteria(StopCriteria):
    def __init__(self, configuration):
        self.configuration = configuration
        self.start_time = time.clock()

    def has_been_fulfilled(self):
        return time.clock() - self.start_time > self.configuration.max_execution_time

    def stop_reasoning_message(self):
        return super().stop_reasoning_message() + \
            'execution time of {0} s exceeded'.format(time.clock() - self.start_time)


class FitnessStopCriteria(StopCriteria):
    def __init__(self, grammar_estimator, configuration):
        self.grammar_estimator = grammar_estimator
        self.configuration = configuration

    def has_been_fulfilled(self):
        return self.grammar_estimator['fitness'].get_global_max() >= \
               self.configuration.satisfying_fitness

    def stop_reasoning_message(self):
        return super().stop_reasoning_message() + \
            'fitness {0}% reached'.format(self.grammar_estimator['fitness'].get_global_max() * 100)


class GcsRunner(object):
    def __init__(self, randomizer):
        self.configuration = None
        self.rule_adding = AddingRuleSupervisor.default(randomizer)
        self.grammar_estimator = None
        self.induction = CykService.default(randomizer, self.rule_adding)
        self.evolution = EvolutionService(randomizer)
        self.stop_criteria = [NoStopCriteriaSpecified()]

    def create_stop_criteria(self):
        self.stop_criteria = [
                                 FitnessStopCriteria(self.grammar_estimator, self.configuration),
                                 StepStopCriteria(self.configuration),
                                 TimeStopCriteria(self.configuration)
                             ]

    @staticmethod
    def add_initial_rules(initial_rules, rule_population, grammar_statistics):
        for rule in initial_rules:
            rule_population.add_rule(rule)
            grammar_statistics.on_added_new_rule(rule)

    def perform_gcs(self, initial_rules, symbol_translator, configuration, grammar_estimator,
                    grammar_statistics):
        self.configuration = configuration
        self.rule_adding.configuration = self.configuration.rule.adding
        self.grammar_estimator = grammar_estimator
        self.create_stop_criteria()

        rule_population = RulePopulation(
            self.configuration.rule.starting_symbol, self.configuration.rule.universal_symbol,
            max_non_terminal_symbols=self.configuration.rule.max_non_terminal_symbols)

        self.add_initial_rules(initial_rules, rule_population, grammar_statistics)

        evolution_step = 0
        while not any(cr() for cr in self.stop_criteria):
            sentences = symbol_translator.get_sentences()
            evolution_step_estimator = EvolutionStepEstimator()
            self.induction.perform_cyk_for_all_sentences(rule_population, sentences,
                                                         evolution_step_estimator,
                                                         self.configuration.induction,
                                                         grammar_statistics)

            self.grammar_estimator.append_step_estimation(evolution_step, evolution_step_estimator)

            if self.configuration.should_run_evolution:
                self.evolution.run_genetic_algorithm(grammar_statistics, rule_population,
                                                     self.rule_adding, self.configuration.evolution)

            evolution_step += 1

        stop_reasoning = next(cr for cr in self.stop_criteria if cr.has_been_fulfilled())
        fitness_reached = self.grammar_estimator['fitness'].get_global_max()

        return rule_population, stop_reasoning, fitness_reached
