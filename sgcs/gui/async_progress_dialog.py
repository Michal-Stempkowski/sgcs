from PyQt4 import QtGui, QtCore

from gui.generic_widget import GenericWidget


class AsyncProgressDialog(object):
    CHANGE_STEP_EVENT = 'AsyncProgressDialog.change_step'
    SET_PROGRESS_EVENT = 'AsyncProgressDialog.set_progress'
    RESET_EVENT = 'AsyncProgressDialog.reset'

    def __init__(self, parent, worker):
        self.parent = parent
        self.worker = worker
        self.dialog = QtGui.QProgressDialog(self.parent.widget)
        self.dialog.setModal(True)
        self.dialog.autoClose()
        self.dialog.connect(
            self.worker, QtCore.SIGNAL(self.CHANGE_STEP_EVENT), self._handle_change_step)
        self.dialog.connect(
            self.worker, QtCore.SIGNAL(self.SET_PROGRESS_EVENT), self._handle_set_progress)
        self.dialog.connect(
            self.worker, QtCore.SIGNAL(self.RESET_EVENT), self._handle_reset)

    def make_lean(self):
        self.dialog.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint)
        GenericWidget.lock_size(self.dialog)
        self.dialog.setCancelButton(None)

    def show(self):
        self.dialog.show()

    def _handle_change_step(self, step):
        self.dialog.setLabelText(step)

    def _handle_set_progress(self, progress):
        self.dialog.setValue(progress)

    def _handle_reset(self):
        self.dialog.reset()
