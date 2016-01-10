import datetime
from PyQt4 import QtCore

from algorithm.gcs_simulator import AsyncGcsSimulator


class RunResult(object):
    SIGNAL = 'PROXY_RUN_RESULT_SIGNAL'

    def __init__(self, run_id, has_succeeded, fitness_reached, run_estimator, evolution_step):
        self.run_id = run_id
        self.has_succeeded = has_succeeded
        self.fitness_reached = fitness_reached
        self.run_estimator = run_estimator
        self.evolution_step = evolution_step


class PyQtAwareAsyncGcsSimulator(AsyncGcsSimulator):
    TIME_FORMAT = '%I:%M:%S %p; %B %d, %Y'
    START_TIME_SIGNAL = 'PROXY_START_TIME_SIGNAL'
    END_TIME_SIGNAL = 'PROXY_END_TIME_SIGNAL'

    def __init__(self, randomizer, algorithm_variant, pyqt_hook):
        super().__init__(randomizer, algorithm_variant)
        self.pyqt_hook = pyqt_hook

    def _handle_run_result(self, stop_reasoning, learning_set, run_estimator, rp, rule_population,
                           fitness_reached, auxiliary_rule_population, aux_fitness, evolution_step,
                           run_no):

        message = RunResult(
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
        self.pyqt_hook.put((self.START_TIME_SIGNAL, (run_no, start_time)))
        result = super()._perform_run(configuration, initial_rules, sentences, run_no)
        end_time = datetime.datetime.now().strftime(self.TIME_FORMAT)
        self.pyqt_hook.put((self.END_TIME_SIGNAL, (run_no, end_time)))
        return result
