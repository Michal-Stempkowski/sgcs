from PyQt4 import QtGui

from gui.dynamic_gui import DynamicRoot


class GenericWidget(DynamicRoot):
    def __init__(self, generated_class):
        super().__init__()
        self.widget = QtGui.QWidget()
        self.ui = generated_class()
        self.ui.setupUi(self.widget)

    def show(self):
        self.widget.show()

    @staticmethod
    def lock_size(widget):
        widget.setFixedWidth(widget.width())
        widget.setFixedHeight(widget.height())
