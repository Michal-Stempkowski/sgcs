from datalayer.symbol_translator import SymbolTranslator


class RuleModel(object):
    def __init__(self, is_terminal):
        self.is_terminal = is_terminal
        self.parent = ''
        self.left_child = ''
        self.right_child = ''


class TerminalRuleModel(RuleModel):
    def __init__(self):
        super().__init__(True)


class NonTerminalRuleModel(RuleModel):
    def __init__(self):
        super().__init__(False)


class PopulationExecutor(object):
    @staticmethod
    def get_learned_translator(population_path):
        symbol_translator = SymbolTranslator.create(population_path)
        list(symbol_translator.get_sentences())
        return symbol_translator
