from PyQt4 import QtGui


class GenericWidget(object):
    def __init__(self, generated_class):
        self.widget = QtGui.QWidget()
        self.ui = generated_class()
        self.ui.setupUi(self.widget)

    def show(self):
        self.widget.show()

    @staticmethod
    def lock_size(widget):
        widget.setFixedWidth(widget.width())
        widget.setFixedHeight(widget.height())
