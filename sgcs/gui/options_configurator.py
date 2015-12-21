import logging
from PyQt4 import QtCore
from abc import abstractmethod

from algorithm.gcs_runner import AlgorithmConfiguration
from evolution.evolution_configuration import *
from gui.generated.options_configurator__gen import Ui_OptionsConfiguratorGen
from gui.generic_widget import GenericWidget
from utils import MethodDecoratorWrapper

NONE_LABEL = '<None>'


class Statistics(object):
    pasieka = 'pasieka'
    classical = 'classical'


class VisibilityGroup(object):
    classical_statistics_conf = 0


class DynamicNode(object):
    @staticmethod
    def always(_):
        return True

    def __init__(self, visibility_condition, enabling_condition, *widgets):
        self.logger = logging.getLogger(__name__)
        self.widgets = widgets
        self.visibility_condition = visibility_condition
        self.enabling_condition = enabling_condition

    def update_visibility(self, options_configurator):
        for w in self.widgets:
            if self.visibility_condition(options_configurator):
                # self.logger.debug('Showing widget: %s', str(w))
                w.show()
            else:
                # self.logger.debug('Hiding widget: %s', str(w))
                w.hide()

    def update_availability(self, options_configurator):
        for w in self.widgets:
            if self.enabling_condition(options_configurator):
                w.setEnabled(True)
            else:
                w.setEnabled(False)


def refreshes_dynamics(func):
    class RefreshesDynamicsDecorator(object):
        NO_REFRESH = 'no_refresh'

        def __init__(self, f):
            self.func = f

        def __call__(self, *args, **kwargs):
            refresh_required = not kwargs.get(self.NO_REFRESH, None)
            options_configurator, *_ = args
            kwargs.pop(self.NO_REFRESH, None)

            self.func(*args, **kwargs)

            if refresh_required:
                options_configurator.update_dynamic_nodes()

        def __get__(self, instance, _):
            return MethodDecoratorWrapper(self, instance)

    return RefreshesDynamicsDecorator(func)


