from PyQt4 import QtGui, QtCore

from gui.dynamic_gui import DynamicRoot


class GenericWidget(DynamicRoot):
    CLOSING_SIGNAL = 'GENERIC_WIDGET_CLOSING_SIGNAL'

    def __init__(self, generated_class):
        super().__init__()
        self.widget = QtGui.QWidget()
        self.ui = generated_class()
        self.ui.setupUi(self.widget)
        self._original_windows_close = self.widget.closeEvent
        self.widget.closeEvent = lambda ev: self._close_event(self.widget, ev)

    def show(self):
        self.widget.show()

    def _close_event(self, widget, event):
        self.widget.emit(QtCore.SIGNAL(self.CLOSING_SIGNAL), self.__class__.__name__)
        self._original_windows_close(event)

    @staticmethod
    def lock_size(widget):
        widget.setFixedWidth(widget.width())
        widget.setFixedHeight(widget.height())
