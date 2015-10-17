import unittest
from unittest.mock import create_autospec, PropertyMock
from hamcrest import *
from sgcs.induction.environment import Environment, CykTableIndexError
from sgcs.induction.symbol import Sentence, Symbol


class TestEnvironment(unittest.TestCase):
    table_size = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sentence_mock = create_autospec(Sentence)
        self.sentence_mock.__len__.return_value = TestEnvironment.table_size
        self.sut = Environment(self.sentence_mock)

    def test_get_sentence_length_should_work(self):
        assert_that(self.sut.get_sentence_length(), is_(equal_to(TestEnvironment.table_size)))

    def test_get_row_length_should_work(self):
        assert_that(self.sut.get_row_length(0), is_(4))
        assert_that(self.sut.get_row_length(1), is_(3))
        assert_that(self.sut.get_row_length(2), is_(2))
        assert_that(self.sut.get_row_length(3), is_(1))

    def test_adding_symbols_should_work_properly(self):
        # Given:
        new_symbols = {'A', 'B'}

        # When/Then:
        self.sut.add_symbols((2, 2), new_symbols)

        assert_that(self.sut.cyk_table[2][2], contains_inanyorder(*new_symbols))

        assert_that(calling(self.sut.add_symbols).with_args((-1, 2), new_symbols),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.add_symbols).with_args((2, -1), new_symbols),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.add_symbols).with_args((2, 4), new_symbols),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.add_symbols).with_args((4, 2), new_symbols),
                    raises(CykTableIndexError))

    def test_getting_symbols_should_work_properly(self):
        # Given:
        current_symbols = {'A', 'B'}
        current_coord = (3, 0)
        self.sut.add_symbols(current_coord, current_symbols)

        left_parent_symbols = {'D'}
        left_parent_coord = (1, 0)
        self.sut.add_symbols(left_parent_coord, left_parent_symbols)

        right_parent_symbols = {'Z', 'Q', 'G'}
        right_parent_coord = (1, 2)
        self.sut.add_symbols(right_parent_coord, right_parent_symbols)

        unshifted_parent_coords = (3, 0, 2)

        # When/Then:
        assert_that(self.sut.get_symbols(current_coord), contains_inanyorder(*current_symbols))

        assert_that(self.sut.get_left_parent_symbol_count(unshifted_parent_coords),
                    is_(equal_to(1)))

        assert_that(self.sut.get_right_parent_symbol_count(unshifted_parent_coords),
                    is_(equal_to(3)))

        assert_that(calling(self.sut.get_symbols).with_args((-1, 2)),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.get_symbols).with_args((2, -1)),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.get_symbols).with_args((2, 4)),
                    raises(CykTableIndexError))
        assert_that(calling(self.sut.get_symbols).with_args((4, 2)),
                    raises(CykTableIndexError))

    def test_should_be_able_to_retrieve_any_symbol_from_sentence(self):
        self.sentence_mock.get_symbol.side_effect = [Symbol(1), Symbol(2), Symbol(3)]

        assert_that(self.sut.get_sentence_symbol(1), is_(equal_to(Symbol(1))))
        assert_that(self.sut.get_sentence_symbol(2), is_(equal_to(Symbol(2))))
        assert_that(self.sut.get_sentence_symbol(3), is_(equal_to(Symbol(3))))

    def test_should_be_able_to_get_detector_symbols(self):
        left_parent_symbols = {'D'}
        left_parent_coord = (1, 0)
        self.sut.add_symbols(left_parent_coord, left_parent_symbols)

        right_parent_symbols = ['Z', 'Q', 'G']
        right_parent_coord = (1, 2)
        self.sut.add_symbols(right_parent_coord, right_parent_symbols)

        unshifted_parent_coords = (3, 0, 2, 0, 1)

        assert_that(self.sut.get_detector_symbols(unshifted_parent_coords),
                    is_(equal_to(('D', 'Q'))))
