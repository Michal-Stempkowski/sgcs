# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\population_editor.ui'
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

class Ui_populationEditor(object):
    def setupUi(self, populationEditor):
        populationEditor.setObjectName(_fromUtf8("populationEditor"))
        populationEditor.resize(422, 393)
        self.verticalLayout = QtGui.QVBoxLayout(populationEditor)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(populationEditor)
        self.groupBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_2 = QtGui.QGroupBox(self.groupBox)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.learningSetLineEdit = QtGui.QLineEdit(self.groupBox_2)
        self.learningSetLineEdit.setReadOnly(True)
        self.learningSetLineEdit.setObjectName(_fromUtf8("learningSetLineEdit"))
        self.horizontalLayout.addWidget(self.learningSetLineEdit)
        self.loadLearningSetPushButton = QtGui.QPushButton(self.groupBox_2)
        self.loadLearningSetPushButton.setObjectName(_fromUtf8("loadLearningSetPushButton"))
        self.horizontalLayout.addWidget(self.loadLearningSetPushButton)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.controlButtonBox = QtGui.QDialogButtonBox(self.groupBox)
        self.controlButtonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.controlButtonBox.setStandardButtons(QtGui.QDialogButtonBox.Open|QtGui.QDialogButtonBox.Reset|QtGui.QDialogButtonBox.Save)
        self.controlButtonBox.setCenterButtons(True)
        self.controlButtonBox.setObjectName(_fromUtf8("controlButtonBox"))
        self.verticalLayout_2.addWidget(self.controlButtonBox)
        self.verticalLayout.addWidget(self.groupBox)
        self.scrollArea = QtGui.QScrollArea(populationEditor)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 402, 187))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.rules_layout = QtGui.QVBoxLayout()
        self.rules_layout.setObjectName(_fromUtf8("rules_layout"))
        self.verticalLayout_4.addLayout(self.rules_layout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout.addWidget(self.scrollArea)
        self.rulesModificationsgroupBox = QtGui.QGroupBox(populationEditor)
        self.rulesModificationsgroupBox.setObjectName(_fromUtf8("rulesModificationsgroupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.rulesModificationsgroupBox)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.addTerminalPushButton = QtGui.QPushButton(self.rulesModificationsgroupBox)
        self.addTerminalPushButton.setObjectName(_fromUtf8("addTerminalPushButton"))
        self.horizontalLayout_2.addWidget(self.addTerminalPushButton)
        self.addNonTerminalPushButton = QtGui.QPushButton(self.rulesModificationsgroupBox)
        self.addNonTerminalPushButton.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.addNonTerminalPushButton.setObjectName(_fromUtf8("addNonTerminalPushButton"))
        self.horizontalLayout_2.addWidget(self.addNonTerminalPushButton)
        self.verticalLayout.addWidget(self.rulesModificationsgroupBox)

        self.retranslateUi(populationEditor)
        QtCore.QMetaObject.connectSlotsByName(populationEditor)

    def retranslateUi(self, populationEditor):
        populationEditor.setWindowTitle(_translate("populationEditor", "Population Editor", None))
        self.groupBox.setTitle(_translate("populationEditor", "Control box", None))
        self.groupBox_2.setTitle(_translate("populationEditor", "Learning set", None))
        self.loadLearningSetPushButton.setText(_translate("populationEditor", "Load", None))
        self.rulesModificationsgroupBox.setTitle(_translate("populationEditor", "Rules Modifications", None))
        self.addTerminalPushButton.setText(_translate("populationEditor", "Add new terminal rule", None))
        self.addNonTerminalPushButton.setText(_translate("populationEditor", "Add new non-terminal rule", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    populationEditor = QtGui.QWidget()
    ui = Ui_populationEditor()
    ui.setupUi(populationEditor)
    populationEditor.show()
    sys.exit(app.exec_())

