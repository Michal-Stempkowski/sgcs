from core.symbol import Symbol, Sentence
from datalayer.data_fetcher import EagerFileFetcher
from datalayer.tokenizer import EagerTokenizer


class UnknownSymbol(Exception):
    def __init__(self, symbol):
        self.symbol = symbol

    def __str__(self):
        return repr(self.symbol)


class UnknownWord(Exception):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        return repr(self.word)


class SymbolTranslator(object):
    @staticmethod
    def create(path):
        file_fetcher = EagerFileFetcher(path)
        tokenizer = EagerTokenizer(file_fetcher)
        return SymbolTranslator(tokenizer)

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.new_id = -101
        self.word_to_id_map = dict()
        self.id_to_word_map = dict()
        self.sentences = list()

    def get_sentences(self):
        if not self.sentences:
            tokenized_sentences = self.tokenizer.get_token_generator()

            for tokenized_sentence in tokenized_sentences:
                words = list()
                is_positive = tokenized_sentence[0]
                for word in tokenized_sentence[1:]:
                    if word not in self.word_to_id_map:
                        self.word_to_id_map[word] = self.new_id
                        self.id_to_word_map[self.new_id] = word
                        self.new_id -= 1

                    words.append(self.word_to_symbol(word))

                sentence = Sentence(words, is_positive)
                self.sentences.append(sentence)
                yield sentence
        else:
            for sentence in self.sentences:
                yield sentence

    def symbol_to_word(self, symbol):
        result = self.id_to_word_map.get(symbol.symbol_id)
        if result is None:
            raise UnknownSymbol(symbol.symbol_id)
        return result

    def word_to_symbol(self, word):
        symbol_id = self.word_to_id_map.get(word)
        if symbol_id is None:
            raise UnknownWord(word)
        return Symbol(symbol_id)

    def rule_population_to_string(self, rule_population):
        name = type(rule_population).__name__
        header_format = 50, '+'
        str_buffer = [name.center(*header_format)]

        for rule in rule_population.get_terminal_rules():
            translated = rule.human_friendly_representation(rule_population.symbol_shift(),
                                                            rule_population.starting_symbol,
                                                            rule_population.universal_symbol)
            str_buffer.append("{0} => '{1}'".format(translated[0],
                                                  self.symbol_to_word(rule.left_child)))

        for rule in rule_population.get_all_non_terminal_rules():
            translated = rule.human_friendly_representation(rule_population.symbol_shift(),
                                                            rule_population.starting_symbol,
                                                            rule_population.universal_symbol)
            str_buffer.append('{0} => {1}; {2}'.format(*translated))

        str_buffer.append(' '.join([name, 'ends']).center(*header_format))

        return '\n'.join(str_buffer)

