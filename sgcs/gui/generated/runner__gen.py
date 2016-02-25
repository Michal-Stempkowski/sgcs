# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\runner.ui'
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

class Ui_runner(object):
    def setupUi(self, runner):
        runner.setObjectName(_fromUtf8("runner"))
        runner.resize(280, 260)
        self.gridLayout = QtGui.QGridLayout(runner)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(runner)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.currentDataFileLineEdit = QtGui.QLineEdit(self.groupBox)
        self.currentDataFileLineEdit.setReadOnly(True)
        self.currentDataFileLineEdit.setObjectName(_fromUtf8("currentDataFileLineEdit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.currentDataFileLineEdit)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.currentConfigFileLineEdit = QtGui.QLineEdit(self.groupBox)
        self.currentConfigFileLineEdit.setReadOnly(True)
        self.currentConfigFileLineEdit.setObjectName(_fromUtf8("currentConfigFileLineEdit"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.currentConfigFileLineEdit)
        self.currentAlgorithmPhaseLlineEdit = QtGui.QLineEdit(self.groupBox)
        self.currentAlgorithmPhaseLlineEdit.setReadOnly(True)
        self.currentAlgorithmPhaseLlineEdit.setObjectName(_fromUtf8("currentAlgorithmPhaseLlineEdit"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.currentAlgorithmPhaseLlineEdit)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_4)
        self.allTasksProgressBar = QtGui.QProgressBar(self.groupBox)
        self.allTasksProgressBar.setProperty("value", 0)
        self.allTasksProgressBar.setObjectName(_fromUtf8("allTasksProgressBar"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.allTasksProgressBar)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(runner)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.runScrollArea = QtGui.QScrollArea(self.groupBox_2)
        self.runScrollArea.setWidgetResizable(True)
        self.runScrollArea.setObjectName(_fromUtf8("runScrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 240, 69))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.runProgressVerticalLayout = QtGui.QVBoxLayout()
        self.runProgressVerticalLayout.setObjectName(_fromUtf8("runProgressVerticalLayout"))
        self.verticalLayout_3.addLayout(self.runProgressVerticalLayout)
        self.runScrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.runScrollArea)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)

        self.retranslateUi(runner)
        QtCore.QMetaObject.connectSlotsByName(runner)

    def retranslateUi(self, runner):
        runner.setWindowTitle(_translate("runner", "Runner", None))
        self.groupBox.setTitle(_translate("runner", "Simulation data", None))
        self.label.setText(_translate("runner", "Tasks progress:", None))
        self.label_2.setText(_translate("runner", "Current data file:", None))
        self.label_3.setText(_translate("runner", "Current config file:", None))
        self.label_4.setText(_translate("runner", "Current phase:", None))
        self.allTasksProgressBar.setFormat(_translate("runner", "%v/%m", None))
        self.groupBox_2.setTitle(_translate("runner", "Run data", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    runner = QtGui.QWidget()
    ui = Ui_runner()
    ui.setupUi(runner)
    runner.show()
    sys.exit(app.exec_())

