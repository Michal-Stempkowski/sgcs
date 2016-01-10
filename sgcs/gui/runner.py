import asyncio
import logging

import multiprocessing

import functools
from PyQt4 import QtCore, QtGui

from executors.simulation_executor import SimulationExecutor
from gui.dynamic_gui import DynamicNode, AutoUpdater, DynamicRoot
from gui.generated.runner__gen import Ui_runner
from gui.generic_widget import GenericWidget


class TaskProgressModel(object):
    def __init__(self):
        self.start_time = None
        self.progress = None
        self.max_steps = None
        self.is_done = False
        self.end_time = None


class RunProgressAutoUpdater(AutoUpdater):
    def __init__(self, run_progress_view):
        super().__init__(
            lambda: self._bind(run_progress_view),
            lambda: self._update_model(run_progress_view),
            lambda: self._update_gui(run_progress_view),
            lambda: self._init_gui(run_progress_view)
        )

    def _init_gui(self, run_progress_view):
        self._update_gui(run_progress_view)

    def _bind(self, run_progress_view):
        pass

    def _update_gui(self, run_progress_view):
        progress_data = run_progress_view.runner.run_progress_data
        if run_progress_view.index < len(progress_data):
            data = progress_data[run_progress_view.index]

            run_progress_view.start_time_line.setText(
                data.start_time if data.start_time is not None else RunnerGuiModel.FIELD_UNDEFINED)

            progress = data.progress if data.progress is not None else 0
            max_steps = data.max_steps if data.max_steps is not None else 0

            run_progress_view.progress_bar.setValue(progress)
            run_progress_view.progress_bar.setMaximum(max_steps)

            run_progress_view.end_time_line.setText(
                data.end_time if data.end_time is not None else RunnerGuiModel.FIELD_UNDEFINED)

            run_progress_view.steps_line.setText('{0}/{1}'.format(progress, max_steps))

    def _update_model(self, run_progress_view):
        pass


class RunProgressView(DynamicRoot):
    START_TIME_LABEL = 'Start time:'
    CURRENT_STEP_LABEL = 'Current step:'
    END_TIME_LABEL = 'End time:'
    TOTAL_STEPS_LABEL = 'Total steps:'

    def __init__(self, index, runner):
        super().__init__()
        self.index = index
        self.runner = runner
        self.groupbox = QtGui.QGroupBox()
        self.groupbox.setTitle('Run {0}'.format(index))
        self.groupbox_layout = QtGui.QFormLayout()
        self.groupbox.setLayout(self.groupbox_layout)

        self.start_time_label, self.start_time_line = \
            self._create_text_row(self.START_TIME_LABEL)

        self.progress_label, self.progress_bar = \
            self._create_progress_row(self.CURRENT_STEP_LABEL)

        self.end_time_label, self.end_time_line = \
            self._create_text_row(self.END_TIME_LABEL)

        self.step_label, self.steps_line = \
            self._create_text_row(self.TOTAL_STEPS_LABEL)

        self.dynamic_nodes += [
            DynamicNode(
                self.groupbox,
                visibility_condition=lambda rpv: rpv.index < len(rpv.runner.run_progress_data),
                auto_updater=RunProgressAutoUpdater(self)
            ),
            DynamicNode(
                self.progress_label,
                self.progress_bar,
                visibility_condition=self._visible_during_run
            ),
            DynamicNode(
                self.end_time_label,
                self.end_time_line,
                self.step_label,
                self.steps_line,
                visibility_condition=self._invisible_during_run
            )
        ]

    @staticmethod
    def _visible_during_run(rpv):
        progress_data = rpv.runner.run_progress_data
        if rpv.index < len(progress_data):
            return not progress_data[rpv.index].is_done
        else:
            return False

    @staticmethod
    def _invisible_during_run(rpv):
        progress_data = rpv.runner.run_progress_data
        if rpv.index < len(progress_data):
            return progress_data[rpv.index].is_done
        else:
            return False

    def _create_row(self, text, elem):
        label = QtGui.QLabel()
        label.setText(text)

        self.groupbox_layout.addRow(label, elem)
        return label, elem

    def _create_text_row(self, text):
        text_line = QtGui.QLineEdit()
        text_line.setReadOnly(True)
        return self._create_row(text, text_line)

    def _create_progress_row(self, text):
        progress_bar = QtGui.QProgressBar()
        return self._create_row(text, progress_bar)


