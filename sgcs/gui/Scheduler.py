import logging
from PyQt4 import QtGui, QtCore

from algorithm.task_model import TaskModel
from gui.dynamic_gui import DynamicNode
from gui.generated.scheduler__gen import Ui_scheduler
from gui.generic_widget import GenericWidget


class TaskView(object):
    REMOVE_TASK_CLICKED_SIGNAL = 'REMOVE_TASK_CLICKED_SIGNAL'

    def __init__(self, index, model):
        self.index = index
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

        self.dynamic_node = DynamicNode(
            self.groupbox,
            visibility_condition=self._visibility_condition)

    def _visibility_condition(self, scheduler):
        return self.index < len(scheduler.tasks)

    def on_remove_clicked(self):
        self.groupbox.emit(QtCore.SIGNAL(self.REMOVE_TASK_CLICKED_SIGNAL), self)

    def create_learning_set(self):
        learning_set_line, learning_set_select_button, _ = \
            self.create_task_item(self.groupbox_layout, 'Learning set')
        return learning_set_line

    def create_testing_set(self):
        testing_set_line, testing_set_select_button, _ = \
            self.create_task_item(self.groupbox_layout, 'Testing set')
        return testing_set_line

    def create_config(self):
        config_set_line, config_set_select_button, _ = \
            self.create_task_item(self.groupbox_layout, 'Configuration file')
        return config_set_line

    def create_population(self):
        population_line, population_select_button, population_default_button = \
            self.create_task_item(self.groupbox_layout, 'Starting population')
        population_default_button.setVisible(True)
        return population_line

    def create_control_section(self):
        groupbox, groupbox_layout = self._create_groupbox_with_horizontal_layout('')
        remove_button = self._add_button_with_title('Remove', groupbox_layout)
        remove_button.clicked.connect(self.on_remove_clicked)

        move_up_button = self._add_button_with_title('Move up', groupbox_layout)
        move_down_button = self._add_button_with_title('Move down', groupbox_layout)

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

        self.tasks = []

        self.widget.connect(self.ui.queueVerticalLayout,
                            QtCore.SIGNAL(TaskView.REMOVE_TASK_CLICKED_SIGNAL), self.on_remove_task)

        self._create_tasks_views()

        self.update_dynamic_nodes()

    def _create_tasks_views(self):
        for i in range(self.MAX_NUMBER_OF_TASKS):
            task = TaskView(i, self)
            self.dynamic_nodes.append(task.dynamic_node)
            self.ui.queueVerticalLayout.addWidget(task.groupbox)
            self.widget.connect(task.groupbox,
                            QtCore.SIGNAL(TaskView.REMOVE_TASK_CLICKED_SIGNAL), self.on_remove_task)

    def _add_task(self, task):
        pass
        # self.tasks.append(task)
        # self.dynamic_nodes.append(task.dynamic_node)
        # self.ui.queueVerticalLayout.addWidget(task.groupbox)

    def on_remove_task(self, task):
        self.logger.debug('Removing task')
        del self.tasks[task.index]
        self.dynamic_gui_update()

    def on_add_task_clicked(self):
        self.logger.debug('Add task clicked!')
        if len(self.tasks) <= self.MAX_NUMBER_OF_TASKS:
            task = TaskModel()
            self.tasks.append(task)
            self.dynamic_gui_update()
