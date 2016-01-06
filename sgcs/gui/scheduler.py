import logging
import os

from PyQt4 import QtGui, QtCore

from algorithm.task_model import TaskModel
from gui.dynamic_gui import DynamicNode, AutoUpdater
from gui.generated.scheduler__gen import Ui_scheduler
from gui.generic_widget import GenericWidget
from gui.input_data_lookup import InputDataLookup


class TaskView(object):
    REMOVE_TASK_CLICKED_SIGNAL = 'REMOVE_TASK_CLICKED_SIGNAL'
    MOVE_UP_TASK_CLICKED_SIGNAL = 'MOVE_UP_TASK_CLICKED_SIGNAL'
    MOVE_DOWN_TASK_CLICKED_SIGNAL = 'MOVE_DOWN_TASK_CLICKED_SIGNAL'

    LEARNING_SET_CONFIG_SELECTED_SIGNAL = 'LEARNING_SET_CONFIG_SELECTED_SIGNAL'
    TESTING_SET_CONFIG_SELECTED_SIGNAL = 'TESTING_SET_CONFIG_SELECTED_SIGNAL'
    PARAMS_SET_CONFIG_SELECTED_SIGNAL = 'PARAMS_SET_CONFIG_SELECTED_SIGNAL'

    NOT_SPECIFIED_LABEL = '<not selected>'
    EMPTY_STARTING_POPULATION_LABEL = '<empty starting population>'

    def __init__(self, index, scheduler):
        self.index = index
        self.scheduler = scheduler
        self.groupbox = QtGui.QGroupBox()
        self.groupbox.setTitle('Task')
        self.groupbox_layout = QtGui.QVBoxLayout()
        self.groupbox.setLayout(self.groupbox_layout)

        self.learning_set_line = self.create_learning_set()
        self.testing_set_line = self.create_testing_set()
        self.config_set_line = self.create_config()
        self.population_line = self.create_population()

        self.remove_button, self.move_up_button, self.move_down_button = \
            self.create_control_section()

        self.dynamic_nodes = [
            DynamicNode(
                self.groupbox,
                visibility_condition=self._visibility_condition,
                auto_updater=AutoUpdater(
                    bind_func=self.nothing,
                    init_gui_func=self.nothing,
                    update_model_func=self.nothing,
                    update_gui_func=self.update_task_view
                )
            ),
            DynamicNode(
                self.move_up_button,
                enabling_condition=lambda _: self.index > 0
            ),
            DynamicNode(
                self.move_down_button,
                enabling_condition=lambda sch: self.index < len(sch.tasks) - 1
            )
        ]

    @staticmethod
    def nothing():
        pass

    def update_task_view(self):
        if self.index < len(self.scheduler.tasks):
            self.update_learning_set_config_path()
            self.update_testing_set_config_path()
            self.update_params_config_path()
            self.update_population_config_path()

    def update_learning_set_config_path(self):
        path_provided = self.scheduler.tasks[self.index].learning_configuration is not None
        text = self.scheduler.tasks[self.index].learning_configuration if path_provided \
            else self.NOT_SPECIFIED_LABEL

        self.learning_set_line.setText(text)

    def update_testing_set_config_path(self):
        path_provided = self.scheduler.tasks[self.index].testing_configuration is not None
        text = self.scheduler.tasks[self.index].testing_configuration if path_provided \
            else self.NOT_SPECIFIED_LABEL

        self.testing_set_line.setText(text)

    def update_params_config_path(self):
        path_provided = self.scheduler.tasks[self.index].params_configuration is not None
        text = self.scheduler.tasks[self.index].params_configuration if path_provided \
            else self.NOT_SPECIFIED_LABEL

        self.config_set_line.setText(text)

    def update_population_config_path(self):
        path_provided = self.scheduler.tasks[self.index].population_configuration is not None
        text = self.scheduler.tasks[self.index].population_configuration if path_provided \
            else self.EMPTY_STARTING_POPULATION_LABEL

        self.population_line.setText(text)

    def _visibility_condition(self, scheduler):
        return self.index < len(scheduler.tasks)

    def on_remove_clicked(self):
        self.groupbox.emit(QtCore.SIGNAL(self.REMOVE_TASK_CLICKED_SIGNAL), self)

    def on_move_up_clicked(self):
        self.groupbox.emit(QtCore.SIGNAL(self.MOVE_UP_TASK_CLICKED_SIGNAL), self)

    def on_move_down_clicked(self):
        self.groupbox.emit(QtCore.SIGNAL(self.MOVE_DOWN_TASK_CLICKED_SIGNAL), self)

    def create_learning_set(self):
        learning_set_line, learning_set_select_button, _ = \
            self.create_task_item(self.groupbox_layout, 'Learning set')

        # noinspection PyUnresolvedReferences
        learning_set_select_button.clicked.connect(self.on_select_learning_set_clicked)

        return learning_set_line

    def on_select_learning_set_clicked(self):
        selected_filename = QtGui.QFileDialog.getOpenFileName(
            self.scheduler.widget, 'Open learning config...', self.scheduler.last_directory,
            InputDataLookup.DATA_CONFIG_EXT)

        if selected_filename:
            self.groupbox.emit(
                QtCore.SIGNAL(self.LEARNING_SET_CONFIG_SELECTED_SIGNAL), self, selected_filename)
            self.scheduler.last_directory = os.path.dirname(selected_filename)

    def create_testing_set(self):
        testing_set_line, testing_set_select_button, _ = \
            self.create_task_item(self.groupbox_layout, 'Testing set')

        # noinspection PyUnresolvedReferences
        testing_set_select_button.clicked.connect(self.on_select_testing_set_clicked)

        return testing_set_line

    def on_select_testing_set_clicked(self):
        selected_filename = QtGui.QFileDialog.getOpenFileName(
            self.scheduler.widget, 'Open testing config...', self.scheduler.last_directory,
            InputDataLookup.DATA_CONFIG_EXT)

        if selected_filename:
            self.groupbox.emit(
                QtCore.SIGNAL(self.TESTING_SET_CONFIG_SELECTED_SIGNAL), self, selected_filename)
            self.scheduler.last_directory = os.path.dirname(selected_filename)

    def create_config(self):
        config_set_line, config_set_select_button, _ = \
            self.create_task_item(self.groupbox_layout, 'Configuration file')

        # noinspection PyUnresolvedReferences
        config_set_select_button.clicked.connect(self.on_select_config_set_clicked)

        return config_set_line

    def on_select_config_set_clicked(self):
        selected_filename = QtGui.QFileDialog.getOpenFileName(
            self.scheduler.widget, 'Open params config...', self.scheduler.last_directory,
            "*.parconf")

        if selected_filename:
            self.groupbox.emit(
                QtCore.SIGNAL(self.PARAMS_SET_CONFIG_SELECTED_SIGNAL), self, selected_filename)
            self.scheduler.last_directory = os.path.dirname(selected_filename)

    def create_population(self):
        population_line, population_select_button, population_default_button = \
            self.create_task_item(self.groupbox_layout, 'Starting population')
        population_default_button.setVisible(True)
        return population_line

    def create_control_section(self):
        groupbox, groupbox_layout = self._create_groupbox_with_horizontal_layout('')
        remove_button = self._add_button_with_title('Remove', groupbox_layout)
        # noinspection PyUnresolvedReferences
        remove_button.clicked.connect(self.on_remove_clicked)

        move_up_button = self._add_button_with_title('Move up', groupbox_layout)
        # noinspection PyUnresolvedReferences
        move_up_button.clicked.connect(self.on_move_up_clicked)

        move_down_button = self._add_button_with_title('Move down', groupbox_layout)
        # noinspection PyUnresolvedReferences
        move_down_button.clicked.connect(self.on_move_down_clicked)

        self.groupbox_layout.addWidget(groupbox)

        return remove_button, move_up_button, move_down_button

    def create_task_item(self, layout, title):
        groupbox, line, select_button, default_button = self._create_task_group_box(title)
        layout.addWidget(groupbox)

        return line, select_button, default_button

    def _create_task_group_box(self, title):
        groupbox, groupbox_layout = self._create_groupbox_with_horizontal_layout(title)

        text_box = QtGui.QLineEdit()
        text_box.setEnabled(False)
        groupbox_layout.addWidget(text_box)

        select_button = self._add_button_with_title('Select', groupbox_layout)

        default_button = self._add_button_with_title('Default', groupbox_layout)
        default_button.setVisible(False)

        return groupbox, text_box, select_button, default_button

    @staticmethod
    def _create_groupbox_with_horizontal_layout(title):
        groupbox = QtGui.QGroupBox()
        groupbox.setTitle(title)
        groupbox_layout = QtGui.QHBoxLayout()
        groupbox.setLayout(groupbox_layout)

        return groupbox, groupbox_layout

    @staticmethod
    def _add_button_with_title(title, layout):
        button = QtGui.QPushButton()
        button.setText(title)
        layout.addWidget(button)

        return button


