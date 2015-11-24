import unittest
from unittest.mock import create_autospec

from hamcrest import *

from grammar_estimator import EvolutionStepEstimator
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
        assert_nearly_equal_or_both_nan(self.sut.fitness, fitness, 0.01)

    def test_adding_results(self):
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
                               fitness=0.66)

        self.sut.append_result(result_tn)
        self.assert_estimation(tp=2, tn=1, fp=1, fn=0, total=4, positives=2, negatives=2,
                               fitness=0.75)

        self.sut.append_result(result_fn)
        self.assert_estimation(tp=2, tn=1, fp=1, fn=1, total=5, positives=3, negatives=2,
                               fitness=0.6)
