from gui.dynamic_gui import AutoUpdater


class EvolutionAutoUpdater(AutoUpdater):
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
        options_configurator.bind_spinner(options_configurator.ui.inversionDoubleSpinBox)
        options_configurator.bind_spinner(options_configurator.ui.mutationDoubleSpinBox)
        options_configurator.bind_spinner(options_configurator.ui.crossoverDoubleSpinBox)

    @staticmethod
    def _update_model(options_configurator):
        options_configurator.configuration.evolution.operators.inversion.chance = \
            options_configurator.ui.inversionDoubleSpinBox.value()
        options_configurator.configuration.evolution.operators.mutation.chance = \
            options_configurator.ui.mutationDoubleSpinBox.value()
        options_configurator.configuration.evolution.operators.crossover.chance = \
            options_configurator.ui.crossoverDoubleSpinBox.value()

    @staticmethod
    def _update_gui(options_configurator):
        options_configurator.ui.inversionDoubleSpinBox.setValue(
            options_configurator.configuration.evolution.operators.inversion.chance)
        options_configurator.ui.mutationDoubleSpinBox.setValue(
            options_configurator.configuration.evolution.operators.mutation.chance)
        options_configurator.ui.crossoverDoubleSpinBox.setValue(
            options_configurator.configuration.evolution.operators.crossover.chance)