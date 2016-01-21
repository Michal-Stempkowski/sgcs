import copy
import unittest
from unittest.mock import create_autospec

import math

import itertools
from hamcrest import *

from grammar_estimator import EvolutionStepEstimator, GrammarEstimator
from induction.cyk_executors import CykResult
from tests.test_common import assert_nearly_equal_or_both_nan


class TestEvolutionStepEstimator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = EvolutionStepEstimator()

    def mk_cyk_result(self, belongs_to_grammar, is_positive):
        result = CykResult()
        result.belongs_to_grammar = belongs_to_grammar
        result.is_positive = is_positive
        return result

    def assert_estimation(self, tp, tn, fp, fn, total, positives, negatives, fitness):
        assert_that(self.sut.true_positive, is_(equal_to(tp)))
        assert_that(self.sut.true_negative, is_(equal_to(tn)))
        assert_that(self.sut.false_positive, is_(equal_to(fp)))
        assert_that(self.sut.false_negative, is_(equal_to(fn)))
        assert_that(self.sut.total, is_(equal_to(total)))
        assert_that(self.sut.positives_that_has_occurred, is_(equal_to(positives)))
        assert_that(self.sut.negatives_that_has_occurred, is_(equal_to(negatives)))
        assert_nearly_equal_or_both_nan(self.sut.fitness, fitness)

    def test_step_estimation(self):
        result_tp = self.mk_cyk_result(True, True)
        result_fp = self.mk_cyk_result(True, False)
        result_tn = self.mk_cyk_result(False, False)
        result_fn = self.mk_cyk_result(False, True)

        self.assert_estimation(tp=0, tn=0, fp=0, fn=0, total=0, positives=0, negatives=0,
                               fitness=float('nan'))

        self.sut.append_result(result_tp)
        self.assert_estimation(tp=1, tn=0, fp=0, fn=0, total=1, positives=1, negatives=0,
                               fitness=1)

        self.sut.append_result(result_tp)
        self.assert_estimation(tp=2, tn=0, fp=0, fn=0, total=2, positives=2, negatives=0,
                               fitness=1)

        self.sut.append_result(result_fp)
        self.assert_estimation(tp=2, tn=0, fp=1, fn=0, total=3, positives=2, negatives=1,
                               fitness=0.67)

        self.sut.append_result(result_tn)
        self.assert_estimation(tp=2, tn=1, fp=1, fn=0, total=4, positives=2, negatives=2,
                               fitness=0.75)

        self.sut.append_result(result_fn)
        self.assert_estimation(tp=2, tn=1, fp=1, fn=1, total=5, positives=3, negatives=2,
                               fitness=0.6)


