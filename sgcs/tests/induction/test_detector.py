import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.induction.detector import Detector
from sgcs.induction.environment import Environment


class TestDetector(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.coordinates = (4, 4, 2)
        self.environment_mock = create_autospec(Environment)
        self.sut = Detector(self.coordinates)

    def test_invalid_coord_should_cause_an_exception(self):
        self.environment_mock.get_symbols.side_effect = IndexError()

        assert_that(
            calling(self.sut.generate_production).with_args(self.environment_mock),
            raises(IndexError))

        self.environment_mock.get_symbols.assert_called_once_with(self.coordinates)

    def test_on_no_rules_generate_production_should_return_empty_production(self):
        self.environment_mock.get_symbols.return_value = []

        assert_that(
            self.sut.generate_production(self.environment_mock).is_empty(),
            is_(equal_to(True)))

        self.environment_mock.get_symbols.assert_called_once_with(self.coordinates)
