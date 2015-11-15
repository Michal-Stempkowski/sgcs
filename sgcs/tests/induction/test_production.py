import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.rule import Rule
from sgcs.induction.detector import Detector
from sgcs.induction.production import ProductionPool, Production, EmptyProduction


class TestProductionPool(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.detector = create_autospec(Detector)

        self.rule_left_side = 'A'
        self.rule = create_autospec(Rule)
        self.rule.configure_mock(parent=self.rule_left_side)

        self.sut = ProductionPool()

    def test_adding_production_should_result_in_storing_it(self):
        # Given:
        production = Production(self.detector, self.rule)

        # When:
        self.sut.add_production(production)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains('A'))
        assert_that(self.sut.get_non_empty_productions(), only_contains(production))

    def test_adding_empty_production_should_be_handled_well(self):
        # Given:
        production = EmptyProduction(self.detector)

        # When:
        self.sut.add_production(production)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(True)))
        assert_that(self.sut.get_effectors(), is_(empty()))
        assert_that(self.sut.get_non_empty_productions(), is_(empty()))

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

    def test_should_be_able_to_find_nonempty_productions_with_a_predicate(self):
        # Given:
        self.rule.configure_mock()
        self.detector.configure_mock(coordinates=1)
        production1 = Production(self.detector, self.rule)
        self.sut.add_production(production1)

        rule2_parent = 'B'
        detector2 = create_autospec(Detector)
        detector2.configure_mock(coordinates=2)
        rule2 = create_autospec(Rule)
        rule2.configure_mock(parent=rule2_parent)
        production2 = Production(detector2, rule2)
        self.sut.add_production(production2)

        # When:
        rules = list(self.sut.find_non_empty_productions(lambda x: x.rule.parent == 'B'))

        # Then:
        assert_that(rules, only_contains(production2))

