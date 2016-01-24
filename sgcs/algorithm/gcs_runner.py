import time
from abc import ABCMeta, abstractmethod

from core.rule import Rule
from core.rule_population import RulePopulation, StochasticRulePopulation
from core.symbol import Symbol
from datalayer.jsonizer import SimpleJsonNode
from evolution.evolution_configuration import EvolutionConfiguration
from evolution.evolution_service import EvolutionService
from grammar_estimator import EvolutionStepEstimator
from induction.cyk_configuration import CykConfiguration
from induction.cyk_service import CykService, StochasticCykService
from rule_adding import AddingRulesConfiguration, AddingRuleSupervisor
from statistics.grammar_statistics import GrammarStatistics, ClassicalStatisticsConfiguration, \
    PasiekaStatisticsConfiguration


class AlgorithmVariant(object):
    gcs = 'GCS'
    sgcs = 'sGCS'


class AlgorithmConfiguration(SimpleJsonNode):
    @staticmethod
    def common_configuration(statistics_configuration, algorithm_variant):
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
            max_non_terminal_symbols=32,
            random_starting_population_size=20,
            max_non_terminal_rules=40
        )

        configuration = AlgorithmConfiguration.create(
            induction_configuration, evolution_configuration, rule_configuration,
            max_algorithm_steps=1,
            should_run_evolution=True,
            max_execution_time=900,
            satisfying_fitness=1,
            statistics=statistics_configuration,
            max_algorithm_runs=50,
            algorithm_variant=algorithm_variant
        )

        return configuration

    @staticmethod
    def default():
        return AlgorithmConfiguration.common_configuration(
            ClassicalStatisticsConfiguration.default(), AlgorithmVariant.gcs)

    @staticmethod
    def sgcs_variant():
        return AlgorithmConfiguration.common_configuration(
            PasiekaStatisticsConfiguration.default(), AlgorithmVariant.sgcs)

    @staticmethod
    def create(induction_configuration, evolution_configuration, rule_configuration,
               max_algorithm_steps, should_run_evolution, max_execution_time, satisfying_fitness,
               statistics, max_algorithm_runs, algorithm_variant):
        configuration = AlgorithmConfiguration()
        configuration.induction = induction_configuration
        configuration.evolution = evolution_configuration
        configuration.rule = rule_configuration
        configuration.max_algorithm_steps = max_algorithm_steps
        configuration.max_execution_time = max_execution_time
        configuration.satisfying_fitness = satisfying_fitness
        configuration.should_run_evolution = should_run_evolution
        configuration.statistics = statistics
        configuration.max_algorithm_runs = max_algorithm_runs
        configuration.algorithm_variant = algorithm_variant
        return configuration

    def __init__(self):
        self.induction = None
        self.evolution = None
        self.rule = None
        self.max_algorithm_steps = None
        self.max_execution_time = None
        self.satisfying_fitness = None
        self.should_run_evolution = None
        self.statistics = None
        self.max_algorithm_runs = None
        self.algorithm_variant = None


class CykServiceVariationManager(object):
    def __init__(self, is_stochastic):
        self.is_stochastic = is_stochastic

    def create_cyk_service(self, randomizer, adding_rule_supervisor):
        if self.is_stochastic:
            return StochasticCykService.default(randomizer, adding_rule_supervisor)
        else:
            return CykService.default(randomizer, adding_rule_supervisor)

    def create_rule_population(self, starting_symbol, universal_symbol=None, previous_instance=None,
                               max_non_terminal_symbols=32):
        if self.is_stochastic:
            return StochasticRulePopulation(starting_symbol, universal_symbol, previous_instance,
                                            max_non_terminal_symbols)
        else:
            return RulePopulation(starting_symbol, universal_symbol, previous_instance,
                                  max_non_terminal_symbols)

    def create_grammar_statistics(self, randomizer, statistics_configuration):
        if not statistics_configuration.negative_sentence_learning:
            return GrammarStatistics.sgcs_variant(randomizer, statistics_configuration)
        else:
            return GrammarStatistics.default(randomizer, statistics_configuration)

    def create_default_configuration(self):
        if self.is_stochastic:
            return AlgorithmConfiguration.sgcs_variant()
        else:
            return AlgorithmConfiguration.default()


