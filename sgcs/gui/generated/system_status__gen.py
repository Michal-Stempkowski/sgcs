# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\system_status.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_systemStatus(object):
    def setupUi(self, systemStatus):
        systemStatus.setObjectName(_fromUtf8("systemStatus"))
        systemStatus.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(systemStatus)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.cpuBox = QtGui.QGroupBox(systemStatus)
        self.cpuBox.setObjectName(_fromUtf8("cpuBox"))
        self.verticalLayout.addWidget(self.cpuBox)
        self.memoryBox = QtGui.QGroupBox(systemStatus)
        self.memoryBox.setObjectName(_fromUtf8("memoryBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.memoryBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.memoryProgressBar = QtGui.QProgressBar(self.memoryBox)
        self.memoryProgressBar.setProperty("value", 0)
        self.memoryProgressBar.setObjectName(_fromUtf8("memoryProgressBar"))
        self.verticalLayout_2.addWidget(self.memoryProgressBar)
        self.verticalLayout.addWidget(self.memoryBox)

        self.retranslateUi(systemStatus)
        QtCore.QMetaObject.connectSlotsByName(systemStatus)

    def retranslateUi(self, systemStatus):
        systemStatus.setWindowTitle(_translate("systemStatus", "System Status", None))
        self.cpuBox.setTitle(_translate("systemStatus", "CPU", None))
        self.memoryBox.setTitle(_translate("systemStatus", "Memory", None))
        self.memoryProgressBar.setFormat(_translate("systemStatus", "%p%", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    systemStatus = QtGui.QWidget()
    ui = Ui_systemStatus()
    ui.setupUi(systemStatus)
    systemStatus.show()
    sys.exit(app.exec_())

