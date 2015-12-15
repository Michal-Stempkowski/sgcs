import unittest
from unittest.mock import create_autospec

import math
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

    def assert_estimation(self, step, fitness, positive, negative, sensitivity, specifity, accuracy,
                          min_fitness, max_fitness, min_positive, max_positive,
                          min_negative, max_negative, min_sensitivity, max_sensitivity,
                          min_specifity, max_specifity, min_accuracy, max_accuracy, average_fitness,
                          average_positive, average_negative, average_sensitivity,
                          average_specifity, average_accuracy, global_min_fitness,
                          global_min_positive, global_min_negative, global_min_sensivity,
                          global_min_specifity, global_min_accuracy, global_max_fitness,
                          global_max_positive, global_max_negative, global_max_sensivity,
                          global_max_specifity, global_max_accuracy):
        fit = 'fitness'
        pos = 'positive'
        neg = 'negative'
        sen = 'sensivity'
        spe = 'specifity'
        acc = 'accuracy'

        assert_nearly_equal_or_both_nan(self.sut[fit].get(step), fitness)
        assert_nearly_equal_or_both_nan(self.sut[pos].get(step), positive)
        assert_nearly_equal_or_both_nan(self.sut[neg].get(step), negative)
        assert_nearly_equal_or_both_nan(self.sut[sen].get(step), sensitivity)
        assert_nearly_equal_or_both_nan(self.sut[spe].get(step), specifity)
        assert_nearly_equal_or_both_nan(self.sut[acc].get(step), accuracy)
        
        assert_nearly_equal_or_both_nan(self.sut[fit].get_min(step), min_fitness)
        assert_nearly_equal_or_both_nan(self.sut[fit].get_max(step), max_fitness)

        assert_nearly_equal_or_both_nan(self.sut[pos].get_min(step), min_positive)
        assert_nearly_equal_or_both_nan(self.sut[pos].get_max(step), max_positive)

        assert_nearly_equal_or_both_nan(self.sut[neg].get_min(step), min_negative)
        assert_nearly_equal_or_both_nan(self.sut[neg].get_max(step), max_negative)

        assert_nearly_equal_or_both_nan(self.sut[sen].get_min(step), min_sensitivity)
        assert_nearly_equal_or_both_nan(self.sut[sen].get_max(step), max_sensitivity)

        assert_nearly_equal_or_both_nan(self.sut[spe].get_min(step), min_specifity)
        assert_nearly_equal_or_both_nan(self.sut[spe].get_max(step), max_specifity)

        assert_nearly_equal_or_both_nan(self.sut[acc].get_min(step), min_accuracy)
        assert_nearly_equal_or_both_nan(self.sut[acc].get_max(step), max_accuracy)
        
        assert_nearly_equal_or_both_nan(self.sut[fit].get_global_average(), average_fitness)
        assert_nearly_equal_or_both_nan(self.sut[pos].get_global_average(), average_positive)
        assert_nearly_equal_or_both_nan(self.sut[neg].get_global_average(), average_negative)
        assert_nearly_equal_or_both_nan(self.sut[sen].get_global_average(), average_sensitivity)
        assert_nearly_equal_or_both_nan(self.sut[spe].get_global_average(), average_specifity)
        assert_nearly_equal_or_both_nan(self.sut[acc].get_global_average(), average_accuracy)
        
        assert_nearly_equal_or_both_nan(self.sut[fit].get_global_min(), global_min_fitness)
        assert_nearly_equal_or_both_nan(self.sut[pos].get_global_min(), global_min_positive)
        assert_nearly_equal_or_both_nan(self.sut[neg].get_global_min(), global_min_negative)
        assert_nearly_equal_or_both_nan(self.sut[sen].get_global_min(), global_min_sensivity)
        assert_nearly_equal_or_both_nan(self.sut[spe].get_global_min(), global_min_specifity)
        assert_nearly_equal_or_both_nan(self.sut[acc].get_global_min(), global_min_accuracy)

        assert_nearly_equal_or_both_nan(self.sut[fit].get_global_max(), global_max_fitness)
        assert_nearly_equal_or_both_nan(self.sut[pos].get_global_max(), global_max_positive)
        assert_nearly_equal_or_both_nan(self.sut[neg].get_global_max(), global_max_negative)
        assert_nearly_equal_or_both_nan(self.sut[sen].get_global_max(), global_max_sensivity)
        assert_nearly_equal_or_both_nan(self.sut[spe].get_global_max(), global_max_specifity)
        assert_nearly_equal_or_both_nan(self.sut[acc].get_global_max(), global_max_accuracy)

    def test_grammar_estimation(self):
        self.assert_estimation(step=0, fitness=float('nan'), positive=float('nan'),
                               negative=float('nan'), sensitivity=float('nan'),
                               specifity=float('nan'), accuracy=float('nan'),
                               min_fitness=float('nan'), max_fitness=float('nan'),
                               min_positive=float('nan'), max_positive=float('nan'),
                               min_negative=float('nan'), max_negative=float('nan'),
                               min_sensitivity=float('nan'), max_sensitivity=float('nan'),
                               min_specifity=float('nan'), max_specifity=float('nan'),
                               min_accuracy=float('nan'), max_accuracy=float('nan'),
                               average_fitness=float('nan'),
                               average_positive=float('nan'),
                               average_negative=float('nan'),
                               average_sensitivity=float('nan'),
                               average_specifity=float('nan'),
                               average_accuracy=float('nan'),
                               global_min_fitness=float('nan'),
                               global_min_positive=float('nan'),
                               global_min_negative=float('nan'),
                               global_min_sensivity=float('nan'),
                               global_min_specifity=float('nan'),
                               global_min_accuracy=float('nan'),
                               global_max_fitness=float('nan'),
                               global_max_positive=float('nan'),
                               global_max_negative=float('nan'),
                               global_max_sensivity=float('nan'),
                               global_max_specifity=float('nan'),
                               global_max_accuracy=float('nan'))

        self.sut.append_step_estimation(0, self.mk_evolution_step(tp=3, tn=2, fp=3, fn=2))
        self.assert_estimation(step=0, fitness=0.5, positive=0.6, negative=0.6, sensitivity=0.4,
                               specifity=0.4, accuracy=0.5,
                               min_fitness=0.5, max_fitness=0.5,
                               min_positive=0.6, max_positive=0.6,
                               min_negative=0.6, max_negative=0.6,
                               min_sensitivity=0.4, max_sensitivity=0.4,
                               min_specifity=0.4, max_specifity=0.4,
                               min_accuracy=0.5, max_accuracy=0.5,
                               average_fitness=0.5,
                               average_positive=0.6,
                               average_negative=0.6,
                               average_sensitivity=0.4,
                               average_specifity=0.4,
                               average_accuracy=0.5,
                               global_min_fitness=0.5,
                               global_min_positive=0.6,
                               global_min_negative=0.6,
                               global_min_sensivity=0.4,
                               global_min_specifity=0.4,
                               global_min_accuracy=0.5,
                               global_max_fitness=0.5,
                               global_max_positive=0.6,
                               global_max_negative=0.6,
                               global_max_sensivity=0.4,
                               global_max_specifity=0.4,
                               global_max_accuracy=0.5)

        self.sut.append_step_estimation(0, self.mk_evolution_step(tp=5, tn=5, fp=0, fn=0))
        self.assert_estimation(step=0, fitness=0.75, positive=0.8, negative=0.3, sensitivity=0.7,
                               specifity=0.7, accuracy=0.75,
                               min_fitness=0.5, max_fitness=0.75,
                               min_positive=0.6, max_positive=0.8,
                               min_negative=0.3, max_negative=0.6,
                               min_sensitivity=0.4, max_sensitivity=0.7,
                               min_specifity=0.4, max_specifity=0.7,
                               min_accuracy=0.5, max_accuracy=0.75,
                               average_fitness=0.75,
                               average_positive=0.8,
                               average_negative=0.3,
                               average_sensitivity=0.7,
                               average_specifity=0.7,
                               average_accuracy=0.75,
                               global_min_fitness=0.5,
                               global_min_positive=0.6,
                               global_min_negative=0.3,
                               global_min_sensivity=0.4,
                               global_min_specifity=0.4,
                               global_min_accuracy=0.5,
                               global_max_fitness=0.75,
                               global_max_positive=0.8,
                               global_max_negative=0.6,
                               global_max_sensivity=0.7,
                               global_max_specifity=0.7,
                               global_max_accuracy=0.75)

        self.sut.append_step_estimation(1, self.mk_evolution_step(tp=0, tn=1, fp=2, fn=0))
        self.assert_estimation(step=1, fitness=0.33, positive=float('nan'), negative=0.67,
                               sensitivity=float('nan'), specifity=0.33, accuracy=0.33,
                               min_fitness=0.33, max_fitness=0.33,
                               min_positive=float('nan'), max_positive=float('nan'),
                               min_negative=0.67, max_negative=0.67,
                               min_sensitivity=float('nan'), max_sensitivity=float('nan'),
                               min_specifity=0.33, max_specifity=0.33,
                               min_accuracy=0.33, max_accuracy=0.33,
                               average_fitness=0.54,
                               average_positive=0.8,
                               average_negative=0.48,
                               average_sensitivity=0.7,
                               average_specifity=0.52,
                               average_accuracy=0.54,
                               global_min_fitness=0.33,
                               global_min_positive=0.6,
                               global_min_negative=0.3,
                               global_min_sensivity=0.4,
                               global_min_specifity=0.33,
                               global_min_accuracy=0.33,
                               global_max_fitness=0.75,
                               global_max_positive=0.8,
                               global_max_negative=0.67,
                               global_max_sensivity=0.7,
                               global_max_specifity=0.7,
                               global_max_accuracy=0.75)
        self.assert_estimation(step=0, fitness=0.75, positive=0.8, negative=0.3, sensitivity=0.7,
                               specifity=0.7, accuracy=0.75,
                               min_fitness=0.5, max_fitness=0.75,
                               min_positive=0.6, max_positive=0.8,
                               min_negative=0.3, max_negative=0.6,
                               min_sensitivity=0.4, max_sensitivity=0.7,
                               min_specifity=0.4, max_specifity=0.7,
                               min_accuracy=0.5, max_accuracy=0.75,
                               average_fitness=0.54,
                               average_positive=0.8,
                               average_negative=0.48,
                               average_sensitivity=0.7,
                               average_specifity=0.52,
                               average_accuracy=0.54,
                               global_min_fitness=0.33,
                               global_min_positive=0.6,
                               global_min_negative=0.3,
                               global_min_sensivity=0.4,
                               global_min_specifity=0.33,
                               global_min_accuracy=0.33,
                               global_max_fitness=0.75,
                               global_max_positive=0.8,
                               global_max_negative=0.67,
                               global_max_sensivity=0.7,
                               global_max_specifity=0.7,
                               global_max_accuracy=0.75)