class AlgorithmVariant(object):
    @staticmethod
    def mk_pairs(*variants):
        return ((v.name, v) for v in variants)

    def __init__(self, name):
        self.name = name
        self._visible_nodes = []
        self._supported_statistics = [NONE_LABEL]

    @abstractmethod
    def create_new_configuration(self):
        pass

    @property
    def visible_nodes(self):
        return self._visible_nodes

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
        self._visible_nodes.append(VisibilityGroup.classical_statistics_conf)
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
    LETTER_SYMBOLS = [chr(i) for i in range(ord('A'), ord('Z') + 1)]
    LETTER_SYMBOLS_WITH_NONE = [NONE_LABEL] + LETTER_SYMBOLS
    DEFAULT_STARTING_SYMBOL = 'S'
    RULE_ADDING_HINTS = [NONE_LABEL] + [
        'expand population',
        'control population size (elitism DISABLED)',
        'control population size (elitism ENABLED)'
    ]
    STATISTICS_CONFIGURATIONS = [NONE_LABEL] + [
        Statistics.classical,
        Statistics.pasieka
    ]

    def is_group_supported(self, group):
        result = group in self.current_variant.visible_nodes
        self.logger.info('Group %s is %s', str(group), 'supported' if result else 'not supported')
        return result

    def __init__(self, last_directory):
        super().__init__(Ui_OptionsConfiguratorGen)
        self.logger = logging.getLogger(__name__)
        self.last_directory = last_directory

        self.selector_bindings = None
        self.configuration = None

        self.dynamic_nodes = [
            DynamicNode(
                lambda main: main.selected_statistics == Statistics.classical,
                DynamicNode.always,
                self.ui.classicalStatisticsGroup),
            DynamicNode(
                DynamicNode.always,
                lambda main: main.configuration.should_run_evolution,
                self.ui.evolutionGroupBox)
        ]

        self.bind_logic()

        feed_with_data(self.ui.algorithmVariantComboBox, list(self.ALGORITHM_VARIANTS.keys()))
        self.current_variant = self.ALGORITHM_VARIANTS[
            self.ui.algorithmVariantComboBox.currentText()]

        self.selected_statistics = None

        self.init_gui()

    def init_gui(self):
        self.logger.info('GUI initialization')
        # noinspection PyTypeChecker
        for b in self.selector_bindings:
            b.init_gui()
        # fields = list(EvolutionSelectorBinding.EVOLUTION_SELECTOR_MAP.keys())
        # for combo in self.selector_combo_boxes:
        #     feed_with_data(combo, fields, EvolutionSelectorBinding.DEFAULT_SELECTOR)

        feed_with_data(self.ui.startingSymbolComboBox, self.LETTER_SYMBOLS,
                       self.DEFAULT_STARTING_SYMBOL)
        feed_with_data(self.ui.universalSymbolComboBox, self.LETTER_SYMBOLS_WITH_NONE)
        feed_with_data(self.ui.ruleAddingHintComboBox, self.RULE_ADDING_HINTS)

        # noinspection PyTypeChecker

        self.on_variant_changed(self.DEFAULT_ALGORITHM_VARIANT_STR)

    @refreshes_dynamics
    def reset_gui(self):
        self.logger.info('GUI reset')

        selectors = self.configuration.evolution.selectors
        # noinspection PyTypeChecker
        for b in self.selector_bindings:
            b.pull_new_state(selectors[b.index] if b.index < len(selectors) else None)
        # for spinner in self.selector_spin_boxes:
        #     spinner.setValue(1)
        #     spinner.setMinimum(1)
        #     spinner.setMaximum(20)
        self.ui.shouldRunEvolutionCheckBox.setCheckState(
            QtCore.Qt.Checked if self.configuration.should_run_evolution else QtCore.Qt.Unchecked)

    def update_dynamic_nodes(self):
        self.logger.info('Dynamic nodes updated')
        for node in self.dynamic_nodes:
            node.update_visibility(self)
            node.update_availability(self)

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

        self.ui.algorithmVariantComboBox.activated[str].connect(self.on_variant_changed)
        self.ui.selectedStatisticsComboBox.activated[str].connect(
            self.on_selected_statistics_changed)
        self.ui.shouldRunEvolutionCheckBox.stateChanged.connect(self.on_run_evolution_state_changed)

    def on_variant_changed(self, variant_str):
        self.logger.info('Variant changing from to %s', variant_str)
        self.configuration = self.current_variant.create_new_configuration()
        self.configuration.evolution.selectors.append(EvolutionRouletteSelectorConfiguration.create())
        self.current_variant = self.ALGORITHM_VARIANTS[variant_str]
        feed_with_data(self.ui.selectedStatisticsComboBox,
                       list(x for x in self.STATISTICS_CONFIGURATIONS
                            if x in self.current_variant.supported_statistics), clear=True)

        self.selected_statistics = self.current_variant.supported_statistics[0]
        self.on_selected_statistics_changed(self.selected_statistics, no_refresh=True)
        self.reset_gui()

    @refreshes_dynamics
    def on_selected_statistics_changed(self, selected_statistics_str):
        self.logger.info('Selected statistics changed')
        self.selected_statistics = selected_statistics_str

    @refreshes_dynamics
    def on_run_evolution_state_changed(self, state):
        self.configuration.should_run_evolution = state == QtCore.Qt.Checked

    @refreshes_dynamics
    def update_selectors(self):
        self.configuration.evolution.selectors = list(filter(None, map(
            lambda x: x.internal_state,  self.selector_bindings)))
        self.logger.debug('Selectors: %s', str(self.configuration.evolution.selectors))


def feed_with_data(widget, data, default_item=None, clear=False):
    if clear:
        widget.clear()
    if default_item is None:
        items = data
    else:
        items = [default_item]
        items += filter(lambda x: x != default_item, data)
    widget.addItems(items)
    widget.setCurrentIndex(0)


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
        self.logger.debug('reset gui %s', str(self.index))
        text = self.RIGHT_EVOLUTION_SELECTOR_MAP[self.internal_state]
        index = self.type_widget.findText(text)
        self.type_widget.setCurrentIndex(index)
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
        return DynamicNode(lambda _: self.is_in_tournament_mode(), DynamicNode.always,
                           self.tournament_widget)

    def on_tournament_size_changed(self):
        self.on_selector_changed(self.RIGHT_EVOLUTION_SELECTOR_MAP[self.internal_state])