class Scheduler(GenericWidget):
    MAX_NUMBER_OF_TASKS = 50

    def __init__(self):
        super().__init__(Ui_scheduler)
        self.logger = logging.getLogger(__name__)
        self.ui.addTaskButton.clicked.connect(self.on_add_task_clicked)
        self.ui.clearTasksButton.clicked.connect(self.on_clear_tasks_clicked)

        self.last_directory = ''

        self.tasks = []

        self.widget.connect(self.ui.queueVerticalLayout,
                            QtCore.SIGNAL(TaskView.REMOVE_TASK_CLICKED_SIGNAL), self.on_remove_task)

        self._create_tasks_views()

        self.dynamic_nodes += [
            DynamicNode(
                self.ui.addTaskButton,
                enabling_condition=lambda sch: len(sch.tasks) < self.MAX_NUMBER_OF_TASKS
            ),
            DynamicNode(
                self.ui.clearTasksButton,
                enabling_condition=lambda sch: len(sch.tasks) > 0
            ),
            DynamicNode(
                self.ui.runTasksButton,
                enabling_condition=lambda sch: sch.tasks and
                all(self._is_valid_task(x) for x in sch.tasks)
            )
        ]

        self.update_dynamic_nodes()

    def _create_tasks_views(self):
        for i in range(self.MAX_NUMBER_OF_TASKS):
            task = TaskView(i, self)
            self.dynamic_nodes += task.dynamic_nodes
            self.ui.queueVerticalLayout.addWidget(task.groupbox)

            self.widget.connect(
                task.groupbox,
                QtCore.SIGNAL(TaskView.REMOVE_TASK_CLICKED_SIGNAL),
                self.on_remove_task
            )

            self.widget.connect(
                task.groupbox,
                QtCore.SIGNAL(TaskView.MOVE_UP_TASK_CLICKED_SIGNAL),
                self.on_move_up_task
            )

            self.widget.connect(
                task.groupbox,
                QtCore.SIGNAL(TaskView.MOVE_DOWN_TASK_CLICKED_SIGNAL),
                self.on_move_down_task
            )

            self.widget.connect(
                task.groupbox,
                QtCore.SIGNAL(TaskView.LEARNING_SET_CONFIG_SELECTED_SIGNAL),
                self.on_learning_set_selected
            )

            self.widget.connect(
                task.groupbox,
                QtCore.SIGNAL(TaskView.TESTING_SET_CONFIG_SELECTED_SIGNAL),
                self.on_testing_set_selected
            )

            self.widget.connect(
                task.groupbox,
                QtCore.SIGNAL(TaskView.PARAMS_SET_CONFIG_SELECTED_SIGNAL),
                self.on_params_set_selected
            )

    def on_remove_task(self, task):
        self.logger.debug('Removing task')
        del self.tasks[task.index]
        self.dynamic_gui_update()

    def on_move_up_task(self, task):
        self.logger.debug('Moving task up')
        current_index = task.index
        if current_index > 0:
            new_index = current_index - 1
            self.tasks[new_index], self.tasks[current_index] = \
                self.tasks[current_index], self.tasks[new_index]
            self.dynamic_gui_update()

    def on_move_down_task(self, task):
        self.logger.debug('Moving task down')
        current_index = task.index
        if current_index < len(self.tasks):
            new_index = current_index + 1
            self.tasks[new_index], self.tasks[current_index] = \
                self.tasks[current_index], self.tasks[new_index]
            self.dynamic_gui_update()

    def on_learning_set_selected(self, task, selected_filename):
        self.logger.debug('Updating learning set path')
        self.tasks[task.index].learning_configuration = selected_filename
        self.dynamic_gui_update()

    def on_testing_set_selected(self, task, selected_filename):
        self.logger.debug('Updating testing set path')
        self.tasks[task.index].testing_configuration = selected_filename
        self.dynamic_gui_update()

    def on_params_set_selected(self, task, selected_filename):
        self.logger.debug('Updating params config set path')
        self.tasks[task.index].params_configuration = selected_filename
        self.dynamic_gui_update()

    def on_add_task_clicked(self):
        self.logger.debug('Add task clicked!')
        if len(self.tasks) <= self.MAX_NUMBER_OF_TASKS:
            task = TaskModel()
            self.tasks.append(task)
            self.dynamic_gui_update()

    def on_clear_tasks_clicked(self):
        self.logger.debug('Clear tasks clicked!')
        self.tasks.clear()
        self.dynamic_gui_update()

    @staticmethod
    def _is_valid_task(task):
        return all(x is not None for x in [
            task.learning_configuration,
            task.testing_configuration,
            task.params_configuration
        ])
