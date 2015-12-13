import unittest
from unittest.mock import create_autospec

from hamcrest import *

from core.symbol import Symbol, Sentence
from datalayer.symbol_translator import SymbolTranslator, UnknownSymbol, UnknownWord
from datalayer.tokenizer import EagerTokenizer


class TestSymbolTranslator(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.tokenizer_mock = create_autospec(EagerTokenizer)
        self.sut = SymbolTranslator(self.tokenizer_mock)

    def perform_get_sentences_scenario(self, sentences):
        first_sentence = next(sentences)
        second_sentence = next(sentences)

        # Then:
        assert_that(calling(next).with_args(sentences), raises(StopIteration))
        assert_that(first_sentence, is_(equal_to(
            Sentence([Symbol(-101), Symbol(-102), Symbol(-103)], is_positive_sentence=True))))
        assert_that(second_sentence, is_(equal_to(
            Sentence([Symbol(-104), Symbol(-102), Symbol(-105)], is_positive_sentence=False))))

        assert_that(self.sut.symbol_to_word(Symbol(-101)), is_(equal_to('ala')))
        assert_that(self.sut.symbol_to_word(Symbol(-102)), is_(equal_to('ma')))
        assert_that(self.sut.symbol_to_word(Symbol(-103)), is_(equal_to('kota')))
        assert_that(self.sut.symbol_to_word(Symbol(-104)), is_(equal_to('kot')))
        assert_that(self.sut.symbol_to_word(Symbol(-105)), is_(equal_to('ale')))
        assert_that(calling(self.sut.symbol_to_word).with_args(Symbol(-106)), raises(UnknownSymbol))

        assert_that(self.sut.word_to_symbol('ala'), is_(equal_to(Symbol(-101))))
        assert_that(self.sut.word_to_symbol('ma'), is_(equal_to(Symbol(-102))))
        assert_that(self.sut.word_to_symbol('kota'), is_(equal_to(Symbol(-103))))
        assert_that(self.sut.word_to_symbol('kot'), is_(equal_to(Symbol(-104))))
        assert_that(self.sut.word_to_symbol('ale'), is_(equal_to(Symbol(-105))))
        assert_that(calling(self.sut.word_to_symbol).with_args('andrzej'), raises(UnknownWord))

    def test_should_be_able_to_get_translated_sentence_generator(self):
        self.tokenizer_mock.get_token_generator.return_value = (iter([
            [True, 'ala', 'ma', 'kota'],
            [False, 'kot', 'ma', 'ale']
        ]))

        sentences = self.sut.get_sentences()
        self.perform_get_sentences_scenario(sentences)
        self.tokenizer_mock.get_token_generator.assert_called_once_with()
        self.tokenizer_mock.get_token_generator.reset_mock()

        sentences = self.sut.get_sentences()
        self.perform_get_sentences_scenario(sentences)
        assert_that(is_not(self.tokenizer_mock.get_token_generator.called))
        self.tokenizer_mock.get_token_generator.reset_mock()

        sentences = self.sut.get_sentences()
        self.perform_get_sentences_scenario(sentences)
        assert_that(is_not(self.tokenizer_mock.get_token_generator.called))

    def test_if_negative_sentences_disabled__they_should_be_ignored(self):
        self.sut.negative_allowed = False
        self.tokenizer_mock.get_token_generator.return_value = (iter([
            [True, 'ala', 'ma', 'kota'],
            [False, 'kot', 'ma', 'ale']
        ]))

        sentences = self.sut.get_sentences()
        assert_that(list(sentences), has_length(1))

