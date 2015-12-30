from gui.dynamic_gui import AutoUpdater, NONE_LABEL, feed_with_data
from rule_adding import AddingRuleStrategyHint


class RulesAutoUpdater(AutoUpdater):
    RULE_ADDING_HINTS_MAP = {name: conf for name, conf in [
        (NONE_LABEL, None),
        ('expand population',
         AddingRuleStrategyHint.expand_population),

        ('control population size (elitism DISABLED)',
         AddingRuleStrategyHint.control_population_size),

        ('control population size (elitism ENABLED)',
         AddingRuleStrategyHint.control_population_size_with_elitism)
    ]}
    RIGHT_RULE_ADDING_HINTS_MAP = {conf: name for name, conf in RULE_ADDING_HINTS_MAP.items()}
    RULE_ADDING_HINTS = list(RULE_ADDING_HINTS_MAP.keys())

    def __init__(self, options_configurator):
        super().__init__(
            lambda: self._bind(options_configurator),
            lambda: self._update_model(options_configurator),
            lambda: self._update_gui(options_configurator),
            lambda: self._init_gui(options_configurator)
        )

    def _init_gui(self, options_configurator):
        feed_with_data(options_configurator.ui.ruleAddingHintComboBox, self.RULE_ADDING_HINTS)

    @staticmethod
    def _bind(options_configurator):
        options_configurator.bind_combobox(options_configurator.ui.ruleAddingHintComboBox)

        options_configurator.bind_spinner(options_configurator.ui.maxNonTerminalsSizeSpinBox)

        options_configurator.bind_spinner(options_configurator.ui.startingPopulationSizeSpinBox)

        options_configurator.bind_spinner(options_configurator.ui.maxNonTerminalSymbolsSpinBox)

    def _update_model(self, options_configurator):
        adding_hint = self.RULE_ADDING_HINTS_MAP[
            options_configurator.ui.ruleAddingHintComboBox.currentText()]
        options_configurator.configuration.induction.coverage.operators.starting.adding_hint = \
            adding_hint
        options_configurator.configuration.induction.coverage.operators.aggressive.adding_hint = \
            adding_hint
        options_configurator.configuration.induction.coverage.operators.full.adding_hint = \
            adding_hint

        options_configurator.configuration.rule.adding.max_non_terminal_rules = \
            options_configurator.ui.maxNonTerminalsSizeSpinBox.value()

        options_configurator.configuration.rule.adding.max_non_terminal_rules = \
            options_configurator.ui.maxNonTerminalsSizeSpinBox.value()

        options_configurator.configuration.rule.random_starting_population_size = \
            options_configurator.ui.startingPopulationSizeSpinBox.value()

        options_configurator.configuration.rule.max_non_terminal_symbols = \
            options_configurator.ui.maxNonTerminalSymbolsSpinBox.value()

    def _update_gui(self, options_configurator):
        hint = options_configurator.configuration.induction.coverage.operators.starting.adding_hint
        text = self.RIGHT_RULE_ADDING_HINTS_MAP[hint]
        index = options_configurator.ui.ruleAddingHintComboBox.findText(text)
        options_configurator.ui.ruleAddingHintComboBox.setCurrentIndex(index)

        options_configurator.ui.maxNonTerminalsSizeSpinBox.setValue(
            options_configurator.configuration.rule.adding.max_non_terminal_rules)
        options_configurator.ui.startingPopulationSizeSpinBox.setValue(
            options_configurator.configuration.rule.random_starting_population_size)
        options_configurator.ui.maxNonTerminalSymbolsSpinBox.setValue(
            options_configurator.configuration.rule.max_non_terminal_symbols)