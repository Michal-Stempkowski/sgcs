import unittest
from unittest.mock import create_autospec

import math
from hamcrest import *

from algorithm.run_estimator import RunEstimator
from tests.test_common import assert_nearly_equal_or_both_nan


class TestRunEstimator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = RunEstimator()

    def assert_estimation(self, n_success, n_evals, s, min_evals):
        assert_that(self.sut.n_success, is_(equal_to(n_success)))
        assert_nearly_equal_or_both_nan(self.sut.n_evals, n_evals)
        assert_nearly_equal_or_both_nan(self.sut.s, s)
        assert_nearly_equal_or_both_nan(self.sut.min_evals, min_evals)

    def test_no_runs__statistics_should_be_according(self):
        self.assert_estimation(
            n_success=(0, 0), n_evals=float('nan'),
            s=float('nan'), min_evals=float('nan'))

    def test_estimation_should_be_calculated_properly(self):
        self.assert_estimation(
            n_success=(0, 0), n_evals=float('nan'),
            s=float('nan'), min_evals=float('nan'))

        self.sut.append_failure()
        self.assert_estimation(
            n_success=(0, 1), n_evals=float('nan'),
            s=float('nan'), min_evals=float('nan'))

        self.sut.append_success(555)
        self.assert_estimation(n_success=(1, 2), n_evals=555, s=0, min_evals=555)

        self.sut.append_success(3)
        self.assert_estimation(n_success=(2, 3), n_evals=279, s=276, min_evals=3)

        self.sut.append_failure()
        self.assert_estimation(n_success=(2, 4), n_evals=279, s=276, min_evals=3)

        self.sut.append_success(20)
        self.assert_estimation(n_success=(3, 5), n_evals=192.66, s=256.30, min_evals=3)

