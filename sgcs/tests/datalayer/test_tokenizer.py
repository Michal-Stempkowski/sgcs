import unittest
from unittest.mock import create_autospec

from hamcrest import *

from datalayer.data_fetcher import EagerFileFetcher
from datalayer.tokenizer import EagerTokenizer


class TestTokenizer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data_fetcher_mock = create_autospec(EagerFileFetcher)
        self.sut = EagerTokenizer(self.data_fetcher_mock)

    def test_should_tokenize_sentences_well(self):
        # Given:
        self.data_fetcher_mock.get_chunk_generator.return_value = (x for x in ["2 5",
                                                                               "1 3 Ala ma kota\n",
                                                                               "      \n",
                                                                               "1 3 Kot ma Ale\n"])

        # When:
        token_generator = self.sut.get_token_generator()

        # Then:
        assert_that(next(token_generator), contains(True, "ala", "ma", "kota"))
        assert_that(next(token_generator), contains(True, "kot", "ma", "ale"))
        assert_that(calling(next).with_args(token_generator), raises(StopIteration))