class SimulationPhases(object):
    INIT = 'Initializing runner...'
    SETUP = 'Performing environment setup...'
    LEARNING = 'Performing learning runs...'
    TESTING = 'Performing testing run...'
    COLLECTING = 'Collecting run artifacts...'
    DONE = 'All tasks finished!'
    ERROR = 'An error has occurred!'


class RunnerSimulationDataAutoUpdater(AutoUpdater):
    def __init__(self, runner):
        super().__init__(
            lambda: self._bind(runner),
            lambda: self._update_model(runner),
            lambda: self._update_gui(runner),
            lambda: self._init_gui(runner)
        )

    def _init_gui(self, runner):
        for run_view in runner.run_progress_views:
            runner.ui.runProgressVerticalLayout.addWidget(run_view.groupbox)
        self._update_gui(runner)

    def _bind(self, runner):
        runner.simulation_worker.start()

    def _update_gui(self, runner):
        data = runner.simulation_worker.current_data
        if data.tasks_progress != RunnerGuiModel.FIELD_UNDEFINED:
            runner.ui.allTasksProgressBar.setValue(data.tasks_progress)
            runner.ui.allTasksProgressBar.setMaximum(len(runner.scheduler.tasks))

        runner.ui.currentDataFileLineEdit.setText(data.current_input)
        runner.ui.currentConfigFileLineEdit.setText(data.current_config)
        runner.ui.currentAlgorithmPhaseLlineEdit.setText(data.current_phase)

    def _update_model(self, runner):
        pass


class RunnerGuiModel(object):
    FIELD_UNDEFINED = '#'

    def __init__(self):
        self.tasks_progress = self.FIELD_UNDEFINED
        self.current_input = self.FIELD_UNDEFINED
        self.current_config = self.FIELD_UNDEFINED
        self.current_phase = SimulationPhases.INIT
        self.runs = []


class SimulationWorker(QtCore.QThread):
    def __init__(self, runner):
        super().__init__(runner.widget)
        self.runner = runner
        self.is_running = False
        self.simulation_executor = SimulationExecutor()
        self.current_data = RunnerGuiModel()

    def run(self):
        for i, task in enumerate(self.runner.scheduler.tasks):
            self._setup_task(i, task)
        while self.is_running:
            pass

    def _setup_task(self, task_no, task):
        new_data = RunnerGuiModel()
        new_data.tasks_progress = task_no
        new_data.current_input = task.data_configuration
        new_data.current_config = task.params_configuration
        new_data.current_phase = SimulationPhases.SETUP
        self.current_data = new_data

        run_func, configuration = self.simulation_executor.prepare_simulation(
            new_data.current_input, new_data.current_config)

        run_progress_data = [TaskProgressModel() for _ in range(configuration.max_algorithm_runs)]
        for _ in range(configuration.max_algorithm_runs):
            task_progress_model = TaskProgressModel()
            task_progress_model.max_steps = configuration.max_algorithm_steps
            run_progress_data.append(task_progress_model)

        self.runner.run_progress_data = run_progress_data


class Runner(GenericWidget):
    MAX_RUNS = 100
    REFRESH_GUI_TIME = 100

    def __init__(self, scheduler):
        super().__init__(Ui_runner)
        self.logger = logging.getLogger(__name__)
        self.scheduler = scheduler

        self.simulation_worker = SimulationWorker(self)

        self.run_progress_views = [RunProgressView(i, self) for i in range(self.MAX_RUNS)]
        self.run_progress_data = []
        self.children += self.run_progress_views

        dynamic_tree = DynamicNode(
            self.ui.allTasksProgressBar,
            self.ui.currentDataFileLineEdit,
            self.ui.currentConfigFileLineEdit,
            self.ui.currentAlgorithmPhaseLlineEdit,
            auto_updater=RunnerSimulationDataAutoUpdater(self)
        )

        self.dynamic_nodes.append(dynamic_tree)

        self._original_close_event = self.widget.closeEvent
        self.widget.closeEvent = self.close_event_with_cleanup

        self.init_gui_dn()
        self.bind_dn()

        self.on_gui_invalidated()
        self.update_timer = QtCore.QTimer(self.widget)
        # noinspection PyUnresolvedReferences
        self.update_timer.timeout.connect(self.on_gui_invalidated)
        self.update_timer.start(self.REFRESH_GUI_TIME)

    def on_gui_invalidated(self):
        self.dynamic_gui_update()

    def close_event_with_cleanup(self, ev):
        self.simulation_worker.is_running = False
        self.simulation_worker.terminate()
        self.scheduler.widget.setEnabled(True)
        self._original_close_event(ev)
