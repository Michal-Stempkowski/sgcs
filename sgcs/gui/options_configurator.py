import logging
from abc import abstractmethod

from algorithm.gcs_runner import AlgorithmConfiguration, RuleConfiguration
from core.symbol import Symbol
from datalayer.jsonizer import BasicJsonizer
from evolution.evolution_configuration import *
from gui.dynamic_gui import NONE_LABEL, DynamicNode, refreshes_dynamics, BlockSignals, \
    feed_with_data
from gui.generated.options_configurator__gen import Ui_OptionsConfiguratorGen
from gui.generic_widget import GenericWidget
from gui.options_configurator_parts.classical_statistics_auto_updater import \
    ClassicalStatisticsAutoUpdater
from gui.options_configurator_parts.crowding_auto_updater import CrowdingAutoUpdater
from gui.options_configurator_parts.elitism_auto_updater import ElitismAutoUpdater
from gui.options_configurator_parts.evolution_auto_updater import EvolutionAutoUpdater
from gui.options_configurator_parts.induction_auto_updater import InductionAutoUpdater
from gui.options_configurator_parts.main_box_auto_updater import MainBoxAutoUpdater
from gui.options_configurator_parts.root_auto_updater import Statistics, RootAutoUpdater
from gui.options_configurator_parts.rules_auto_updater import RulesAutoUpdater
from induction.cyk_configuration import CoverageConfiguration, CoverageOperatorsConfiguration, \
    CykConfiguration, GrammarCorrection
from induction.cyk_configuration import CoverageOperatorConfiguration
from rule_adding import AddingRulesConfiguration, CrowdingConfiguration, \
    ElitismConfiguration


class AlgorithmVariant(object):
    @staticmethod
    def mk_pairs(*variants):
        return ((v.name, v) for v in variants)

    def __init__(self, name):
        self.name = name
        self._supported_statistics = []

    @abstractmethod
    def create_new_configuration(self):
        pass

    @property
    def supported_statistics(self):
        return self._supported_statistics


class SGcsAlgorithmVariant(AlgorithmVariant):
    def __init__(self):
        super().__init__('sGCS')
        self._supported_statistics += [
            Statistics.pasieka
        ]

    def create_new_configuration(self):
        return AlgorithmConfiguration.sgcs_variant()


class GcsAlgorithmVariant(AlgorithmVariant):
    def __init__(self):
        super().__init__('GCS')
        self._supported_statistics += [
            Statistics.classical
        ]

    def create_new_configuration(self):
        return AlgorithmConfiguration.default()


class OptionsConfigurator(GenericWidget):
    ALGORITHM_VARIANTS = {n: v for n, v in AlgorithmVariant.mk_pairs(
        SGcsAlgorithmVariant(),
        GcsAlgorithmVariant()
    )}
    DEFAULT_ALGORITHM_VARIANT_STR = 'sGCS'
    STATISTICS_CONFIGURATIONS = [NONE_LABEL] + [
        Statistics.classical,
        Statistics.pasieka
    ]

    def __init__(self, last_directory):
        super().__init__(Ui_OptionsConfiguratorGen)
        self.logger = logging.getLogger(__name__)
        self.last_directory = last_directory

        self.selector_bindings = None
        self.configuration = None

        self.dynamic_nodes += [
            DynamicNode(
                self.ui.classicalStatisticsGroup,
                visibility_condition=lambda main: main.selected_statistics == Statistics.classical,
                auto_updater=ClassicalStatisticsAutoUpdater(self)
            ),
            DynamicNode(
                self.ui.evolutionGroupBox,
                enabling_condition=lambda main: main.configuration.should_run_evolution
            ),
            DynamicNode(
                self.ui.eliteSizeSpinBox,
                enabling_condition=lambda main: main.configuration.rule.adding.elitism.is_used
            ),
            DynamicNode(
                auto_updater=RootAutoUpdater(self)
            ),
            DynamicNode(
                auto_updater=EvolutionAutoUpdater(self)
            ),
            DynamicNode(
                auto_updater=InductionAutoUpdater(self)
            ),
            DynamicNode(
                auto_updater=CrowdingAutoUpdater(self)
            ),
            DynamicNode(
                auto_updater=ElitismAutoUpdater(self)
            ),
            DynamicNode(
                auto_updater=RulesAutoUpdater(self)
            ),
            DynamicNode(
                auto_updater=MainBoxAutoUpdater(self)
            )
        ]

        self.bind_logic()

        with BlockSignals(*self.ui.__dict__.values()) as _:
            feed_with_data(self.ui.algorithmVariantComboBox, list(self.ALGORITHM_VARIANTS.keys()),
                           default_item=self.DEFAULT_ALGORITHM_VARIANT_STR)
            self.current_variant = self.ALGORITHM_VARIANTS[
                self.ui.algorithmVariantComboBox.currentText()]

            self.selected_statistics = None

            self.init_gui()

    def init_gui(self):
        self.logger.info('GUI initialization')
        # noinspection PyTypeChecker
        for b in self.selector_bindings:
            b.init_gui()

        self.init_gui_dn()

        # noinspection PyTypeChecker
        self.on_variant_changed(self.DEFAULT_ALGORITHM_VARIANT_STR)

    @refreshes_dynamics
    def reset_gui(self):
        self.logger.info('GUI reset')

        selectors = self.configuration.evolution.selectors
        # noinspection PyTypeChecker
        for b in self.selector_bindings:
            b.pull_new_state(selectors[b.index] if b.index < len(selectors) else None)

        self.update_dn_gui()

    def update_dynamic_nodes(self):
        self.logger.info('Dynamic nodes updated')
        super().update_dynamic_nodes()

    def bind_logic(self):
        self.logger.info('Binding logic')

        self.selector_bindings = [
            EvolutionSelectorBinding(i, c, s, self) for i, (c, s) in enumerate([
                (self.ui.selectorComboBox, self.ui.selectorSpinBox),
                (self.ui.selectorComboBox_2, self.ui.selectorSpinBox_2),
                (self.ui.selectorComboBox_3, self.ui.selectorSpinBox_3),
                (self.ui.selectorComboBox_4, self.ui.selectorSpinBox_4),
                (self.ui.selectorComboBox_5, self.ui.selectorSpinBox_5),
                (self.ui.selectorComboBox_6, self.ui.selectorSpinBox_6),
                (self.ui.selectorComboBox_7, self.ui.selectorSpinBox_7),
                (self.ui.selectorComboBox_8, self.ui.selectorSpinBox_8),
                (self.ui.selectorComboBox_9, self.ui.selectorSpinBox_9),
                (self.ui.selectorComboBox_10, self.ui.selectorSpinBox_10)
            ])
        ]

        for b in self.selector_bindings:
            b.bind_logic()
            
        self.bind_dn()

        self.ui.algorithmVariantComboBox.activated[str].connect(self.on_variant_changed)

    def bind_spinner(self, widget):
        widget.valueChanged.connect(self.on_gui_change)

    def bind_checkbox(self, widget):
        widget.stateChanged.connect(self.on_gui_change)

    def bind_combobox(self, widget):
        widget.currentIndexChanged.connect(self.on_gui_change)

    def on_gui_change(self):
        self.logger.debug('Updating model')
        self.update_model_dn()
        self.update_dynamic_nodes()

    def on_variant_changed(self, variant_str):
        self.logger.info('Variant changing from to %s', variant_str)
        self.current_variant = self.ALGORITHM_VARIANTS[variant_str]
        self.configuration = self.current_variant.create_new_configuration()
        self.configuration.evolution.selectors.append(
            EvolutionRouletteSelectorConfiguration.create())

        self.variant_changed__reset_gui()

    def variant_changed__reset_gui(self):
        self.selected_statistics = self.current_variant.supported_statistics[0]
        with BlockSignals(*self.ui.__dict__.values()) as _:
            index = self.ui.algorithmVariantComboBox.findText(self.current_variant.name)
            self.ui.algorithmVariantComboBox.setCurrentIndex(index)
            feed_with_data(self.ui.selectedStatisticsComboBox,
                           list(x for x in self.STATISTICS_CONFIGURATIONS
                                if x in self.current_variant.supported_statistics), clear=True,
                           default_item=self.selected_statistics)

            self.reset_gui()

    @refreshes_dynamics
    def update_selectors(self):
        self.configuration.evolution.selectors = list(filter(None, map(
            lambda x: x.internal_state,  self.selector_bindings)))
        self.logger.debug('Selectors: %s', str(self.configuration.evolution.selectors))


