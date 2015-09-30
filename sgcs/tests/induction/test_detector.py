import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.induction.detector import Detector
from sgcs.induction.environment import Environment


class TestDetector(unittest.TestCase):
    def test_invalid_coord_should_cause_an_exception(self):
        coordinates = (-1, -1, 5)
        environment_mock = create_autospec(Environment)
        environment_mock.get_symbols.side_effect = IndexError()
        sut = Detector(coordinates)
        assert_that(calling(sut.generate_production).with_args(environment_mock), raises(IndexError))
        environment_mock.get_symbols.assert_called_once_with(coordinates)
