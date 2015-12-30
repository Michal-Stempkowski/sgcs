from gui.dynamic_gui import AutoUpdater


class ClassicalStatisticsAutoUpdater(AutoUpdater):
    def __init__(self, options_configurator):
        super().__init__(
            lambda: self._bind(options_configurator),
            lambda: self._update_model(options_configurator),
            lambda: self._update_gui(options_configurator),
            lambda: self._init_gui(options_configurator)
        )

    def _init_gui(self, options_configurator):
        pass

    @staticmethod
    def _bind(options_configurator):
        options_configurator.bind_spinner(options_configurator.ui.baseFitnessDoubleSpinBox)

        options_configurator.bind_spinner(options_configurator.ui.fitnessWeightDoubleSpinBox)

        options_configurator.bind_spinner(options_configurator.ui.fertilityWeightDoubleSpinBox)

        options_configurator.bind_spinner(options_configurator.ui.validSentencePriceDoubleSpinBox)

        options_configurator.bind_spinner(options_configurator.ui.invalidSentencePriceDoubleSpinBox)

        options_configurator.bind_spinner(
            options_configurator.ui.positiveSentenceWeightDoubleSpinBox)

        options_configurator.bind_spinner(
            options_configurator.ui.negativeSentenceWeightDoubleSpinBox)

    @staticmethod
    def _update_model(options_configurator):
        options_configurator.configuration.statistics.base_fitness = \
            options_configurator.ui.baseFitnessDoubleSpinBox.value()

        options_configurator.configuration.statistics.classical_fitness_weight = \
            options_configurator.ui.fitnessWeightDoubleSpinBox.value()

        options_configurator.configuration.statistics.fertility_weight = \
            options_configurator.ui.fertilityWeightDoubleSpinBox.value()

        options_configurator.configuration.statistics.valid_sentence_price = \
            options_configurator.ui.validSentencePriceDoubleSpinBox.value()

        options_configurator.configuration.statistics.invalid_sentence_price = \
            options_configurator.ui.invalidSentencePriceDoubleSpinBox.value()

        options_configurator.configuration.statistics.positive_weight = \
            options_configurator.ui.positiveSentenceWeightDoubleSpinBox.value()

        options_configurator.configuration.statistics.negative_weight = \
            options_configurator.ui.negativeSentenceWeightDoubleSpinBox.value()

    @staticmethod
    def _update_gui(options_configurator):
        options_configurator.ui.baseFitnessDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.base_fitness)

        options_configurator.ui.fitnessWeightDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.classical_fitness_weight)

        options_configurator.ui.fertilityWeightDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.fertility_weight)

        options_configurator.ui.validSentencePriceDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.valid_sentence_price)

        options_configurator.ui.invalidSentencePriceDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.invalid_sentence_price)

        options_configurator.ui.positiveSentenceWeightDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.positive_weight)

        options_configurator.ui.negativeSentenceWeightDoubleSpinBox.setValue(
            options_configurator.configuration.statistics.negative_weight)