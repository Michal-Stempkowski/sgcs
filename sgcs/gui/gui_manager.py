import os
import sys

from PyQt4 import QtGui

from gui.input_data_lookup import InputDataLookup


def main():
    app = QtGui.QApplication(sys.argv)
    input_data_lookup = InputDataLookup(os.getcwd())
    input_data_lookup.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
