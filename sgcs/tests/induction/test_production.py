import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *
from sgcs.induction.detector import Detector
from sgcs.induction.production import ProductionPool, Production, EmptyProduction
from sgcs.induction.rule import Rule


class TestProductionPool(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.detector = create_autospec(Detector)

        self.rule_left_side = 'A'
        self.rule = create_autospec(Rule)
        type(self.rule).parent = PropertyMock(return_value=self.rule_left_side)

        self.sut = ProductionPool()

    def test_adding_production_should_result_in_storing_it(self):
        # Given:
        production = Production(self.detector, self.rule)

        # When:
        self.sut.add_production(production)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains('A'))

    def test_adding_empty_production_should_be_handled_well(self):
        # Given:
        production = EmptyProduction(self.detector)

        # When:
        self.sut.add_production(production)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(True)))
        assert_that(self.sut.get_effectors(), is_(empty()))

    def test_should_be_able_to_get_unsatisfied_detectors(self):
        # Given:
        empty_detector = create_autospec(Detector)
        empty_production = EmptyProduction(empty_detector)
        self.sut.add_production(empty_production)

        production = Production(self.detector, self.rule)
        self.sut.add_production(production)

        # When:
        result = self.sut.get_unsatisfied_detectors()

        # Then:
        assert_that(result, only_contains(empty_detector))

