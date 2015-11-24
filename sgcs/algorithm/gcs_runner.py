import sys

import time

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
            should_run_evolution=True
        )

        return configuration

    @staticmethod
    def create(induction_configuration, evolution_configuration, rule_configuration,
               max_algorithm_steps, should_run_evolution):
        configuration = AlgorithmConfiguration()
        configuration.induction = induction_configuration
        configuration.evolution = evolution_configuration
        configuration.rule = rule_configuration
        configuration.max_algorithm_steps = max_algorithm_steps
        configuration.should_run_evolution = should_run_evolution
        return configuration

    def __init__(self):
        self.induction = None
        self.evolution = None
        self.rule = None
        self.max_algorithm_steps = None
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


class LoopStopCriteria(object):
    def __init__(self, max_evolution_steps):
        self.max_evolution_steps = max_evolution_steps
        self.current_step = 0
        self.start_time = time.clock()

    def __call__(self, *args, **kwargs):
        print('current step:', self.current_step)
        self.current_step += 1
        return self.current_step > self.max_evolution_steps or time.clock() - self.start_time > 900


class GcsRunner(object):
    def __init__(self, configuration, randomizer):
        self.configuration = configuration
        self.rule_adding = AddingRuleSupervisor.default(randomizer)
        self.rule_adding.configuration = self.configuration.rule.adding
        self.grammar_statistics = GrammarStatistics.default(randomizer)
        self.induction = CykService.default(self.configuration.induction, randomizer,
                                            self.rule_adding, self.grammar_statistics)
        self.evolution = EvolutionService(self.configuration.evolution, randomizer)
        self.stop_criteria_creator = LoopStopCriteria

    def add_initial_rules(self, initial_rules):
        for rule in initial_rules:
            self.grammar_statistics.on_added_new_rule(rule)

    def perform_gcs(self, initial_rules, symbol_translator):
        self.add_initial_rules(initial_rules)
        rule_population = RulePopulation(
            self.configuration.rule.starting_symbol, self.configuration.rule.universal_symbol,
            max_non_terminal_symbols=self.configuration.rule.max_non_terminal_symbols)
        stop_criteria = self.stop_criteria_creator(self.configuration.max_algorithm_steps)
        while not stop_criteria():
            sentences = symbol_translator.get_sentences()
            evolution_step_estimator = EvolutionStepEstimator()
            self.induction.perform_cyk_for_all_sentences(rule_population, sentences,
                                                         evolution_step_estimator)
            # Calculate Fg
            if self.configuration.should_run_evolution:
                self.evolution.run_genetic_algorithm(self.grammar_statistics, rule_population,
                                                     self.rule_adding)
            print('rule_statistics size:', len(self.grammar_statistics.rule_statistics._rule_info))
            # print('rule_population size:', sys.getsizeof(rule_population.all_non_terminal_rules))

        return rule_population
