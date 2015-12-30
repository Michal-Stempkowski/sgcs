from gui.dynamic_gui import AutoUpdater
from statistics.grammar_statistics import ClassicalStatisticsConfiguration


class Statistics(object):
    pasieka = 'pasieka'
    classical = 'classical'


class RootAutoUpdater(AutoUpdater):
    STATISTICS_CONFIGURATION_MAP = {
        'pasieka': lambda: None,
        'classical': ClassicalStatisticsConfiguration.default
    }
    RIGHT_STATISTICS_CONFIGURATION_MAP = type('StatisticsTranslator', (object,), dict(
        __getitem__=lambda _, instance: 'pasieka' if instance is None else 'classical'))()

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
        options_configurator.bind_checkbox(options_configurator.ui.shouldRunEvolutionCheckBox)
        options_configurator.bind_spinner(options_configurator.ui.maxAlgorithmRunsSpinBox)
        options_configurator.bind_spinner(options_configurator.ui.maxExecutionTimeSpinBox)
        options_configurator.bind_spinner(options_configurator.ui.maxEvolutionStepsSpinBox)
        options_configurator.bind_spinner(options_configurator.ui.satisfyingFitnessDoubleSpinBox)
        options_configurator.bind_combobox(options_configurator.ui.selectedStatisticsComboBox)

    @staticmethod
    def _update_gui(options_configurator):
        options_configurator.ui.shouldRunEvolutionCheckBox.setChecked(
            options_configurator.configuration.should_run_evolution)
        options_configurator.ui.maxAlgorithmRunsSpinBox.setValue(
            options_configurator.configuration.max_algorithm_runs)
        options_configurator.ui.maxExecutionTimeSpinBox.setValue(
            options_configurator.configuration.max_execution_time)
        options_configurator.ui.maxEvolutionStepsSpinBox.setValue(
            options_configurator.configuration.max_algorithm_steps)
        options_configurator.ui.satisfyingFitnessDoubleSpinBox.setValue(
            options_configurator.configuration.satisfying_fitness * 100.)

        # statistics = options_configurator.configuration.statistics
        # # noinspection PyUnresolvedReferences
        # text = self.RIGHT_STATISTICS_CONFIGURATION_MAP[statistics]
        # index = options_configurator.ui.selectedStatisticsComboBox.findText(text)
        # options_configurator.ui.selectedStatisticsComboBox.setCurrentIndex(index)

    @staticmethod
    def _update_model(options_configurator):
        options_configurator.configuration.should_run_evolution = \
            options_configurator.ui.shouldRunEvolutionCheckBox.isChecked()
        options_configurator.configuration.max_algorithm_runs = \
            options_configurator.ui.maxAlgorithmRunsSpinBox.value()
        options_configurator.configuration.max_execution_time = \
            options_configurator.ui.maxExecutionTimeSpinBox.value()
        options_configurator.configuration.max_algorithm_steps = \
            options_configurator.ui.maxEvolutionStepsSpinBox.value()
        options_configurator.configuration.satisfying_fitness = \
            options_configurator.ui.satisfyingFitnessDoubleSpinBox.value() / 100.

        # text = options_configurator.ui.selectedStatisticsComboBox.currentText()
        # statistics = self.STATISTICS_CONFIGURATION_MAP[text]()
        # options_configurator.configuration.statistics = statistics