import os
import sys

from PyQt4 import QtGui

from gui.input_data_lookup import InputDataLookup
from gui.options_configurator import OptionsConfigurator


def main():
    app = QtGui.QApplication(sys.argv)
    input_data_lookup = OptionsConfigurator(os.getcwd())
    input_data_lookup.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
