from gui.dynamic_gui import AutoUpdater


class CrowdingAutoUpdater(AutoUpdater):
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
        options_configurator.bind_spinner(options_configurator.ui.crowdingFactorSpinBox)
        options_configurator.bind_spinner(options_configurator.ui.crowdingSizeSpinBox)

    @staticmethod
    def _update_model(options_configurator):
        options_configurator.configuration.rule.adding.crowding.factor = \
            options_configurator.ui.crowdingFactorSpinBox.value()
        options_configurator.configuration.rule.adding.crowding.size = \
            options_configurator.ui.crowdingSizeSpinBox.value()

    @staticmethod
    def _update_gui(options_configurator):
        options_configurator.ui.crowdingFactorSpinBox.setValue(
            options_configurator.configuration.rule.adding.crowding.factor)
        options_configurator.ui.crowdingSizeSpinBox.setValue(
            options_configurator.configuration.rule.adding.crowding.size)