class TestGrammarEstimator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = GrammarEstimator()

    @staticmethod
    def mk_evolution_step(tp, tn, fp, fn):
        step = EvolutionStepEstimator()
        step._true_positive = tp
        step._true_negative = tn
        step._false_positive = fp
        step._false_negative = fn
        return step

    def assert_estimation(self, step, fitness, miss_rate, fallout, sensitivity, specificity,
                          accuracy,
                          min_fitness, max_fitness, min_miss_rate, max_miss_rate,
                          min_fallout, max_fallout, min_sensitivity, max_sensitivity,
                          min_specificity, max_specificity, min_accuracy, max_accuracy,
                          average_fitness, average_miss_rate, average_fallout, average_sensitivity,
                          average_specificity, average_accuracy, global_min_fitness,
                          global_min_miss_rate, global_min_fallout, global_min_sensitivity,
                          global_min_specificity, global_min_accuracy, global_max_fitness,
                          global_max_miss_rate, global_max_fallout, global_max_sensitivity,
                          global_max_specificity, global_max_accuracy, estimator=None):
        fit = 'fitness'
        mis = 'missrate'
        fal = 'fallout'
        sen = 'sensitivity'
        spe = 'specificity'
        acc = 'accuracy'

        estimator = estimator if estimator is not None else self.sut

        assert_nearly_equal_or_both_nan(estimator[fit].get(step), fitness)
        assert_nearly_equal_or_both_nan(estimator[mis].get(step), miss_rate)
        assert_nearly_equal_or_both_nan(estimator[fal].get(step), fallout)
        assert_nearly_equal_or_both_nan(estimator[sen].get(step), sensitivity)
        assert_nearly_equal_or_both_nan(estimator[spe].get(step), specificity)
        assert_nearly_equal_or_both_nan(estimator[acc].get(step), accuracy)
        
        assert_nearly_equal_or_both_nan(estimator[fit].get_min(step), min_fitness)
        assert_nearly_equal_or_both_nan(estimator[fit].get_max(step), max_fitness)

        assert_nearly_equal_or_both_nan(estimator[mis].get_min(step), min_miss_rate)
        assert_nearly_equal_or_both_nan(estimator[mis].get_max(step), max_miss_rate)

        assert_nearly_equal_or_both_nan(estimator[fal].get_min(step), min_fallout)
        assert_nearly_equal_or_both_nan(estimator[fal].get_max(step), max_fallout)

        assert_nearly_equal_or_both_nan(estimator[sen].get_min(step), min_sensitivity)
        assert_nearly_equal_or_both_nan(estimator[sen].get_max(step), max_sensitivity)

        assert_nearly_equal_or_both_nan(estimator[spe].get_min(step), min_specificity)
        assert_nearly_equal_or_both_nan(estimator[spe].get_max(step), max_specificity)

        assert_nearly_equal_or_both_nan(estimator[acc].get_min(step), min_accuracy)
        assert_nearly_equal_or_both_nan(estimator[acc].get_max(step), max_accuracy)
        
        assert_nearly_equal_or_both_nan(estimator[fit].get_global_average(), average_fitness)
        assert_nearly_equal_or_both_nan(estimator[mis].get_global_average(), average_miss_rate)
        assert_nearly_equal_or_both_nan(estimator[fal].get_global_average(), average_fallout)
        assert_nearly_equal_or_both_nan(estimator[sen].get_global_average(), average_sensitivity)
        assert_nearly_equal_or_both_nan(estimator[spe].get_global_average(), average_specificity)
        assert_nearly_equal_or_both_nan(estimator[acc].get_global_average(), average_accuracy)
        
        assert_nearly_equal_or_both_nan(estimator[fit].get_global_min(), global_min_fitness)
        assert_nearly_equal_or_both_nan(estimator[mis].get_global_min(), global_min_miss_rate)
        assert_nearly_equal_or_both_nan(estimator[fal].get_global_min(), global_min_fallout)
        assert_nearly_equal_or_both_nan(estimator[sen].get_global_min(), global_min_sensitivity)
        assert_nearly_equal_or_both_nan(estimator[spe].get_global_min(), global_min_specificity)
        assert_nearly_equal_or_both_nan(estimator[acc].get_global_min(), global_min_accuracy)

        assert_nearly_equal_or_both_nan(estimator[fit].get_global_max(), global_max_fitness)
        assert_nearly_equal_or_both_nan(estimator[mis].get_global_max(), global_max_miss_rate)
        assert_nearly_equal_or_both_nan(estimator[fal].get_global_max(), global_max_fallout)
        assert_nearly_equal_or_both_nan(estimator[sen].get_global_max(), global_max_sensitivity)
        assert_nearly_equal_or_both_nan(estimator[spe].get_global_max(), global_max_specificity)
        assert_nearly_equal_or_both_nan(estimator[acc].get_global_max(), global_max_accuracy)

    def test_grammar_estimation(self):
        self.assert_estimation(step=0, fitness=float('nan'), miss_rate=float('nan'),
                               fallout=float('nan'), sensitivity=float('nan'),
                               specificity=float('nan'), accuracy=float('nan'),
                               min_fitness=float('nan'), max_fitness=float('nan'),
                               min_miss_rate=float('nan'), max_miss_rate=float('nan'),
                               min_fallout=float('nan'), max_fallout=float('nan'),
                               min_sensitivity=float('nan'), max_sensitivity=float('nan'),
                               min_specificity=float('nan'), max_specificity=float('nan'),
                               min_accuracy=float('nan'), max_accuracy=float('nan'),
                               average_fitness=float('nan'),
                               average_miss_rate=float('nan'),
                               average_fallout=float('nan'),
                               average_sensitivity=float('nan'),
                               average_specificity=float('nan'),
                               average_accuracy=float('nan'),
                               global_min_fitness=float('nan'),
                               global_min_miss_rate=float('nan'),
                               global_min_fallout=float('nan'),
                               global_min_sensitivity=float('nan'),
                               global_min_specificity=float('nan'),
                               global_min_accuracy=float('nan'),
                               global_max_fitness=float('nan'),
                               global_max_miss_rate=float('nan'),
                               global_max_fallout=float('nan'),
                               global_max_sensitivity=float('nan'),
                               global_max_specificity=float('nan'),
                               global_max_accuracy=float('nan'))

        self.sut.append_step_estimation(0, self.mk_evolution_step(tp=3, tn=2, fp=3, fn=2))
        self.assert_estimation(step=0, fitness=0.5, miss_rate=0.4, fallout=0.6, sensitivity=0.6,
                               specificity=0.4, accuracy=0.5,
                               min_fitness=0.5, max_fitness=0.5,
                               min_miss_rate=0.4, max_miss_rate=0.4,
                               min_fallout=0.6, max_fallout=0.6,
                               min_sensitivity=0.6, max_sensitivity=0.6,
                               min_specificity=0.4, max_specificity=0.4,
                               min_accuracy=0.5, max_accuracy=0.5,
                               average_fitness=0.5,
                               average_miss_rate=0.4,
                               average_fallout=0.6,
                               average_sensitivity=0.6,
                               average_specificity=0.4,
                               average_accuracy=0.5,
                               global_min_fitness=0.5,
                               global_min_miss_rate=0.4,
                               global_min_fallout=0.6,
                               global_min_sensitivity=0.6,
                               global_min_specificity=0.4,
                               global_min_accuracy=0.5,
                               global_max_fitness=0.5,
                               global_max_miss_rate=0.4,
                               global_max_fallout=0.6,
                               global_max_sensitivity=0.6,
                               global_max_specificity=0.4,
                               global_max_accuracy=0.5)

        self.sut.append_step_estimation(0, self.mk_evolution_step(tp=5, tn=5, fp=0, fn=0))
        self.assert_estimation(step=0, fitness=0.75, miss_rate=0.2, fallout=0.3, sensitivity=0.8,
                               specificity=0.7, accuracy=0.75,
                               min_fitness=0.5, max_fitness=0.75,
                               min_miss_rate=0.2, max_miss_rate=0.4,
                               min_fallout=0.3, max_fallout=0.6,
                               min_sensitivity=0.6, max_sensitivity=0.8,
                               min_specificity=0.4, max_specificity=0.7,
                               min_accuracy=0.5, max_accuracy=0.75,
                               average_fitness=0.75,
                               average_miss_rate=0.2,
                               average_fallout=0.3,
                               average_sensitivity=0.8,
                               average_specificity=0.7,
                               average_accuracy=0.75,
                               global_min_fitness=0.5,
                               global_min_miss_rate=0.2,
                               global_min_fallout=0.3,
                               global_min_sensitivity=0.6,
                               global_min_specificity=0.4,
                               global_min_accuracy=0.5,
                               global_max_fitness=0.75,
                               global_max_miss_rate=0.4,
                               global_max_fallout=0.6,
                               global_max_sensitivity=0.8,
                               global_max_specificity=0.7,
                               global_max_accuracy=0.75)

        self.sut.append_step_estimation(1, self.mk_evolution_step(tp=0, tn=1, fp=2, fn=0))
        self.common_final_assert()

    def common_grammar_estimation_adding(self, left, right, first, second, third):
        first.append_step_estimation(0, self.mk_evolution_step(tp=7, tn=2, fp=1, fn=0))
        self.assert_estimation(step=0, fitness=0.9, miss_rate=0, fallout=0.33, sensitivity=1,
                               specificity=0.67, accuracy=0.9,
                               min_fitness=0.9, max_fitness=0.9,
                               min_miss_rate=0, max_miss_rate=0,
                               min_fallout=0.33, max_fallout=0.33,
                               min_sensitivity=1, max_sensitivity=1,
                               min_specificity=0.67, max_specificity=0.67,
                               min_accuracy=0.9, max_accuracy=0.9,
                               average_fitness=0.9,
                               average_miss_rate=0,
                               average_fallout=0.33,
                               average_sensitivity=1,
                               average_specificity=0.67,
                               average_accuracy=0.9,
                               global_min_fitness=0.9,
                               global_min_miss_rate=0,
                               global_min_fallout=0.33,
                               global_min_sensitivity=1,
                               global_min_specificity=0.67,
                               global_min_accuracy=0.9,
                               global_max_fitness=0.9,
                               global_max_miss_rate=0,
                               global_max_fallout=0.33,
                               global_max_sensitivity=1,
                               global_max_specificity=0.67,
                               global_max_accuracy=0.9,
                               estimator=left + right)

        second.append_step_estimation(0, self.mk_evolution_step(tp=3, tn=2, fp=0, fn=1))
        self.assert_estimation(step=0, fitness=0.87, miss_rate=0.13, fallout=0.17, sensitivity=0.88,
                               specificity=0.83, accuracy=0.87,
                               min_fitness=0.87, max_fitness=0.9,
                               min_miss_rate=0, max_miss_rate=0.13,
                               min_fallout=0.17, max_fallout=0.33,
                               min_sensitivity=0.88, max_sensitivity=1,
                               min_specificity=0.67, max_specificity=0.83,
                               min_accuracy=0.87, max_accuracy=0.9,
                               average_fitness=0.87,
                               average_miss_rate=0.13,
                               average_fallout=0.17,
                               average_sensitivity=0.88,
                               average_specificity=0.83,
                               average_accuracy=0.87,
                               global_min_fitness=0.87,
                               global_min_miss_rate=0,
                               global_min_fallout=0.17,
                               global_min_sensitivity=0.88,
                               global_min_specificity=0.67,
                               global_min_accuracy=0.87,
                               global_max_fitness=0.9,
                               global_max_miss_rate=0.13,
                               global_max_fallout=0.33,
                               global_max_sensitivity=1,
                               global_max_specificity=0.83,
                               global_max_accuracy=0.9,
                               estimator=left + right)

        third.append_step_estimation(1, self.mk_evolution_step(tp=2, tn=7, fp=1, fn=5))
        self.assert_estimation(step=0, fitness=0.87, miss_rate=0.13, fallout=0.17, sensitivity=0.88,
                               specificity=0.83, accuracy=0.87,
                               min_fitness=0.87, max_fitness=0.9,
                               min_miss_rate=0, max_miss_rate=0.13,
                               min_fallout=0.17, max_fallout=0.33,
                               min_sensitivity=0.88, max_sensitivity=1,
                               min_specificity=0.67, max_specificity=0.83,
                               min_accuracy=0.87, max_accuracy=0.9,
                               average_fitness=0.73,
                               average_miss_rate=0.42,
                               average_fallout=0.15,
                               average_sensitivity=0.58,
                               average_specificity=0.85,
                               average_accuracy=0.73,
                               global_min_fitness=0.6,
                               global_min_miss_rate=0,
                               global_min_fallout=0.13,
                               global_min_sensitivity=0.29,
                               global_min_specificity=0.67,
                               global_min_accuracy=0.6,
                               global_max_fitness=0.9,
                               global_max_miss_rate=0.71,
                               global_max_fallout=0.33,
                               global_max_sensitivity=1,
                               global_max_specificity=0.88,
                               global_max_accuracy=0.9,
                               estimator=left + right)
        self.assert_estimation(step=1, fitness=0.6, miss_rate=0.71, fallout=0.13, sensitivity=0.29,
                               specificity=0.88, accuracy=0.6,
                               min_fitness=0.6, max_fitness=0.6,
                               min_miss_rate=0.71, max_miss_rate=0.71,
                               min_fallout=0.13, max_fallout=0.13,
                               min_sensitivity=0.29, max_sensitivity=0.29,
                               min_specificity=0.88, max_specificity=0.88,
                               min_accuracy=0.6, max_accuracy=0.6,
                               average_fitness=0.73,
                               average_miss_rate=0.42,
                               average_fallout=0.15,
                               average_sensitivity=0.58,
                               average_specificity=0.85,
                               average_accuracy=0.73,
                               global_min_fitness=0.6,
                               global_min_miss_rate=0,
                               global_min_fallout=0.13,
                               global_min_sensitivity=0.29,
                               global_min_specificity=0.67,
                               global_min_accuracy=0.6,
                               global_max_fitness=0.9,
                               global_max_miss_rate=0.71,
                               global_max_fallout=0.33,
                               global_max_sensitivity=1,
                               global_max_specificity=0.88,
                               global_max_accuracy=0.9,
                               estimator=left + right)

    @staticmethod
    def _select(left, right, decision):
        return left if not decision else right

    def test_grammar_estimation_adding(self):
        test_data = [
            (0, 0, 0)  # 3/0
            , (0, 0, 1)  # false
            , (0, 1, 0)  # 2/1
            , (0, 1, 1)  # 1/2
        ]
        for decisions in test_data:
            left = GrammarEstimator()
            right = GrammarEstimator()
            args = [left, right] + [self._select(left, right, x) for x in decisions]
            self.common_grammar_estimation_adding(*args)

    def common_final_assert(self):
        self.assert_estimation(step=1, fitness=0.33, miss_rate=float('nan'), fallout=0.67,
                               sensitivity=float('nan'), specificity=0.33, accuracy=0.33,
                               min_fitness=0.33, max_fitness=0.33,
                               min_miss_rate=float('nan'), max_miss_rate=float('nan'),
                               min_fallout=0.67, max_fallout=0.67,
                               min_sensitivity=float('nan'), max_sensitivity=float('nan'),
                               min_specificity=0.33, max_specificity=0.33,
                               min_accuracy=0.33, max_accuracy=0.33,
                               average_fitness=0.54,
                               average_miss_rate=0.2,
                               average_fallout=0.48,
                               average_sensitivity=0.8,
                               average_specificity=0.52,
                               average_accuracy=0.54,
                               global_min_fitness=0.33,
                               global_min_miss_rate=0.2,
                               global_min_fallout=0.3,
                               global_min_sensitivity=0.6,
                               global_min_specificity=0.33,
                               global_min_accuracy=0.33,
                               global_max_fitness=0.75,
                               global_max_miss_rate=0.4,
                               global_max_fallout=0.67,
                               global_max_sensitivity=0.8,
                               global_max_specificity=0.7,
                               global_max_accuracy=0.75)
        self.assert_estimation(step=0, fitness=0.75, miss_rate=0.2, fallout=0.3, sensitivity=0.8,
                               specificity=0.7, accuracy=0.75,
                               min_fitness=0.5, max_fitness=0.75,
                               min_miss_rate=0.2, max_miss_rate=0.4,
                               min_fallout=0.3, max_fallout=0.6,
                               min_sensitivity=0.6, max_sensitivity=0.8,
                               min_specificity=0.4, max_specificity=0.7,
                               min_accuracy=0.5, max_accuracy=0.75,
                               average_fitness=0.54,
                               average_miss_rate=0.2,
                               average_fallout=0.48,
                               average_sensitivity=0.8,
                               average_specificity=0.52,
                               average_accuracy=0.54,
                               global_min_fitness=0.33,
                               global_min_miss_rate=0.2,
                               global_min_fallout=0.3,
                               global_min_sensitivity=0.6,
                               global_min_specificity=0.33,
                               global_min_accuracy=0.33,
                               global_max_fitness=0.75,
                               global_max_miss_rate=0.4,
                               global_max_fallout=0.67,
                               global_max_sensitivity=0.8,
                               global_max_specificity=0.7,
                               global_max_accuracy=0.75)

    def test_grammar_json(self):
        self.sut.append_step_estimation(0, self.mk_evolution_step(tp=3, tn=2, fp=3, fn=2))
        self.sut.append_step_estimation(0, self.mk_evolution_step(tp=5, tn=5, fp=0, fn=0))
        self.sut.append_step_estimation(1, self.mk_evolution_step(tp=0, tn=1, fp=2, fn=0))
        self.common_final_assert()

        jsonized = self.sut.json_coder()
        self.sut = GrammarEstimator()
        self.sut.json_decoder(jsonized)
        self.common_final_assert()
