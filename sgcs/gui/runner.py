import logging
import os
import queue
import shutil
from multiprocessing import Queue

import multiprocessing

import psutil
from PyQt4 import QtCore, QtGui

from executors.simulation_executor import SimulationExecutor
from gui.dynamic_gui import DynamicNode, AutoUpdater, DynamicRoot
from gui.generated.runner__gen import Ui_runner
from gui.generic_widget import GenericWidget
from gui.proxy.simulator_proxy import RunResult, PyQtAwareAsyncGcsSimulator, PyQtAwareGcsRunner
from utils import rmdir_forced


class RunPostMortemModel(object):
    def __init__(self):
        self.max_steps = None
        self.is_done = False
        self.task_no = 0


class RunVolatileModel(object):
    def __init__(self):
        self.start_time = None
        self.progress = None
        self.end_time = None
        self.task_no = 0


class RunProgressAutoUpdater(AutoUpdater):
    def __init__(self, run_progress_view):
        super().__init__(
            lambda: self._bind(run_progress_view),
            lambda: self._update_model(run_progress_view),
            lambda: self._update_gui(run_progress_view),
            lambda: self._init_gui(run_progress_view)
        )

    def _init_gui(self, run_progress_view):
        run_progress_view.progress_bar.setFormat(
            run_progress_view.runner.ui.allTasksProgressBar.format())
        run_progress_view.progress_bar.setMinimum(0)
        self._update_gui(run_progress_view)

    def _bind(self, run_progress_view):
        pass

    @staticmethod
    def _update_gui(run_progress_view):
        progress_data = run_progress_view.runner.run_progress_data
        volatile_progress_data = run_progress_view.runner.run_volatile_data
        if run_progress_view.index < len(progress_data):
            volatile_task_no = volatile_progress_data[run_progress_view.index].task_no
            volatile_start = volatile_progress_data[run_progress_view.index].start_time
            volatile_progress = volatile_progress_data[run_progress_view.index].progress
            volatile_end = volatile_progress_data[run_progress_view.index].end_time
            data = progress_data[run_progress_view.index]

            volatile_start = volatile_start if volatile_start is not None else \
                RunnerGuiModel.FIELD_UNDEFINED

            volatile_progress = volatile_progress if volatile_progress is not None else 0

            volatile_end = volatile_end if volatile_end is not None else \
                RunnerGuiModel.FIELD_UNDEFINED

            if data.task_no is not None:
                run_progress_view.progress_bar.setValue(volatile_progress)
                run_progress_view.progress_bar.setMaximum(data.max_steps)

                run_progress_view.start_time_line.setText(volatile_start)
                run_progress_view.end_time_line.setText(volatile_end)

                run_progress_view.steps_line.setText('{0}/{1}'.format(
                    volatile_progress, data.max_steps))

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
    PERMISSION_ERROR = 'No permission to write artifacts!'


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

    @staticmethod
    def _bind(runner):
        runner.simulation_worker.start()
        runner.partial_information_worker.start()

    @staticmethod
    def _update_gui(runner):
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
    TASK_CONFIRMED_FINISHED_SIGNAL = 'TASK_CONFIRMED_FINISHED_SIGNAL'
    ALL_TASKS_FINISHED_SIGNAL = 'ALL_TASKS_FINISHED_SIGNAL'

    def __init__(self, runner):
        super().__init__(runner.widget)
        self.runner = runner
        self.is_running = False
        self.simulation_executor = SimulationExecutor()
        self.current_data = RunnerGuiModel()
        self.root_dir = self.runner.scheduler.ui.outputDirectorylineEdit.text()

    def run(self):
        for i, task in enumerate(self.runner.scheduler.tasks):
            run_func, configuration = self._setup_task(i, task)
            result = self._run_task(run_func, configuration)

            collected = False
            while not collected:
                try:
                    self._collect_task(result, i, configuration)
                except PermissionError:
                    collected = False
                    self.current_data.current_phase = SimulationPhases.PERMISSION_ERROR
                else:
                    collected = True
                    self.current_data.current_phase = SimulationPhases.COLLECTING

        self.current_data.current_phase = SimulationPhases.DONE
        self.emit(QtCore.SIGNAL(self.ALL_TASKS_FINISHED_SIGNAL))

    def _setup_task(self, task_no, task):
        new_data = RunnerGuiModel()
        new_data.tasks_progress = task_no
        new_data.current_input = task.data_configuration
        new_data.current_config = task.params_configuration
        new_data.current_phase = SimulationPhases.SETUP
        self.current_data = new_data

        run_func, configuration = self.simulation_executor.prepare_simulation(
            self.runner, task_no, new_data.current_input, new_data.current_config)

        run_post_mortem_data = []
        for _ in range(configuration.max_algorithm_runs):
            task_progress_model = RunPostMortemModel()
            task_progress_model.max_steps = configuration.max_algorithm_steps
            task_progress_model.task_no = task_no
            run_post_mortem_data.append(task_progress_model)

        self.runner.run_progress_data = run_post_mortem_data

        return run_func, configuration

    def _run_task(self, run_func, configuration):
        self.current_data.current_phase = SimulationPhases.LEARNING
        return run_func(configuration)

    def _collect_task(self, result, task_id, configuration):
        self.current_data.current_phase = SimulationPhases.COLLECTING
        run_estimator, ngen, grammar_estimator, population = result

        path = self._prepare_artifact_dir(task_id)

        input_data_name = os.path.basename(self.current_data.current_input)
        config_data_name = os.path.basename(self.current_data.current_config)

        shutil.copy(self.current_data.current_input, os.path.join(path, input_data_name))
        shutil.copy(self.current_data.current_config, os.path.join(path, config_data_name))

        self.simulation_executor.save_population(
            population, path, 'final_population'
        )
        self.simulation_executor.save_grammar_estimator(
            grammar_estimator, path, 'grammar_estimator'
        )
        self.simulation_executor.save_execution_summary(
            run_estimator, ngen, path, 'run_summary'
        )
        self.simulation_executor.generate_grammar_estimation_diagrams(
            grammar_estimator, path, configuration
        )

    def _prepare_artifact_dir(self, task_id):
        path = os.path.join(self.root_dir, 'task_{0}'.format(task_id))
        if os.path.exists(path):
            rmdir_forced(path)

        os.mkdir(path)
        return path


