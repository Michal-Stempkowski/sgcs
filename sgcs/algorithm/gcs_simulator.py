import copy
import logging

import multiprocessing
import os
import random

from algorithm.gcs_runner import GcsRunner
from algorithm.run_estimator import RunEstimator
from grammar_estimator import GrammarEstimator
from statistics.grammar_statistics import GrammarStatistics


class GcsSimulator(object):
    def __init__(self, randomizer, algorithm_variant):
        self.randomizer = randomizer
        self.algorithm_variant = algorithm_variant

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

    def _prepare_for_run(self, learning_set):
        run_estimator = RunEstimator()
        rule_population = None
        auxiliary_rule_population, aux_fitness = None, 0

        sentences = list(learning_set.get_sentences())

        return run_estimator, rule_population, auxiliary_rule_population, aux_fitness, sentences

    def _perform_run(self, configuration, initial_rules, sentences, run_no):
        grammar_estimator = GrammarEstimator()
        grammar_statistics = self.algorithm_variant.create_grammar_statistics(
            self.randomizer, configuration.statistics)

        runner = GcsRunner(self.randomizer, self.algorithm_variant)

        return runner.perform_gcs(
            initial_rules, copy.deepcopy(configuration), grammar_estimator, grammar_statistics,
            sentences) + (grammar_estimator, )

    def _handle_run_result(self, stop_reasoning, learning_set, run_estimator, rp, rule_population,
                           fitness_reached, auxiliary_rule_population, aux_fitness, evolution_step,
                           run_no):
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
        print(run_no, ':', msg)
        logging.info('%s : %s', str(run_no), str(msg))

        return rule_population, auxiliary_rule_population, aux_fitness

    def _perform_generalization_test(self, configuration, rule_population, auxiliary_rule_population,
                                     testing_set, run_estimator):
        conf = self._prepare_configuration_for_generalization_test(configuration)

        print('nGen starting')
        logging.info('nGen starting')

        rule_population = rule_population if rule_population is not None \
            else auxiliary_rule_population

        rules = list(rule_population.get_all_non_terminal_rules())
        rules += rule_population.get_terminal_rules()

        rule_population, _, n_gen, *_ = self._generalization_run(
            conf, rules, list(testing_set.get_sentences()))

        logging.info(testing_set.rule_population_to_string(rule_population))

        return run_estimator, n_gen

    def _generalization_run(self, conf, rules, sentences):
        return self._perform_run(conf, rules, sentences, None)

    def perform_simulation(self, learning_set, testing_set, configuration):
        run_estimator, rule_population, auxiliary_rule_population, aux_fitness, sentences = \
            self._prepare_for_run(learning_set)

        for i in range(configuration.max_algorithm_runs):
            logging.info('Run: %s', str(i))
            rp, stop_reasoning, fitness_reached, evolution_step, grammar_estimator = \
                self._perform_run(configuration, [], sentences, i)

            rule_population, auxiliary_rule_population, aux_fitness = self._handle_run_result(
                stop_reasoning, learning_set, run_estimator, rp, rule_population, fitness_reached,
                auxiliary_rule_population, aux_fitness, evolution_step, i)

        return self._perform_generalization_test(
            configuration, rule_population, auxiliary_rule_population, testing_set, run_estimator)


class AsyncGcsSimulator(GcsSimulator):
    @staticmethod
    def calculate(func, args):
        return func(*args)

    def calculate_star(self, args):
        func, args_, run_no, seed = args
        self.randomizer.generator = random.Random(seed)
        return self.calculate(func, args_), run_no

    def perform_simulation(self, learning_set, testing_set, configuration):
        run_estimator, rule_population, auxiliary_rule_population, aux_fitness, sentences = \
            self._prepare_for_run(learning_set)

        worker_pool_size = multiprocessing.cpu_count()

        with multiprocessing.Pool(worker_pool_size) as pool:
            runs_to_be_performed = range(configuration.max_algorithm_runs)
            tasks = [(self._perform_run, (
                copy.deepcopy(configuration), copy.deepcopy([]), copy.deepcopy(sentences), run_no),
                      run_no, random.randint(0, 10**10))
                     for run_no in runs_to_be_performed]

            async_results = pool.imap_unordered(self.calculate_star, tasks)

            for result in async_results:
                # print(result)
                (rp, stop_reasoning, fitness_reached, evolution_step, grammar_estimator), run_no = \
                    result

                rule_population, auxiliary_rule_population, aux_fitness = self._handle_run_result(
                    stop_reasoning, learning_set, run_estimator, rp, rule_population,
                    fitness_reached, auxiliary_rule_population, aux_fitness, evolution_step, run_no)

        # for i in range(configuration.max_algorithm_runs):
        #     logging.info('Run: %s', str(i))
        #     rp, stop_reasoning, fitness_reached, evolution_step = self._perform_run(
        #         configuration, [], sentences)
        #
        #     rule_population, auxiliary_rule_population, aux_fitness = self._handle_run_result(
        #         stop_reasoning, learning_set, run_estimator, rp, rule_population, fitness_reached,
        #         auxiliary_rule_population, aux_fitness, evolution_step, i)

        return self._perform_generalization_test(
            configuration, rule_population, auxiliary_rule_population, testing_set, run_estimator)

    def _generalization_run(self, conf, rules, sentences):
        with multiprocessing.Pool(1) as pool:
            async_result = pool.imap_unordered(
                self.calculate_star, [(self._perform_run, (conf, rules, sentences, None), None,
                                       random.randint(0, 10**10))])

        for result in async_result:
            return result
