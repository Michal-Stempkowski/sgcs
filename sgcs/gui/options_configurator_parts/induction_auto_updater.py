from gui.dynamic_gui import AutoUpdater


class InductionAutoUpdater(AutoUpdater):
    def __init__(self, options_configurator):
        super().__init__(
            lambda: self._bind(options_configurator),
            lambda: self._update_model(options_configurator),
            lambda: self._update_gui(options_configurator),
            lambda: self._init_gui(options_configurator)
        )

    @staticmethod
    def _init_gui(options_configurator):
        pass

    @staticmethod
    def _bind(options_configurator):
        options_configurator.bind_spinner(
            options_configurator.ui.terminalProbabilityDoubleSpinBox
        )
        options_configurator.bind_spinner(
            options_configurator.ui.universalProbabilityDoubleSpinBox
        )
        options_configurator.bind_spinner(
            options_configurator.ui.aggressiveProbabilityDoubleSpinBox
        )
        options_configurator.bind_spinner(
            options_configurator.ui.startingProbabilityDoubleSpinBox
        )
        options_configurator.bind_spinner(
            options_configurator.ui.fullProbabilityDoubleSpinBox
        )
        options_configurator.bind_checkbox(
            options_configurator.ui.grammarCorrectionCheckBox
        )

    @staticmethod
    def _update_model(options_configurator):
        options_configurator.configuration.induction.coverage.operators.terminal.chance = \
            options_configurator.ui.terminalProbabilityDoubleSpinBox.value()

        options_configurator.configuration.induction.coverage.operators.universal.chance = \
            options_configurator.ui.universalProbabilityDoubleSpinBox.value()

        options_configurator.configuration.induction.coverage.operators.aggressive.chance = \
            options_configurator.ui.aggressiveProbabilityDoubleSpinBox.value()

        options_configurator.configuration.induction.coverage.operators.starting.chance = \
            options_configurator.ui.startingProbabilityDoubleSpinBox.value()

        options_configurator.configuration.induction.coverage.operators.full.chance = \
            options_configurator.ui.fullProbabilityDoubleSpinBox.value()

        options_configurator.configuration.induction.grammar_correction.should_run = \
            options_configurator.ui.grammarCorrectionCheckBox.isChecked()

    @staticmethod
    def _update_gui(options_configurator):
        options_configurator.ui.terminalProbabilityDoubleSpinBox.setValue(
            options_configurator.configuration.induction.coverage.operators.terminal.chance
        )
        options_configurator.ui.universalProbabilityDoubleSpinBox.setValue(
            options_configurator.configuration.induction.coverage.operators.universal.chance
        )
        options_configurator.ui.aggressiveProbabilityDoubleSpinBox.setValue(
            options_configurator.configuration.induction.coverage.operators.aggressive.chance
        )
        options_configurator.ui.startingProbabilityDoubleSpinBox.setValue(
            options_configurator.configuration.induction.coverage.operators.starting.chance
        )
        options_configurator.ui.fullProbabilityDoubleSpinBox.setValue(
            options_configurator.configuration.induction.coverage.operators.full.chance
        )
        options_configurator.ui.grammarCorrectionCheckBox.setChecked(
            options_configurator.configuration.induction.grammar_correction.should_run
        )