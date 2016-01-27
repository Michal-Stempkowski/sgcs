import logging
import os
from random import Random

from PyQt4 import QtGui, QtCore

from core.rule import Rule
from core.rule_population import RulePopulation
from core.symbol import Symbol
from executors.population_executor import PopulationExecutor, TerminalRuleModel, \
    NonTerminalRuleModel
from executors.simulation_executor import SimulationExecutor
from gui.async_progress_dialog import AsyncProgressDialog
from gui.dynamic_gui import DynamicNode, AutoUpdater
from gui.generated.population_editor__gen import Ui_populationEditor
from gui.generic_widget import GenericWidget
from utils import Randomizer


class RuleViewAutoUpdater(AutoUpdater):
    def __init__(self, rule_view):
        super().__init__(
            lambda: self._bind(rule_view),
            lambda: self._update_model(rule_view),
            lambda: self._update_gui(rule_view),
            lambda: self._init_gui(rule_view)
        )

    def _init_gui(self, rule_view):
        pass

    @staticmethod
    def _bind(rule_view):
        pass

    @staticmethod
    def _update_model(rule_view):
        pass

    @staticmethod
    def _update_gui(rule_view):
        if rule_view.exists():
            data = rule_view.population_editor.rules[rule_view.index]
            rule_view.groupbox.setTitle('{0}Rule'.format('Terminal ' if data.is_terminal else ''))
            rule_view.parent_line.setText(data.parent)
            rule_view.left_child_line.setText(data.left_child)
            rule_view.right_child_line.setText(data.right_child)


class RuleView(object):
    REMOVE_RULE_CLICKED_SIGNAL = 'REMOVE_RULE_CLICKED_SIGNAL'

    SEPARATOR_STRING = '=>'

    def __init__(self, index, population_editor):
        self.index = index
        self.population_editor = population_editor
        self.groupbox = QtGui.QGroupBox()
        self.groupbox.setTitle('_Rule_')
        self._groupbox_layout = QtGui.QHBoxLayout()
        self.groupbox.setLayout(self._groupbox_layout)
        self.parent_line, self.left_child_line, self.right_child_line = self._create_interior()

        self.dynamic_nodes = [
            DynamicNode(
                self.groupbox,
                visibility_condition=lambda _: self.exists(),
                auto_updater=RuleViewAutoUpdater(self)
            ),
            DynamicNode(
                self.right_child_line,
                visibility_condition=lambda _: not self._is_terminal(),
                auto_updater=RuleViewAutoUpdater(self)
            )
        ]

        self._bind()

    # noinspection PyUnresolvedReferences
    def _bind(self):
        self.parent_line.editingFinished.connect(self._on_editing_finished)
        self.left_child_line.editingFinished.connect(self._on_editing_finished)
        self.right_child_line.editingFinished.connect(self._on_editing_finished)

    def _create_interior(self):
        parent_line = QtGui.QLineEdit()

        separator = QtGui.QLabel()
        separator.setText(self.SEPARATOR_STRING)

        left_child_line = QtGui.QLineEdit()
        right_child_line = QtGui.QLineEdit()

        remove_button = QtGui.QPushButton()
        remove_button.setText('Remove')
        # noinspection PyUnresolvedReferences
        remove_button.clicked.connect(
            self._on_remove_clicked
        )

        self._groupbox_layout.addWidget(parent_line)
        self._groupbox_layout.addWidget(separator)
        self._groupbox_layout.addWidget(left_child_line)
        self._groupbox_layout.addWidget(right_child_line)
        self._groupbox_layout.addWidget(remove_button)

        return parent_line, left_child_line, right_child_line

    def exists(self):
        return self.index < len(self.population_editor.rules)

    def _is_terminal(self):
        return self.exists() and self.population_editor.rules[self.index].is_terminal

    def _on_editing_finished(self):
        parent = self.parent_line.text()
        left_child = self.left_child_line.text()
        right_child = self.right_child_line.text()

        if self.exists():
            data = self.population_editor.rules[self.index]
            data.parent = parent
            data.left_child = left_child

            if not data.is_terminal:
                self.population_editor.rules[self.index].right_child = right_child

    def _on_remove_clicked(self):
        self.groupbox.emit(QtCore.SIGNAL(self.REMOVE_RULE_CLICKED_SIGNAL), self.index)


