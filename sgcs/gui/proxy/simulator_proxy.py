import datetime
from PyQt4 import QtCore

from algorithm.gcs_runner import GcsRunner
from algorithm.gcs_simulator import AsyncGcsSimulator


class RunResult(object):
    SIGNAL = 'PROXY_RUN_RESULT_SIGNAL'

    def __init__(self, task_no, run_id, has_succeeded, fitness_reached, run_estimator, evolution_step):
        self.task_no = task_no
        self.run_id = run_id
        self.has_succeeded = has_succeeded
        self.fitness_reached = fitness_reached
        self.run_estimator = run_estimator
        self.evolution_step = evolution_step


class PyQtAwareAsyncGcsSimulator(AsyncGcsSimulator):
    TIME_FORMAT = '%I:%M:%S %p; %B %d, %Y'
    START_TIME_SIGNAL = 'PROXY_START_TIME_SIGNAL'
    END_TIME_SIGNAL = 'PROXY_END_TIME_SIGNAL'
    TESTING_HAS_STARTED_SIGNAL = 'PROXY_TESTING_HAS_STARTED_SIGNAL'

    def __init__(self, randomizer, algorithm_variant, task_no, pyqt_hook):
        super().__init__(randomizer, algorithm_variant)
        self.pyqt_hook = pyqt_hook
        self.task_no = task_no

    def _handle_run_result(self, stop_reasoning, learning_set, run_estimator, rp, rule_population,
                           fitness_reached, auxiliary_rule_population, aux_fitness, evolution_step,
                           run_no):

        message = RunResult(
            task_no=self.task_no,
            run_id=run_no,
            has_succeeded=stop_reasoning.has_succeeded(),
            fitness_reached=fitness_reached,
            run_estimator=run_estimator,
            evolution_step=evolution_step
        )

        self.pyqt_hook.put((RunResult.SIGNAL, message))

        return super()._handle_run_result(
            stop_reasoning, learning_set, run_estimator, rp, rule_population, fitness_reached,
            auxiliary_rule_population, aux_fitness, evolution_step, run_no)

    def _perform_run(self, configuration, initial_rules, sentences, run_no):
        start_time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        self.pyqt_hook.put((self.START_TIME_SIGNAL, (self.task_no, run_no, start_time)))
        result = super()._perform_run(configuration, initial_rules, sentences, run_no)
        end_time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        self.pyqt_hook.put((self.END_TIME_SIGNAL, (self.task_no, run_no, end_time)))
        return result

    def _create_gcs_runner(self, run_no):
        return PyQtAwareGcsRunner(
            self.randomizer, run_no, self.pyqt_hook, self.task_no, self.algorithm_variant)

    def _generalization_run(self, conf, rules, sentences):
        self.pyqt_hook.put((self.TESTING_HAS_STARTED_SIGNAL, (self.task_no,)))
        result = super()._generalization_run(conf, rules, sentences)

        return result


class PyQtAwareGcsRunner(GcsRunner):
    STEP_SIGNAL = 'PROXY_STEP_SIGNAL'

    def __init__(self, randomizer, run_no, pyqt_hook, task_no, cyk_service_variant=None):
        super().__init__(randomizer, run_no, cyk_service_variant)
        self.task_no = task_no
        self.pyqt_hook = pyqt_hook

    def _post_step_actions(self, step):
        super()._post_step_actions(step)
        self.pyqt_hook.put((self.STEP_SIGNAL, (self.task_no, self.run_no, step)))
