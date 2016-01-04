import json
import os

from PyQt4 import QtGui

from algorithm.gcs_runner import AlgorithmConfiguration
from algorithm.gcs_runner import RuleConfiguration
from core.symbol import Symbol
from datalayer.jsonizer import ConfigurationJsonizer
from evolution.evolution_configuration import EvolutionConfiguration, EvolutionOperatorConfiguration, \
    EvolutionOperatorsConfiguration, EvolutionSelectorConfiguration, \
    EvolutionRandomSelectorConfiguration, EvolutionTournamentSelectorConfiguration, \
    EvolutionRouletteSelectorConfiguration
from gui.dynamic_gui import AutoUpdater
from induction.cyk_configuration import CoverageConfiguration, CoverageOperatorConfiguration, \
    CoverageOperatorsConfiguration, CykConfiguration, GrammarCorrection
from rule_adding import AddingRulesConfiguration, CrowdingConfiguration, ElitismConfiguration
from statistics.grammar_statistics import ClassicalStatisticsConfiguration


class MainBoxAutoUpdater(AutoUpdater):
    def __init__(self, options_configurator):
        super().__init__(
            lambda: self._bind(options_configurator),
            lambda: self._update_model(options_configurator),
            lambda: self._update_gui(options_configurator),
            lambda: self._init_gui(options_configurator)
        )
        self.serializer = ConfigurationJsonizer([
            AddingRulesConfiguration,
            CrowdingConfiguration,
            ElitismConfiguration,
            AlgorithmConfiguration,
            RuleConfiguration,
            Symbol,
            EvolutionConfiguration,
            EvolutionOperatorConfiguration,
            EvolutionOperatorsConfiguration,
            EvolutionSelectorConfiguration,
            CoverageConfiguration,
            CoverageOperatorConfiguration,
            CoverageOperatorsConfiguration,
            CykConfiguration,
            GrammarCorrection,
            ClassicalStatisticsConfiguration,
            EvolutionRandomSelectorConfiguration,
            EvolutionTournamentSelectorConfiguration,
            EvolutionRouletteSelectorConfiguration
        ])

    @staticmethod
    def _init_gui(options_configurator):
        pass

    def _bind(self, options_configurator):
        options_configurator.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(
            lambda: self.on_reset_clicked(options_configurator))
        options_configurator.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.connect(
            lambda: self.on_save_clicked(options_configurator))
        options_configurator.ui.buttonBox.button(QtGui.QDialogButtonBox.Open).clicked.connect(
            lambda: self.on_open_clicked(options_configurator))

    @staticmethod
    def on_reset_clicked(options_configurator):
        options_configurator.on_variant_changed(options_configurator.current_variant.name)

    def on_save_clicked(self, options_configurator):
        selected_filename = QtGui.QFileDialog.getSaveFileName(
            options_configurator.widget, 'Save configuration as...',
            options_configurator.last_directory, "*.parconf")

        if selected_filename:
            options_configurator.last_directory = os.path.dirname(selected_filename)
            with open(selected_filename, 'w+') as f:
                json.dump(self.serializer.to_json(options_configurator.configuration), f,
                          sort_keys=True, indent=4)

    def on_open_clicked(self, options_configurator):
        selected_filename = QtGui.QFileDialog.getOpenFileName(
            options_configurator.widget, 'Load configuration...',
            options_configurator.last_directory, "*.parconf")

        if selected_filename:
            options_configurator.last_directory = os.path.dirname(selected_filename)
            with open(selected_filename) as f:
                configuration = self.serializer.from_json(json.load(f))
            options_configurator.on_variant_changed(configuration.algorithm_variant)
            options_configurator.configuration = configuration
            options_configurator.variant_changed__reset_gui()

    @staticmethod
    def _update_model(options_configurator):
        pass

    @staticmethod
    def _update_gui(options_configurator):
        pass
