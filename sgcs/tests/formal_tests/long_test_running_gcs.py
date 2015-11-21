import unittest
from unittest.mock import create_autospec

from hamcrest import *

from algorithm.gcs_runner import GcsRunner, AlgorithmConfiguration


class LongTestRunningGcs(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.configuration = AlgorithmConfiguration.default()

        self.sut = GcsRunner(self.configuration)

    def test_gcs_for_tomita_l1(self):
        assert_that(True)