class LoadPopulationWorker(QtCore.QThread):
    TRANSLATOR_READY_SIGNAL = 'TRANSLATOR_READY_SIGNAL'
    POPULATION_LOADED_SIGNAL = 'POPULATION_LOADED_SIGNAL'
    STARTING_SYMBOL = Symbol(1)

    def __init__(self, population_editor):
        super().__init__(population_editor.widget)
        self.population_editor = population_editor
        self.translator = None
        self.population_executor = PopulationExecutor()
        self.simulation_executor = SimulationExecutor()
        self.operation = None
        self.randomizer = Randomizer(Random())

    def run(self):
        self.emit(QtCore.SIGNAL(AsyncProgressDialog.CHANGE_STEP_EVENT), 'Operation in progress...')
        self.emit(QtCore.SIGNAL(AsyncProgressDialog.SET_PROGRESS_EVENT), -1)
        if self.operation is not None:
            # noinspection PyCallingNonCallable
            self.operation()
        self.emit(QtCore.SIGNAL(AsyncProgressDialog.RESET_EVENT))

    def load_learning_set_operation(self):
        self.translator = self.population_executor.get_learned_translator(
            self.population_editor.population_path)
        self.emit(QtCore.SIGNAL(self.TRANSLATOR_READY_SIGNAL))

    def load_population_operation(self):
        name = os.path.basename(self.population_editor.population_path).split('.')[0]
        dir_path = os.path.dirname(self.population_editor.population_path)
        rule_population = self.simulation_executor.load_population(
            dir_path, name, starting_symbol=self.STARTING_SYMBOL)

        self.population_editor.rules.clear()

        for rule in rule_population.get_terminal_rules():
            translated = rule.human_friendly_representation(rule_population.symbol_shift(),
                                                            rule_population.starting_symbol,
                                                            rule_population.universal_symbol)
            rule_model = TerminalRuleModel()
            rule_model.parent = translated[0]
            rule_model.left_child = self.translator.symbol_to_word(rule.left_child)
            self.population_editor.rules.append(rule_model)

        for rule in rule_population.get_all_non_terminal_rules():
            translated = rule.human_friendly_representation(rule_population.symbol_shift(),
                                                            rule_population.starting_symbol,
                                                            rule_population.universal_symbol)
            rule_model = NonTerminalRuleModel()
            rule_model.parent, rule_model.left_child, rule_model.right_child = translated
            self.population_editor.rules.append(rule_model)

        self.emit(QtCore.SIGNAL(self.POPULATION_LOADED_SIGNAL))

    def save_population_operation(self):
        population = RulePopulation(self.STARTING_SYMBOL)
        for rule_model in self.population_editor.rules:
            if rule_model.is_terminal:
                parent, terminal_word = Rule.from_human_friendly_representation(
                    population.symbol_shift(),
                    population.starting_symbol,
                    population.universal_symbol,
                    rule_model.parent,
                    rule_model.left_child,
                    rule_model.right_child
                )
                terminal_symbol = self.translator.word_to_symbol(terminal_word)

                population.add_rule(Rule(parent, terminal_symbol), self.randomizer)
            else:
                parent, left, right = Rule.from_human_friendly_representation(
                    population.symbol_shift(),
                    population.starting_symbol,
                    population.universal_symbol,
                    rule_model.parent,
                    rule_model.left_child,
                    rule_model.right_child
                )

                population.add_rule(Rule(parent, left, right), self.randomizer)

        name = os.path.basename(self.population_editor.population_path).split('.')[0]
        path = os.path.dirname(self.population_editor.population_path)
        self.simulation_executor.save_population_data(population, path, name)


class PopulationAutoUpdater(AutoUpdater):
    NO_LEARNING_SET_SELECTED = '<no learning set selected>'

    def __init__(self, population_editor):
        super().__init__(
            lambda: self._bind(population_editor),
            lambda: self._update_model(population_editor),
            lambda: self._update_gui(population_editor),
            lambda: self._init_gui(population_editor)
        )

    def _init_gui(self, population_editor):
        self.update_gui(population_editor)

    @staticmethod
    def _bind(population_editor):
        pass

    @staticmethod
    def _update_model(population_editor):
        population_editor.population_path = population_editor.learning_set_line.text()

    def _update_gui(self, population_editor):
        text = population_editor.population_path if population_editor.population_path is not None \
            else self.NO_LEARNING_SET_SELECTED
        population_editor.learning_set_line.setText(text)


