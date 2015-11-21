import unittest
from unittest.mock import create_autospec

from hamcrest import *

from algorithm.gcs_runner import GcsRunner


class LongTestRunningGcs(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.sut = GcsRunner()

    def test_gcs_for_tomita_l1(self):
        assert_that(True)