class EvolutionSelectorBinding(object):
    EVOLUTION_SELECTOR_MAP = {name: conf for name, conf in [
        ('no selector', None),
        ('random', EvolutionRandomSelectorConfiguration.create()),
        ('tournament', EvolutionTournamentSelectorConfiguration.create()),
        ('roulette', EvolutionRouletteSelectorConfiguration.create())
    ]}
    RIGHT_EVOLUTION_SELECTOR_MAP = {conf: name for name, conf in EVOLUTION_SELECTOR_MAP.items()}
    EVOLUTION_SELECTOR_NAMES = list(EVOLUTION_SELECTOR_MAP.keys())
    DEFAULT_SELECTOR = 'no selector'

    def __init__(self, index, type_widget, tournament_widget, options_configurator):
        self.logger = logging.getLogger(__name__)
        self.index = index
        self.type_widget = type_widget
        self.tournament_widget = tournament_widget
        self.options_configurator = options_configurator
        self.internal_state = None

    def bind_logic(self):
        self.type_widget.activated[str].connect(self.on_selector_changed)
        self.tournament_widget.valueChanged.connect(self.on_tournament_size_changed)
        self.options_configurator.dynamic_nodes.append(self.create_dynamic_tournament_node())

    def init_gui(self):
        self.logger.debug('init gui %s', str(self.index))
        feed_with_data(self.type_widget, self.EVOLUTION_SELECTOR_NAMES, self.DEFAULT_SELECTOR)
        self.tournament_widget.setMinimum(1)
        self.tournament_widget.setMaximum(20)

    def reset_gui(self):
        with BlockSignals(self.tournament_widget) as _:
            self.logger.debug('reset gui %s', str(self.index))
            text = self.RIGHT_EVOLUTION_SELECTOR_MAP[self.internal_state]
            index = self.type_widget.findText(text)
            self.type_widget.setCurrentIndex(index)
            if self.is_in_tournament_mode():
                self.tournament_widget.setValue(self.internal_state.tournament_size)
            else:
                self.tournament_widget.setValue(1)

    def pull_new_state(self, new_state):
        self.internal_state = new_state
        self.reset_gui()

    def on_selector_changed(self, selector_name):
        self.internal_state = self.EVOLUTION_SELECTOR_MAP[selector_name]
        self._customize_internal_state()
        self.options_configurator.update_selectors()

    def _customize_internal_state(self):
        if self.is_in_tournament_mode():
            self.internal_state.tournament_size = self.tournament_widget.value()

    def is_in_tournament_mode(self):
        return self.internal_state == self.EVOLUTION_SELECTOR_MAP['tournament']

    def create_dynamic_tournament_node(self):
        return DynamicNode(self.tournament_widget,
                           visibility_condition=lambda _: self.is_in_tournament_mode())

    def on_tournament_size_changed(self):
        self.on_selector_changed(self.RIGHT_EVOLUTION_SELECTOR_MAP[self.internal_state])