class RuleConfiguration(SimpleJsonNode):
    @staticmethod
    def create(crowding_factor, crowding_size, elitism_size, starting_symbol, universal_symbol,
               max_non_terminal_symbols, random_starting_population_size, max_non_terminal_rules):
        configuration = RuleConfiguration()
        configuration.adding = AddingRulesConfiguration.create(
            crowding_factor, crowding_size, elitism_size, max_non_terminal_rules)
        configuration.starting_symbol = Symbol(starting_symbol)
        configuration.universal_symbol = Symbol(universal_symbol) if universal_symbol else None
        configuration.max_non_terminal_symbols = max_non_terminal_symbols
        configuration.random_starting_population_size = random_starting_population_size
        return configuration

    def __init__(self):
        self.adding = None
        self.starting_symbol = None
        self.universal_symbol = None
        self.random_starting_population_size = None
        self.max_non_terminal_symbols = None
        self.max_non_terminal_rules = None


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

    @staticmethod
    def has_succeeded():
        return False


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

    @staticmethod
    def has_succeeded():
        return True


class GcsRunner(object):
    def __init__(self, randomizer, run_no, cyk_service_variant=None):
        self.cyk_service_variant = cyk_service_variant if cyk_service_variant is not None \
            else CykServiceVariationManager(False)
        self.randomizer = randomizer
        self.configuration = None
        self.rule_adding = AddingRuleSupervisor.default(randomizer)
        self.grammar_estimator = None
        self.induction = self.cyk_service_variant.create_cyk_service(randomizer, self.rule_adding)
        self.evolution = EvolutionService(randomizer)
        self.stop_criteria = [NoStopCriteriaSpecified()]
        self.run_no = run_no

    def create_stop_criteria(self):
        self.stop_criteria = [
                                 FitnessStopCriteria(self.grammar_estimator, self.configuration),
                                 StepStopCriteria(self.configuration),
                                 TimeStopCriteria(self.configuration)
                             ]

    def _random_symbol_id(self, configuration):
        return self.randomizer.randint(
            RulePopulation.symbol_shift(),
            RulePopulation.symbol_shift() + configuration.rule.max_non_terminal_symbols)

    def generate_random_rules(self, provided_rules):
        rules = set()
        rules |= set(provided_rules)
        while len(rules) < self.configuration.rule.random_starting_population_size:
            rules.add(Rule(Symbol(self._random_symbol_id(self.configuration)),
                           Symbol(self._random_symbol_id(self.configuration)),
                           Symbol(self._random_symbol_id(self.configuration))))

        return list(rules)

    def add_initial_rules(self, initial_rules, rule_population, grammar_statistics):
        for rule in initial_rules:
            rule_population.add_rule(rule, self.randomizer)
            grammar_statistics.on_added_new_rule(rule)

    def perform_gcs(self, initial_rules, configuration, grammar_estimator,
                    grammar_statistics, sentences):
        self.configuration = configuration
        self.rule_adding.configuration = self.configuration.rule.adding
        self.grammar_estimator = grammar_estimator
        self.create_stop_criteria()

        rule_population = self.cyk_service_variant.create_rule_population(
            self.configuration.rule.starting_symbol, self.configuration.rule.universal_symbol,
            max_non_terminal_symbols=self.configuration.rule.max_non_terminal_symbols)

        self.add_initial_rules(self.generate_random_rules(initial_rules), rule_population,
                               grammar_statistics)

        evolution_step = 0

        # print('')
        while not any(cr() for cr in self.stop_criteria):
            # print('.', end='')
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
            self._post_step_actions(evolution_step)

        stop_reasoning = next(cr for cr in self.stop_criteria if cr.has_been_fulfilled())
        fitness_reached = self.grammar_estimator['fitness'].get_global_max()
        # for x in rule_population.get_all_non_terminal_rules():
        #     print(x)
        # for x in rule_population.get_terminal_rules():
        #     print(x)

        return rule_population, stop_reasoning, fitness_reached, evolution_step

    def _post_step_actions(self, step):
        pass
