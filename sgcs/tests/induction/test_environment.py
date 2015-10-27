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
