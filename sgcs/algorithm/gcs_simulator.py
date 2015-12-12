import copy
import logging

from algorithm.gcs_runner import GcsRunner
from algorithm.run_estimator import RunEstimator
from grammar_estimator import GrammarEstimator
from statistics.grammar_statistics import GrammarStatistics


class GcsSimulator(object):
    def __init__(self, randomizer):
        self.randomizer = randomizer

    @staticmethod
    def _prepare_configuration_for_generalization_test(conf):
        configuration = copy.deepcopy(conf)

        configuration.should_run_evolution = False

        configuration.induction.grammar_correction.should_run = False
        configuration.induction.coverage.operators.terminal.chance = 0
        configuration.induction.coverage.operators.universal.chance = 0
        configuration.induction.coverage.operators.starting.chance = 0
        configuration.induction.coverage.operators.full.chance = 0

        configuration.max_algorithm_steps = 1
        configuration.max_execution_time = 1800

        configuration.evolution.operators.crossover.chance = 0
        configuration.evolution.operators.mutation.chance = 0
        configuration.evolution.operators.inversion.chance = 0

        configuration.induction.coverage.operators.aggressive.chance = 0

        return configuration

    @staticmethod
    def _rules_population_size_keyfunc(rp):
        return float('inf') if rp is None else rp.terminal_rule_count + rp.non_terminal_rule_count

    def perform_simulation(self, learning_set, testing_set, configuration):
        run_estimator = RunEstimator()
        rule_population = None
        auxiliary_rule_population, aux_fitness = None, 0

        for i in range(configuration.max_algorithm_runs):
            logging.info('Run: %s', str(i))
            grammar_estimator = GrammarEstimator()
            grammar_statistics = GrammarStatistics.default(
                self.randomizer, configuration.statistics)

            runner = GcsRunner(self.randomizer)

            initial_rules = []

            rp, stop_reasoning, fitness_reached, evolution_step = runner.perform_gcs(
                initial_rules, learning_set, configuration, grammar_estimator, grammar_statistics)

            logging.info(learning_set.rule_population_to_string(rp))

            if stop_reasoning.has_succeeded():
                run_estimator.append_success(evolution_step)
                rule_population = min(rp, rule_population, key=self._rules_population_size_keyfunc)
            else:
                run_estimator.append_failure()

            if fitness_reached > aux_fitness:
                auxiliary_rule_population, aux_fitness = rp, fitness_reached

            msg = 'Success: {0}'.format(evolution_step) if stop_reasoning.has_succeeded() \
                else 'Failure'
            print(i, ':', msg)
            logging.info('%s : %s', str(i), str(msg))

        conf = self._prepare_configuration_for_generalization_test(configuration)

        grammar_estimator = GrammarEstimator()
        grammar_statistics = GrammarStatistics.default(self.randomizer, conf.statistics)

        runner = GcsRunner(self.randomizer)

        print('nGen starting')
        logging.info('nGen starting')

        rule_population = rule_population if rule_population is not None \
            else auxiliary_rule_population

        rules = list(rule_population.get_all_non_terminal_rules())
        rules += rule_population.get_terminal_rules()

        rule_population, _, n_gen, *_ = runner.perform_gcs(
            rules, testing_set, conf, grammar_estimator, grammar_statistics)

        logging.info(testing_set.rule_population_to_string(rule_population))

        return run_estimator, n_gen
