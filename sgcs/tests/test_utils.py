from random import Random
import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.utils import Randomizer


class TestRandomizer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.low = 0.2
        self.chance = 0.2
        self.high = 0.21

        self.generator_mock = create_autospec(Random)
        self.sut = Randomizer(self.generator_mock)

    def test_on_high_result_perform_with_chance_should_return_false(self):
        self.generator_mock.random.return_value = self.high

        assert_that(self.sut.perform_with_chance(self.chance), is_(False))

    def test_on_low_result_perform_with_chance_should_return_true(self):
        self.generator_mock.random.return_value = self.low

        assert_that(self.sut.perform_with_chance(self.chance), is_(True))
