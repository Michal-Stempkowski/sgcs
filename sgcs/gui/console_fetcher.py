import logging
import os
import shutil
import sys
from optparse import OptionParser


from algorithm.task_model import TaskModel
from executors.simulation_executor import SimulationExecutor
from gui.non_gui_scheduler import NonGuiScheduler
from gui.runner import Runner
from utils import chunk, rmdir_forced


class DummyQueue(object):
    def put(*args, **kwargs):
        pass



class Runner(object):
    def __init__(self):
        self.input_queue = DummyQueue()




def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s'
    )
    usage = "usage: %prog -o OUTPUT_DIR [options] [input, config]..."
    parser = OptionParser(usage=usage)
    parser.add_option('-p', '--print_only', action="store_false", dest='run', default=True,
                      help='Only shows configuration, does not run it')
    parser.add_option('-o', '--output', dest='output', default=None,
                      help='Destination')
    options, args = parser.parse_args()

    if options.output is None:
        print("No output dir specified!")
        return

    print('artifact directory:', options.output)

    if not args or len(args) % 2 != 0:
        print("Invalid number of arguments!")
        return

    i = 0
    tasks = []
    for input_file, config_file in chunk(args, 2):
        print('Task', i)
        task = TaskModel()

        print('\tinput:', input_file)
        task.data_configuration = input_file

        print('\tconfig:', config_file)
        task.params_configuration = config_file

        tasks.append(task)

    if options.run:
        print('Starting run')
        executor = SimulationExecutor()
        runner = Runner()
        for i, x in enumerate(tasks):
            run_func, configuration, population_printer = executor.prepare_simulation(
                runner, i, x.data_configuration, x.params_configuration)

            result = run_func(configuration)

            collected = False
            while not collected:
                try:
                    _collect_task(x, result, i, configuration, population_printer, executor, options.output)
                except PermissionError:
                    collected = False
                    print('not collected!')
                else:
                    collected = True


def _collect_task(task, result, task_id, configuration, population_printer, executor, root_dir):
    run_estimator, ngen, grammar_estimator, population, generalisation_data = result

    path = _prepare_artifact_dir(task_id, root_dir)

    input_data_name = os.path.basename(task.data_configuration)
    config_data_name = os.path.basename(task.params_configuration)

    shutil.copy(task.data_configuration, os.path.join(path, input_data_name))
    shutil.copy(task.params_configuration, os.path.join(path, config_data_name))

    executor.save_population(
        population, population_printer, path, 'final_population'
    )
    executor.save_grammar_estimator(
        grammar_estimator, path, 'grammar_estimator'
    )
    executor.save_execution_summary(
        run_estimator, ngen, generalisation_data, path, 'run_summary'
    )
    executor.generate_grammar_estimation_diagrams(
        grammar_estimator, path, configuration
    )


def _prepare_artifact_dir(task_id, root_dir):
    path = os.path.join(root_dir, 'task_{0}'.format(task_id))
    if os.path.exists(path):
        rmdir_forced(path)

    os.mkdir(path)
    return path

if __name__ == '__main__':
    main()
