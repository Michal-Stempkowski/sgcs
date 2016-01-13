import logging
import unittest

from hamcrest import *
from mock import create_autospec

from executors.simulation_executor import SimulationExecutor


class QueueDummy(object):
    def get(self, *args, **kwargs):
        pass

    def put(self, *args, **kwargs):
        pass


class RunnerDummy(object):
    def __init__(self):
        self.input_queue = QueueDummy()


class LongTestSimulationExecutor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logging.basicConfig(level=logging.INFO,
                            filename=r"C:\Users\Michał\PycharmProjects\mgr\sgcs\log.log",
                            format='%(asctime)s %(message)s')

        self.sut = SimulationExecutor()
        self.runner_dummy = RunnerDummy()
        self.task_no = 0
        self.config_path = \
            r"C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\data\experimental\unold0.parconf"

    def test_tomita_1(self):
        input_data = r"C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\data\experimental\t1.inconf"
        run_func, conf = self.sut.prepare_simulation(
            self.runner_dummy, self.task_no, input_data, self.config_path)
        run_func(conf)
