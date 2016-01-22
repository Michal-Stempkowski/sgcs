import logging
import sys
from optparse import OptionParser

from PyQt4 import QtGui

from algorithm.task_model import TaskModel
from gui.non_gui_scheduler import NonGuiScheduler
from gui.runner import Runner
from utils import chunk


def main():
    logging.basicConfig(
        level=logging.INFO,
        filename=r"C:\Users\Michał\PycharmProjects\mgr\sgcs\log.log",
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
        app = QtGui.QApplication(sys.argv)
        scheduler = NonGuiScheduler(options.output, tasks)
        input_data_lookup = Runner(scheduler)
        input_data_lookup.show()
        sys.exit(app.exec_())

if __name__ == '__main__':
    main()
