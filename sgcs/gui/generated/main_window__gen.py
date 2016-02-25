# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\main_window.ui'
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

class Ui_InputDataLookup(object):
    def setupUi(self, InputDataLookup):
        InputDataLookup.setObjectName(_fromUtf8("InputDataLookup"))
        InputDataLookup.resize(834, 629)
        self.horizontalLayout_8 = QtGui.QHBoxLayout(InputDataLookup)
        self.horizontalLayout_8.setObjectName(_fromUtf8("horizontalLayout_8"))
        self.tabWidget_2 = QtGui.QTabWidget(InputDataLookup)
        self.tabWidget_2.setObjectName(_fromUtf8("tabWidget_2"))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.horizontalLayout_7 = QtGui.QHBoxLayout(self.tab_3)
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.tabWidget = QtGui.QTabWidget(self.tab_3)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.verticalLayout = QtGui.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(self.tab)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.lineEdit = QtGui.QLineEdit(self.groupBox)
        self.lineEdit.setEnabled(False)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.pushButton = QtGui.QPushButton(self.groupBox)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.horizontalLayout_2.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(self.tab)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.scrollArea = QtGui.QScrollArea(self.groupBox_2)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 746, 426))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.tableWidget = QtGui.QTableWidget(self.scrollAreaWidgetContents)
        self.tableWidget.setEnabled(False)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayout.addWidget(self.tableWidget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.tab_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_3 = QtGui.QGroupBox(self.tab_2)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.lineEdit_2 = QtGui.QLineEdit(self.groupBox_3)
        self.lineEdit_2.setEnabled(False)
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.horizontalLayout_4.addWidget(self.lineEdit_2)
        self.pushButton_2 = QtGui.QPushButton(self.groupBox_3)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.horizontalLayout_4.addWidget(self.pushButton_2)
        self.verticalLayout_2.addWidget(self.groupBox_3)
        self.groupBox_4 = QtGui.QGroupBox(self.tab_2)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.scrollArea_2 = QtGui.QScrollArea(self.groupBox_4)
        self.scrollArea_2.setWidgetResizable(True)
        self.scrollArea_2.setObjectName(_fromUtf8("scrollArea_2"))
        self.scrollAreaWidgetContents_2 = QtGui.QWidget()
        self.scrollAreaWidgetContents_2.setGeometry(QtCore.QRect(0, 0, 746, 426))
        self.scrollAreaWidgetContents_2.setObjectName(_fromUtf8("scrollAreaWidgetContents_2"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.tableWidget_2 = QtGui.QTableWidget(self.scrollAreaWidgetContents_2)
        self.tableWidget_2.setEnabled(False)
        self.tableWidget_2.setObjectName(_fromUtf8("tableWidget_2"))
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)
        self.horizontalLayout_6.addWidget(self.tableWidget_2)
        self.scrollArea_2.setWidget(self.scrollAreaWidgetContents_2)
        self.horizontalLayout_5.addWidget(self.scrollArea_2)
        self.verticalLayout_2.addWidget(self.groupBox_4)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.horizontalLayout_7.addWidget(self.tabWidget)
        self.tabWidget_2.addTab(self.tab_3, _fromUtf8(""))
        self.tab_4 = QtGui.QWidget()
        self.tab_4.setObjectName(_fromUtf8("tab_4"))
        self.tabWidget_2.addTab(self.tab_4, _fromUtf8(""))
        self.horizontalLayout_8.addWidget(self.tabWidget_2)

        self.retranslateUi(InputDataLookup)
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(InputDataLookup)

    def retranslateUi(self, InputDataLookup):
        InputDataLookup.setWindowTitle(_translate("InputDataLookup", "Form", None))
        self.groupBox.setTitle(_translate("InputDataLookup", "Select file with learning set", None))
        self.pushButton.setText(_translate("InputDataLookup", "load", None))
        self.groupBox_2.setTitle(_translate("InputDataLookup", "File lookup", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("InputDataLookup", "Learning set lookup", None))
        self.groupBox_3.setTitle(_translate("InputDataLookup", "Select file with testing set", None))
        self.pushButton_2.setText(_translate("InputDataLookup", "load", None))
        self.groupBox_4.setTitle(_translate("InputDataLookup", "File lookup", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("InputDataLookup", "Testing set lookup", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("InputDataLookup", "Input", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("InputDataLookup", "Tab 2", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    InputDataLookup = QtGui.QWidget()
    ui = Ui_InputDataLookup()
    ui.setupUi(InputDataLookup)
    InputDataLookup.show()
    sys.exit(app.exec_())

