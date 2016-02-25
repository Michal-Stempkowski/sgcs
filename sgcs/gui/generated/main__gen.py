# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\main.ui'
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

class Ui_mainApp(object):
    def setupUi(self, mainApp):
        mainApp.setObjectName(_fromUtf8("mainApp"))
        mainApp.resize(400, 300)
        self.verticalLayout = QtGui.QVBoxLayout(mainApp)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputDataLookupButton = QtGui.QPushButton(mainApp)
        self.inputDataLookupButton.setObjectName(_fromUtf8("inputDataLookupButton"))
        self.verticalLayout.addWidget(self.inputDataLookupButton)
        self.optionsConfiguratorButton = QtGui.QPushButton(mainApp)
        self.optionsConfiguratorButton.setObjectName(_fromUtf8("optionsConfiguratorButton"))
        self.verticalLayout.addWidget(self.optionsConfiguratorButton)
        self.editPopulationPushButton = QtGui.QPushButton(mainApp)
        self.editPopulationPushButton.setObjectName(_fromUtf8("editPopulationPushButton"))
        self.verticalLayout.addWidget(self.editPopulationPushButton)
        self.schedulerButton = QtGui.QPushButton(mainApp)
        self.schedulerButton.setObjectName(_fromUtf8("schedulerButton"))
        self.verticalLayout.addWidget(self.schedulerButton)
        self.systemStatusButton = QtGui.QPushButton(mainApp)
        self.systemStatusButton.setObjectName(_fromUtf8("systemStatusButton"))
        self.verticalLayout.addWidget(self.systemStatusButton)

        self.retranslateUi(mainApp)
        QtCore.QMetaObject.connectSlotsByName(mainApp)

    def retranslateUi(self, mainApp):
        mainApp.setWindowTitle(_translate("mainApp", "Main", None))
        self.inputDataLookupButton.setText(_translate("mainApp", "Prepare input data", None))
        self.optionsConfiguratorButton.setText(_translate("mainApp", "Prepare configuration", None))
        self.editPopulationPushButton.setText(_translate("mainApp", "Edit population", None))
        self.schedulerButton.setText(_translate("mainApp", "Run simulations", None))
        self.systemStatusButton.setText(_translate("mainApp", "System status", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    mainApp = QtGui.QWidget()
    ui = Ui_mainApp()
    ui.setupUi(mainApp)
    mainApp.show()
    sys.exit(app.exec_())

