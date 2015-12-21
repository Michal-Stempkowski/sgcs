from algorithm.gcs_runner import AlgorithmConfiguration
from evolution.evolution_configuration import *
from gui.generated.options_configurator__gen import Ui_OptionsConfiguratorGen
from gui.generic_widget import GenericWidget


class AlgorithmVariant(object):
    @staticmethod
    def mk_pairs(*variants):
        return ((v.name, v) for v in variants)

    def __init__(self, name):
        self.name = name


class SGcsAlgorithmVariant(AlgorithmVariant):
    def __init__(self):
        super().__init__('sGCS')


class GcsAlgorithmVariant(AlgorithmVariant):
    def __init__(self):
        super().__init__('GCS')


class OptionsConfigurator(GenericWidget):
    ALGORITHM_VARIANTS = {n: v for n, v in AlgorithmVariant.mk_pairs(
        SGcsAlgorithmVariant(),
        GcsAlgorithmVariant()
    )}
    EVOLUTION_SELECTOR_MAP = {name: conf for name, conf in [
        ('no selector', None),
        ('random', EvolutionRandomSelectorConfiguration.create),
        ('tournament', EvolutionTournamentSelectorConfiguration.create),
        ('roulette', EvolutionRouletteSelectorConfiguration.create)
    ]}
    DEFAULT_SELECTOR = 'no selector'
    LETTER_SYMBOLS = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    NONE_LABEL = '<None>'
    LETTER_SYMBOLS_WITH_NONE = [NONE_LABEL] + LETTER_SYMBOLS
    DEFAULT_STARTING_SYMBOL = 'S'
    RULE_ADDING_HINTS = [NONE_LABEL] + [
        'expand population',
        'control population size (elitism DISABLED)',
        'control population size (elitism ENABLED)'
    ]
    VARIANT_CREATOR_MAP = dict(
        sGCS=AlgorithmConfiguration.sgcs_variant,
        GCS=AlgorithmConfiguration.default
    )

    @staticmethod
    def feed_with_data(widget, data, default_item=None):
        if default_item is None:
            items = data
        else:
            items = [default_item]
            items += filter(lambda x: x != default_item, data)
        widget.addItems(items)
        widget.setCurrentIndex(0)

    def __init__(self, last_directory):
        super().__init__(Ui_OptionsConfiguratorGen)
        self.last_directory = last_directory

        self.selector_combo_boxes = [
            self.ui.selectorComboBox,
            self.ui.selectorComboBox_2,
            self.ui.selectorComboBox_3,
            self.ui.selectorComboBox_4,
            self.ui.selectorComboBox_5,
            self.ui.selectorComboBox_6,
            self.ui.selectorComboBox_7,
            self.ui.selectorComboBox_8,
            self.ui.selectorComboBox_9,
            self.ui.selectorComboBox_10
        ]
        self.selector_spin_boxes = [
            self.ui.selectorSpinBox,
            self.ui.selectorSpinBox_2,
            self.ui.selectorSpinBox_3,
            self.ui.selectorSpinBox_4,
            self.ui.selectorSpinBox_5,
            self.ui.selectorSpinBox_6,
            self.ui.selectorSpinBox_7,
            self.ui.selectorSpinBox_8,
            self.ui.selectorSpinBox_9,
            self.ui.selectorSpinBox_10
        ]
        self.feed_with_data(self.ui.algorithmVariantComboBox, list(self.ALGORITHM_VARIANTS.keys()))
        self.configuration = self.VARIANT_CREATOR_MAP[
            self.ui.algorithmVariantComboBox.currentText()]()

        self.init_gui()

    def init_gui(self):

        fields = list(self.EVOLUTION_SELECTOR_MAP.keys())
        for combo in self.selector_combo_boxes:
            self.feed_with_data(combo, fields, self.DEFAULT_SELECTOR)

        self.feed_with_data(self.ui.startingSymbolComboBox, self.LETTER_SYMBOLS,
                            self.DEFAULT_STARTING_SYMBOL)
        self.feed_with_data(self.ui.universalSymbolComboBox, self.LETTER_SYMBOLS_WITH_NONE)
        self.feed_with_data(self.ui.ruleAddingHintComboBox, self.RULE_ADDING_HINTS)

        self.reset_gui()

    def reset_gui(self):
        for spinner in self.selector_spin_boxes:
            spinner.setValue(1)
            spinner.setMinimum(1)
            spinner.setMaximum(20)