class PartialInformationWorker(QtCore.QThread):
    TIMEOUT = 10

    def __init__(self, runner):
        super().__init__(runner.widget)
        self.runner = runner
        self.is_running = True

    def run(self):
        while self.is_running:
            try:
                message = self.runner.input_queue.get(timeout=self.TIMEOUT)
            except queue.Empty:
                pass
            else:
                message_type, value = message

                if message_type == PyQtAwareAsyncGcsSimulator.START_TIME_SIGNAL:
                    task_no, run_id, start_time = value
                    if run_id is not None:
                        self.runner.run_volatile_data[run_id].start_time = start_time
                        self.runner.run_volatile_data[run_id].task_no = task_no

                elif message_type == PyQtAwareAsyncGcsSimulator.END_TIME_SIGNAL:
                    task_no, run_id, end_time = value
                    if run_id is not None:
                        self.runner.run_volatile_data[run_id].end_time = end_time
                        self.runner.run_volatile_data[run_id].task_no = task_no

                elif message_type == RunResult.SIGNAL:
                    previous_state = self.runner.run_progress_data
                    if value.run_id < len(previous_state):
                        old = previous_state[value.run_id]
                        post_mortem_model = RunPostMortemModel()
                        post_mortem_model.max_steps = old.max_steps
                        post_mortem_model.is_done = True
                        post_mortem_model.task_no = value.task_no

                        previous_state[value.run_id] = post_mortem_model

                elif message_type == PyQtAwareGcsRunner.STEP_SIGNAL:
                    task_no, run_id, step = value
                    if run_id is not None:
                        self.runner.run_volatile_data[run_id].progress = step
                        self.runner.run_volatile_data[run_id].task_no = task_no

                elif message_type == PyQtAwareAsyncGcsSimulator.TESTING_HAS_STARTED_SIGNAL:
                    task_no, = value
                    self.runner.simulation_worker.current_data.current_phase = \
                        SimulationPhases.TESTING


class Runner(GenericWidget):
    MAX_RUNS = 100
    REFRESH_GUI_TIME = 1000

    def __init__(self, scheduler):
        super().__init__(Ui_runner)
        self.logger = logging.getLogger(__name__)
        self.scheduler = scheduler

        self._multiprocessing_manager = multiprocessing.Manager()
        self.input_queue = self._multiprocessing_manager.Queue()
        self.simulation_worker = SimulationWorker(self)
        self.partial_information_worker = PartialInformationWorker(self)

        self.run_progress_views = [RunProgressView(i, self) for i in range(self.MAX_RUNS)]
        self.run_progress_data = []
        self.run_volatile_data = [RunVolatileModel() for _ in range(self.MAX_RUNS)]
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
        self.simulation_worker.connect(
            self.simulation_worker,
            QtCore.SIGNAL(self.simulation_worker.ALL_TASKS_FINISHED_SIGNAL),
            self.on_all_tasks_finished)

    def on_gui_invalidated(self):
        self.dynamic_gui_update()

    def close_event_with_cleanup(self, ev):
        self.simulation_worker.is_running = False
        self.partial_information_worker.is_running = False
        self.simulation_worker.terminate()
        self.partial_information_worker.terminate()
        self.scheduler.widget.setEnabled(True)
        self._original_close_event(ev)

    def on_all_tasks_finished(self):
        QtGui.QMessageBox().about(self.widget, 'Info', SimulationPhases.DONE)
