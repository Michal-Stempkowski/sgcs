import unittest
from unittest.mock import create_autospec, PropertyMock, call
from hamcrest import *
from sgcs.factory import Factory
from sgcs.induction.cyk_executors import CykTypeId
from sgcs.induction.detector import Detector
from sgcs.induction.environment import Environment, CykTableIndexError
from sgcs.induction.production import Production, ProductionPool
from sgcs.induction.rule import Rule, TerminalRule
from sgcs.induction.symbol import Sentence, Symbol
from sgcs.tests.test_common import are_


class TestEnvironment(unittest.TestCase):
    table_size = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentence_mock = create_autospec(Sentence)
        self.sentence_mock.__len__.return_value = TestEnvironment.table_size
        self.production_pool_mock = create_autospec(ProductionPool)
        self.executor_factory = Factory(
            {
                CykTypeId.production_pool: lambda *args: self.production_pool_mock
            })
        self.sut = Environment(self.sentence_mock, self.executor_factory)

    def test_get_sentence_length_should_work(self):
        assert_that(self.sut.get_sentence_length(), is_(equal_to(TestEnvironment.table_size)))

    def test_get_row_length_should_work(self):
        assert_that(self.sut.get_row_length(0), is_(4))
        assert_that(self.sut.get_row_length(1), is_(3))
        assert_that(self.sut.get_row_length(2), is_(2))
        assert_that(self.sut.get_row_length(3), is_(1))

    def production_with(self, row, col, shift, left_id, right_id, effector):
        return Production(
            Detector((row, col, shift, left_id, right_id)),
            Rule(effector, Symbol('A'), Symbol('B')))

    def terminal_production_with(self, row, col, shift, left_id, right_id, effector, terminal):
        return Production(
            Detector((row, col, shift, left_id, right_id)),
            TerminalRule(effector, Symbol(terminal)))

    def test_adding_productions_should_work_properly(self):
        # Given:
        p1 = self.production_with(1, 0, 1, 0, 0, Symbol('A'))
        p2 = self.production_with(1, 0, 1, 0, 1, Symbol('B'))

        # When/Then:
        self.sut.add_production(p1)
        self.sut.add_production(p2)
        self.production_pool_mock.add_production.assert_has_calls([call(p1), call(p2)])

        new_symbol = Symbol('D')
        assert_that(calling(self.sut.add_production).with_args(
            self.production_with(-1, 0, 1, 0, 0, new_symbol)),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.add_production).with_args(
            self.production_with(1, -1, 1, 0, 0, new_symbol)),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.add_production).with_args(
            self.production_with(2, 4, 1, 0, 0, new_symbol)),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.add_production).with_args(
            self.production_with(4, 2, 1, 0, 0, new_symbol)),
                    raises(CykTableIndexError))

    def test_should_be_able_to_retrieve_any_symbol_from_sentence(self):
        self.sentence_mock.get_symbol.side_effect = [Symbol(1), Symbol(2), Symbol(3)]

        assert_that(self.sut.get_sentence_symbol(1), is_(equal_to(Symbol(1))))
        assert_that(self.sut.get_sentence_symbol(2), is_(equal_to(Symbol(2))))
        assert_that(self.sut.get_sentence_symbol(3), is_(equal_to(Symbol(3))))

    def test_should_be_able_to_get_detector_symbols(self):
        self.production_pool_mock.get_effectors.side_effect = \
            [['D'], ['E', 'Q']]

        unshifted_parent_coords = (3, 0, 2, 0, 1)

        assert_that(self.sut.get_detector_symbols(unshifted_parent_coords),
                    is_(equal_to(('D', 'Q'))))

    def test_should_be_able_to_get_unsatisfied_detectors(self):
        # Given:
        coordinates = (2, 2)
        self.production_pool_mock.get_unsatisfied_detectors.return_value = [Detector(coordinates)]

        # When:
        result = self.sut.get_unsatisfied_detectors(coordinates)

        # Then:
        assert_that(result, only_contains(Detector(coordinates)))

    def test_should_be_able_to_get_productions_from_last_cell(self):
        # Given:
        p1 = self.production_with(1, 0, 1, 0, 0, Symbol('A'))
        p2 = self.production_with(1, 0, 1, 0, 1, Symbol('B'))
        self.production_pool_mock.get_non_empty_productions.return_value = [p1, p2]

        # When:
        productions = self.sut.get_last_cell_productions()

        # Then:
        self.production_pool_mock.get_non_empty_productions.assert_has_calls([call()])
        assert_that(productions, contains_inanyorder(p1, p2))

    def test_should_be_able_to_get_parent_productions(self):
        # Given:
        p0 = self.production_with(1, 0, 1, 0, 0, Symbol('C'))
        p1 = self.terminal_production_with(1, 0, 1, 0, 0, Symbol('A'), Symbol('a'))
        p2 = self.terminal_production_with(1, 0, 1, 0, 1, Symbol('B'), Symbol('b'))
        p3 = self.terminal_production_with(1, 0, 1, 0, 1, Symbol('Y'), Symbol('y'))
        self.production_pool_mock.find_non_empty_productions.side_effect = [(p1, p2), (p3,)]

        # When:
        p0_productions = list(self.sut.get_child_productions(p0))
        p1_productions = list(self.sut.get_child_productions(p1))
        p2_productions = list(self.sut.get_child_productions(p2))
        p3_productions = list(self.sut.get_child_productions(p3))

        # Then:
        assert_that(p0_productions, contains_inanyorder(p1, p2, p3))
        assert_that(p1_productions, is_(empty()))
        assert_that(p2_productions, is_(empty()))
        assert_that(p3_productions, is_(empty()))
