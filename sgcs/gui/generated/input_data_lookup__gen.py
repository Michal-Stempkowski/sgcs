# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\gui\input_data_lookup.ui'
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

class Ui_InputDataLookupGen(object):
    def setupUi(self, InputDataLookupGen):
        InputDataLookupGen.setObjectName(_fromUtf8("InputDataLookupGen"))
        InputDataLookupGen.resize(588, 522)
        self.verticalLayout = QtGui.QVBoxLayout(InputDataLookupGen)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_3 = QtGui.QGroupBox(InputDataLookupGen)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.groupBox_4 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.groupBox_4)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.filepath_learning = QtGui.QLineEdit(self.groupBox_4)
        self.filepath_learning.setEnabled(True)
        self.filepath_learning.setReadOnly(True)
        self.filepath_learning.setObjectName(_fromUtf8("filepath_learning"))
        self.horizontalLayout_4.addWidget(self.filepath_learning)
        self.update_learning_with_opened_button = QtGui.QPushButton(self.groupBox_4)
        self.update_learning_with_opened_button.setEnabled(False)
        self.update_learning_with_opened_button.setObjectName(_fromUtf8("update_learning_with_opened_button"))
        self.horizontalLayout_4.addWidget(self.update_learning_with_opened_button)
        self.verticalLayout_2.addWidget(self.groupBox_4)
        self.groupBox_5 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.groupBox_5)
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.filepath_testing = QtGui.QLineEdit(self.groupBox_5)
        self.filepath_testing.setEnabled(True)
        self.filepath_testing.setReadOnly(True)
        self.filepath_testing.setObjectName(_fromUtf8("filepath_testing"))
        self.horizontalLayout_5.addWidget(self.filepath_testing)
        self.update_testing_with_opened_button = QtGui.QPushButton(self.groupBox_5)
        self.update_testing_with_opened_button.setEnabled(False)
        self.update_testing_with_opened_button.setObjectName(_fromUtf8("update_testing_with_opened_button"))
        self.horizontalLayout_5.addWidget(self.update_testing_with_opened_button)
        self.verticalLayout_2.addWidget(self.groupBox_5)
        self.groupBox_6 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.groupBox_6)
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.load_configuration_button = QtGui.QPushButton(self.groupBox_6)
        self.load_configuration_button.setObjectName(_fromUtf8("load_configuration_button"))
        self.horizontalLayout_6.addWidget(self.load_configuration_button)
        self.save_configuration_button = QtGui.QPushButton(self.groupBox_6)
        self.save_configuration_button.setEnabled(False)
        self.save_configuration_button.setObjectName(_fromUtf8("save_configuration_button"))
        self.horizontalLayout_6.addWidget(self.save_configuration_button)
        self.verticalLayout_2.addWidget(self.groupBox_6)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox = QtGui.QGroupBox(InputDataLookupGen)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.groupBox)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.filepath_line_edit = QtGui.QLineEdit(self.groupBox)
        self.filepath_line_edit.setEnabled(True)
        self.filepath_line_edit.setReadOnly(True)
        self.filepath_line_edit.setObjectName(_fromUtf8("filepath_line_edit"))
        self.horizontalLayout_2.addWidget(self.filepath_line_edit)
        self.select_file_button = QtGui.QPushButton(self.groupBox)
        self.select_file_button.setObjectName(_fromUtf8("select_file_button"))
        self.horizontalLayout_2.addWidget(self.select_file_button)
        self.reload_content_button = QtGui.QPushButton(self.groupBox)
        self.reload_content_button.setEnabled(False)
        self.reload_content_button.setObjectName(_fromUtf8("reload_content_button"))
        self.horizontalLayout_2.addWidget(self.reload_content_button)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(InputDataLookupGen)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.scrollArea = QtGui.QScrollArea(self.groupBox_2)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 548, 188))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.sentence_data_widget = QtGui.QTableWidget(self.scrollAreaWidgetContents)
        self.sentence_data_widget.setEnabled(True)
        self.sentence_data_widget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.sentence_data_widget.setObjectName(_fromUtf8("sentence_data_widget"))
        self.sentence_data_widget.setColumnCount(0)
        self.sentence_data_widget.setRowCount(0)
        self.horizontalLayout.addWidget(self.sentence_data_widget)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.addWidget(self.scrollArea)
        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(InputDataLookupGen)
        QtCore.QMetaObject.connectSlotsByName(InputDataLookupGen)

    def retranslateUi(self, InputDataLookupGen):
        InputDataLookupGen.setWindowTitle(_translate("InputDataLookupGen", "Input Data Lookup", None))
        self.groupBox_3.setTitle(_translate("InputDataLookupGen", "Currently selected sets", None))
        self.groupBox_4.setTitle(_translate("InputDataLookupGen", "Learning", None))
        self.filepath_learning.setText(_translate("InputDataLookupGen", "<INVALID>", None))
        self.update_learning_with_opened_button.setText(_translate("InputDataLookupGen", "Set loaded as learning set", None))
        self.groupBox_5.setTitle(_translate("InputDataLookupGen", "Testing", None))
        self.filepath_testing.setText(_translate("InputDataLookupGen", "<INVALID>", None))
        self.update_testing_with_opened_button.setText(_translate("InputDataLookupGen", "Set loaded as testing set", None))
        self.groupBox_6.setTitle(_translate("InputDataLookupGen", "Configuration", None))
        self.load_configuration_button.setText(_translate("InputDataLookupGen", "Load", None))
        self.save_configuration_button.setText(_translate("InputDataLookupGen", "Save", None))
        self.groupBox.setTitle(_translate("InputDataLookupGen", "Select file", None))
        self.filepath_line_edit.setText(_translate("InputDataLookupGen", "<INVALID>", None))
        self.select_file_button.setText(_translate("InputDataLookupGen", "Select Input", None))
        self.reload_content_button.setText(_translate("InputDataLookupGen", "Reload Content", None))
        self.groupBox_2.setTitle(_translate("InputDataLookupGen", "File lookup", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    InputDataLookupGen = QtGui.QWidget()
    ui = Ui_InputDataLookupGen()
    ui.setupUi(InputDataLookupGen)
    InputDataLookupGen.show()
    sys.exit(app.exec_())