class PopulationEditor(GenericWidget):
    MAX_NUMBER_OF_RULES = 100

    def __init__(self):
        super().__init__(Ui_populationEditor)
        self.logger = logging.getLogger(__name__)
        self.last_directory = '.'
        self.population_path = None

        self.rules = []

        self.learning_set_line = self.ui.learningSetLineEdit
        self._load_learning_set_button = self.ui.loadLearningSetPushButton
        self._reset_button = self.ui.controlButtonBox.button(QtGui.QDialogButtonBox.Reset)
        self._save_button = self.ui.controlButtonBox.button(QtGui.QDialogButtonBox.Save)
        self._open_button = self.ui.controlButtonBox.button(QtGui.QDialogButtonBox.Open)
        self._add_terminal_button = self.ui.addTerminalPushButton
        self._add_nonterminal_button = self.ui.addNonTerminalPushButton

        self.worker = LoadPopulationWorker(self)
        self.async_progress_dialog = AsyncProgressDialog(self, self.worker)
        self.async_progress_dialog.make_lean()

        self.dynamic_nodes += [
            DynamicNode(
                self._save_button, self._open_button,
                enabling_condition=PopulationEditor._is_learning_set_selected
            ),
            DynamicNode(
                self.learning_set_line,
                auto_updater=PopulationAutoUpdater(self)
            )
        ]

        self._create_rule_views()
        self._bind()
        self.dynamic_gui_update()

    def _bind(self):
        self._load_learning_set_button.clicked.connect(
            self._on_load_learning_set_clicked
        )
        self.widget.connect(
            self.worker,
            QtCore.SIGNAL(LoadPopulationWorker.TRANSLATOR_READY_SIGNAL),
            self._on_gui_invalidated
        )
        self.widget.connect(
            self.worker,
            QtCore.SIGNAL(LoadPopulationWorker.POPULATION_LOADED_SIGNAL),
            self._on_gui_invalidated
        )
        self._open_button.clicked.connect(
            self._on_open_population_clicked
        )
        self._save_button.clicked.connect(
            self._on_save_population_clicked
        )
        self._add_terminal_button.clicked.connect(
            self._add_new_terminal_rule
        )
        self._add_nonterminal_button.clicked.connect(
            self._add_new_nonterminal_rule
        )

    def _add_new_terminal_rule(self):
        self.rules.append(TerminalRuleModel())
        self._on_gui_invalidated()

    def _add_new_nonterminal_rule(self):
        self.rules.append(NonTerminalRuleModel())
        self._on_gui_invalidated()

    def _is_learning_set_selected(self):
        return self.worker.translator is not None

    def _create_rule_views(self):
        for i in range(self.MAX_NUMBER_OF_RULES):
            rule_view = RuleView(i, self)
            self.dynamic_nodes += rule_view.dynamic_nodes
            self.ui.rules_layout.addWidget(rule_view.groupbox)

            self.widget.connect(
                rule_view.groupbox,
                QtCore.SIGNAL(RuleView.REMOVE_RULE_CLICKED_SIGNAL),
                self._on_remove_rule
            )

    def _on_remove_rule(self, index):
        del self.rules[index]
        self.dynamic_gui_update()

    def _on_load_learning_set_clicked(self):
        learning_set_path = QtGui.QFileDialog.getOpenFileName(
            self.widget, 'Select learning set...', self.last_directory)
        if learning_set_path:
            self.last_directory = os.path.dirname(learning_set_path)
            self.async_progress_dialog.show()
            self.population_path = learning_set_path
            self.worker.operation = self.worker.load_learning_set_operation
            self.worker.start()

    def _on_open_population_clicked(self):
        population_path = QtGui.QFileDialog.getOpenFileName(
            self.widget, 'Open population...', self.last_directory,
            '*' + SimulationExecutor.POPULATION_EXT)
        if population_path:
            self.last_directory = os.path.dirname(population_path)
            self.async_progress_dialog.show()
            self.population_path = population_path
            self.worker.operation = self.worker.load_population_operation
            self.worker.start()

    def _on_save_population_clicked(self):
        population_path = QtGui.QFileDialog.getSaveFileName(
            self.widget, 'Save population...', self.last_directory,
            '*' + SimulationExecutor.POPULATION_EXT)
        if population_path:
            self.last_directory = os.path.dirname(population_path)
            self.async_progress_dialog.show()
            self.population_path = population_path
            self.worker.operation = self.worker.save_population_operation
            self.worker.start()

    def _on_gui_invalidated(self):
        self.dynamic_gui_update()
