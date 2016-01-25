import logging
from PyQt4 import QtGui, QtCore
import psutil as psutil
from gui.generated.system_status__gen import Ui_systemStatus
from gui.generic_widget import GenericWidget


class SystemStatus(GenericWidget):
    CPU_USAGE_SIGNAL = 'CPU_USAGE_SIGNAL'

    def __init__(self):
        super().__init__(Ui_systemStatus)
        self.logger = logging.getLogger(__name__)
        
        self.cpu_count = psutil.cpu_count()
        self.monitors = []

        self.cpu_usage_worker = CpuUsageWorker(self.widget)

        self.cpu_layout = QtGui.QVBoxLayout(self.ui.cpuBox)
        
        for i in range(self.cpu_count):
            self.create_cpu_usage_monitor(i)

        self._original_close_event = self.widget.closeEvent
        self.widget.closeEvent = self.close_event_with_stopping_worker

        self.widget.connect(self.cpu_usage_worker, QtCore.SIGNAL(SystemStatus.CPU_USAGE_SIGNAL),
                            self.on_cpu_usage_signal)

        self.cpu_usage_worker.start()

    def create_cpu_usage_monitor(self, i):
        monitor = CpuUsageMonitor(self, i)
        self.monitors.append(monitor)
        monitor.start()

    def close_event_with_stopping_worker(self, ev):
        self.cpu_usage_worker.is_running = False
        self._original_close_event(ev)

    def on_cpu_usage_signal(self, usage_data):
        self.ui.memoryProgressBar.setValue(usage_data[1])


class CpuUsageMonitor(object):
    def __init__(self, system_status, identifier):
        self.progress_bar = QtGui.QProgressBar()
        self.identifier = identifier
        self.system_status = system_status

        self.system_status.cpu_layout.addWidget(self.progress_bar)

    def start(self):
        self.system_status.widget.connect(self.system_status.cpu_usage_worker,
                                          QtCore.SIGNAL(SystemStatus.CPU_USAGE_SIGNAL),
                                          self.on_cpu_usage_signal)

    def on_cpu_usage_signal(self, usage_data):
        self.progress_bar.setValue(usage_data[0][self.identifier])


class CpuUsageWorker(QtCore.QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            usage_data = psutil.cpu_percent(interval=1, percpu=1), psutil.virtual_memory().percent
            self.emit(QtCore.SIGNAL(SystemStatus.CPU_USAGE_SIGNAL), usage_data)
