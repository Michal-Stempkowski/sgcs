import os
import unittest
from unittest.mock import create_autospec

from hamcrest import *

from datalayer.data_fetcher import EagerFileFetcher, LazyFileFetcher
from datalayer.symbol_translator import SymbolTranslator
from datalayer.tokenizer import EagerTokenizer


class LongTestDataRead(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dir_path = r"C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\data\example gramatics"
        self.filename = 'toy opt los 65534'

        self.data_fetcher = EagerFileFetcher(os.path.join(self.dir_path, self.filename))
        self.tokenizer = EagerTokenizer(self.data_fetcher)
        self.sut = SymbolTranslator(self.tokenizer)

    def perform_long_double_read_scenario(self, sentences):
        for sentence in sentences:
            assert_that(sentence.is_positive_sentence, is_(not_none()))
            for s in sentence.symbols:
                assert_that(s.symbol_id, is_(less_than_or_equal_to(-101)))
                assert_that(s.symbol_id, is_(greater_than_or_equal_to(-104)))

    def test_big_data_read(self):
        sentences = self.sut.get_sentences()
        self.perform_long_double_read_scenario(sentences)

    def test_big_data_read_with_buffering(self):
        sentences = self.sut.get_sentences()
        self.perform_long_double_read_scenario(sentences)

        sentences = self.sut.get_sentences()
        self.perform_long_double_read_scenario(sentences)
