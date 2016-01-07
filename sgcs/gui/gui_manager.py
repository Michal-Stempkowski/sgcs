import logging
import os
import sys

from PyQt4 import QtGui

from gui.input_data_lookup import InputDataLookup
from gui.main_app import MainApp
from gui.options_configurator import OptionsConfigurator
from gui.scheduler import Scheduler
from gui.system_status import SystemStatus


def main():
    logging.basicConfig(level=logging.DEBUG)
    app = QtGui.QApplication(sys.argv)
    input_data_lookup = MainApp()
    input_data_lookup.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
