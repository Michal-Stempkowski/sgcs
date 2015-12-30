from gui.dynamic_gui import AutoUpdater


class ElitismAutoUpdater(AutoUpdater):
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
        options_configurator.bind_checkbox(options_configurator.ui.isElitismUsedCheckBox)
        options_configurator.bind_spinner(options_configurator.ui.eliteSizeSpinBox)

    @staticmethod
    def _update_model(options_configurator):
        options_configurator.configuration.rule.adding.elitism.is_used = \
            options_configurator.ui.isElitismUsedCheckBox.isChecked()

        options_configurator.configuration.rule.adding.elitism.size = \
            options_configurator.ui.eliteSizeSpinBox.value()

    @staticmethod
    def _update_gui(options_configurator):
        options_configurator.ui.isElitismUsedCheckBox.setChecked(
            options_configurator.configuration.rule.adding.elitism.is_used)

        options_configurator.ui.eliteSizeSpinBox.setValue(
            options_configurator.configuration.rule.adding.elitism.size)