# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\scheduler.ui'
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

class Ui_scheduler(object):
    def setupUi(self, scheduler):
        scheduler.setObjectName(_fromUtf8("scheduler"))
        scheduler.resize(502, 362)
        self.verticalLayout = QtGui.QVBoxLayout(scheduler)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(scheduler)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.scrollArea = QtGui.QScrollArea(self.groupBox)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 462, 198))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.queueVerticalLayout = QtGui.QVBoxLayout()
        self.queueVerticalLayout.setObjectName(_fromUtf8("queueVerticalLayout"))
        self.verticalLayout_4.addLayout(self.queueVerticalLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.verticalLayout_2.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_3 = QtGui.QGroupBox(scheduler)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.outputDirectorylineEdit = QtGui.QLineEdit(self.groupBox_3)
        self.outputDirectorylineEdit.setReadOnly(True)
        self.outputDirectorylineEdit.setObjectName(_fromUtf8("outputDirectorylineEdit"))
        self.horizontalLayout_2.addWidget(self.outputDirectorylineEdit)
        self.outputDirectoryButton = QtGui.QPushButton(self.groupBox_3)
        self.outputDirectoryButton.setObjectName(_fromUtf8("outputDirectoryButton"))
        self.horizontalLayout_2.addWidget(self.outputDirectoryButton)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_2 = QtGui.QGroupBox(scheduler)
        self.groupBox_2.setTitle(_fromUtf8(""))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.addTaskButton = QtGui.QPushButton(self.groupBox_2)
        self.addTaskButton.setObjectName(_fromUtf8("addTaskButton"))
        self.horizontalLayout.addWidget(self.addTaskButton)
        self.clearTasksButton = QtGui.QPushButton(self.groupBox_2)
        self.clearTasksButton.setObjectName(_fromUtf8("clearTasksButton"))
        self.horizontalLayout.addWidget(self.clearTasksButton)
        self.runTasksButton = QtGui.QPushButton(self.groupBox_2)
        self.runTasksButton.setObjectName(_fromUtf8("runTasksButton"))
        self.horizontalLayout.addWidget(self.runTasksButton)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(scheduler)
        QtCore.QMetaObject.connectSlotsByName(scheduler)

    def retranslateUi(self, scheduler):
        scheduler.setWindowTitle(_translate("scheduler", "Scheduler", None))
        self.groupBox.setTitle(_translate("scheduler", "Execution Queue", None))
        self.groupBox_3.setTitle(_translate("scheduler", "Output directory:", None))
        self.outputDirectoryButton.setText(_translate("scheduler", "Select output dir", None))
        self.addTaskButton.setText(_translate("scheduler", "Add Task", None))
        self.clearTasksButton.setText(_translate("scheduler", "Clear Tasks", None))
        self.runTasksButton.setText(_translate("scheduler", "Run Tasks", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    scheduler = QtGui.QWidget()
    ui = Ui_scheduler()
    ui.setupUi(scheduler)
    scheduler.show()
    sys.exit(app.exec_())

