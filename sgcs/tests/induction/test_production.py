import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.rule import Rule
from core.symbol import Symbol
from induction.environment import viterbi_probability_approach, baum_welch_probability_approach
from sgcs.induction.detector import Detector
from sgcs.induction.production import ProductionPool, Production, EmptyProduction


class TestProductionPool(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.detector = create_autospec(Detector)

        self.rule_left_side = Symbol('A')
        self.rule = create_autospec(Rule)
        self.rule.configure_mock(parent=self.rule_left_side)

        self.sut = ProductionPool()

    def test_adding_production_should_result_in_storing_it(self):
        # Given:
        production = Production(self.detector, self.rule)

        # When:
        self.sut.add_production(production, (anything(), anything()), None)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains(Symbol('A')))
        assert_that(self.sut.get_non_empty_productions(), only_contains(production))

    def test_adding_empty_production_should_be_handled_well(self):
        # Given:
        production = EmptyProduction(self.detector)

        # When:
        self.sut.add_production(production, (anything(), anything()), None)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(True)))
        assert_that(self.sut.get_effectors(), is_(empty()))
        assert_that(self.sut.get_non_empty_productions(), is_(empty()))

    def test_should_be_able_to_get_unsatisfied_detectors(self):
        # Given:
        empty_detector = create_autospec(Detector)
        empty_production = EmptyProduction(empty_detector)
        self.sut.add_production(empty_production, (anything(), anything()), None)

        production = Production(self.detector, self.rule)
        self.sut.add_production(production, (anything(), anything()), None)

        # When:
        result = self.sut.get_unsatisfied_detectors()

        # Then:
        assert_that(result, only_contains(empty_detector))

    def test_should_be_able_to_find_nonempty_productions_with_a_predicate(self):
        # Given:
        self.rule.configure_mock()
        self.detector.configure_mock(coordinates=1)
        production1 = Production(self.detector, self.rule)
        self.sut.add_production(production1, (anything(), anything()), None)

        rule2_parent = Symbol('B')
        detector2 = create_autospec(Detector)
        detector2.configure_mock(coordinates=2)
        rule2 = create_autospec(Rule)
        rule2.configure_mock(parent=rule2_parent)
        production2 = Production(detector2, rule2)
        self.sut.add_production(production2, (anything(), anything()), None)

        # When:
        rules = list(self.sut.find_non_empty_productions(lambda x: x.rule.parent == Symbol('B')))

        # Then:
        assert_that(rules, only_contains(production2))

    def test_viterbi_should_work_well_with_terminal_productions(self):
        # Given:
        production = Production(self.detector, self.rule)
        production.probability = 0.5
        production2 = Production(self.detector, self.rule)
        production2.probability = 0.8

        # When:
        self.sut.add_production(production, None, viterbi_probability_approach)
        self.sut.add_production(production2, None, viterbi_probability_approach)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains(Symbol('A')))
        assert_that(self.sut.get_non_empty_productions(), only_contains(production))
        assert_that(self.sut.effector_probabilities[Symbol('A')], is_(equal_to(0.8)))

    def test_viterbi_should_work_well_with_non_terminal_productions(self):
        # Given:
        production = Production(self.detector, self.rule)
        production.probability = 0.5
        production2 = Production(self.detector, self.rule)
        production2.probability = 0.8

        # When:
        self.sut.add_production(production, (anything(), 0.4, anything(), 0.6),
                                viterbi_probability_approach)
        self.sut.add_production(production2, (anything(), 0.1, anything(), 0.5),
                                viterbi_probability_approach)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains(Symbol('A')))
        assert_that(self.sut.get_non_empty_productions(), only_contains(production))
        assert_that(self.sut.effector_probabilities[Symbol('A')], is_(equal_to(0.12)))

    def test_baum_welch_should_work_well_with_terminal_productions(self):
        # Given:
        production = Production(self.detector, self.rule)
        production.probability = 0.5
        production2 = Production(self.detector, self.rule)
        production2.probability = 0.8

        # When:
        self.sut.add_production(production, None, baum_welch_probability_approach)
        self.sut.add_production(production2, None, baum_welch_probability_approach)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains(Symbol('A')))
        assert_that(self.sut.get_non_empty_productions(), only_contains(production))
        assert_that(self.sut.effector_probabilities[Symbol('A')], is_(equal_to(1.3)))

    def test_baum_welch_should_work_well_with_non_terminal_productions(self):
        # Given:
        production = Production(self.detector, self.rule)
        production.probability = 0.5
        production2 = Production(self.detector, self.rule)
        production2.probability = 0.8

        # When:
        self.sut.add_production(production, (anything(), 0.4, anything(), 0.6),
                                baum_welch_probability_approach)
        self.sut.add_production(production2, (anything(), 0.1, anything(), 0.5),
                                baum_welch_probability_approach)

        # Then:
        assert_that(self.sut.is_empty(), is_(equal_to(False)))
        assert_that(self.sut.get_effectors(), only_contains(Symbol('A')))
        assert_that(self.sut.get_non_empty_productions(), only_contains(production))
        assert_that(self.sut.effector_probabilities[Symbol('A')], is_(equal_to(0.16)))

