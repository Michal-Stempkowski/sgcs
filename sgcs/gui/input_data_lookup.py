import json
import os

from PyQt4 import QtGui, QtCore

import utils
from datalayer.symbol_translator import SymbolTranslator
from executors.simulation_executor import SimulationExecutor
from gui.async_progress_dialog import AsyncProgressDialog
from gui.generated.input_data_lookup__gen import Ui_InputDataLookupGen
from gui.generic_widget import GenericWidget


class Header(object):
    def __init__(self, name, handle_row_fun):
        self.name = name
        self._handle_row_fun = handle_row_fun

    def handle_cell(self, row_data, cell_id):
        return self._handle_row_fun(self, row_data, cell_id)

    def __getattr__(self, _):
        return None


class LoadInputWorker(QtCore.QThread):
    MIN_CHUNK_SIZE = 500
    MAX_CHUNK_NUM = 100

    def __init__(self, employer):
        super().__init__(employer.widget)
        self.employer = employer

    def _load_sentences(self):
        self.emit(QtCore.SIGNAL(AsyncProgressDialog.CHANGE_STEP_EVENT), 'Opening file...')
        self.employer.symbol_translator = SymbolTranslator.create(
            self.employer.selected_filename)
        return list(self.employer.symbol_translator.get_sentences())

    def _set_table_size(self, sentences):
        max_sentence_length = max(map(len, sentences))
        self.employer.ui.sentence_data_widget.setRowCount(len(sentences))
        return max_sentence_length

    def _prepare_headers(self, max_sentence_length):
        headers = [
            Header('is positive', self._handle_sentence_is_positive)
        ]

        static_headers_len = len(headers)

        headers += (Header('#{0}'.format(i),
                           self._make_handle_sentence_sentence_symbol(static_headers_len))
                    for i in range(max_sentence_length))

        self.emit(QtCore.SIGNAL(InputDataLookup.HEADERS_LOADED_EVENT), headers)

        return headers

    def _make_handle_sentence_sentence_symbol(self, static_headers_len):
        return lambda _, rd, col: self._handle_sentence_sentence_symbol(rd, col, static_headers_len)

    def _handle_sentence_sentence_symbol(self, sentence, col, static_headers_len):
        word_num = col - static_headers_len

        return self.employer.symbol_translator.symbol_to_word(sentence.get_symbol(word_num)) \
            if word_num < len(sentence) else ''

    @staticmethod
    def _handle_sentence_sentence_id(header, _, _2):
        header.sentence_no = header.sentence_no + 1 if header.sentence_no is not None else 0
        return str(header.sentence_no)

    @staticmethod
    def _handle_sentence_is_positive(_, row_data, _2):
        return 'P' if row_data.is_positive_sentence else 'N'

    def _fill_table(self, sentences, headers, max_sentence_length):
        total = len(sentences)
        chunk_size = max(total // self.MAX_CHUNK_NUM, self.MIN_CHUNK_SIZE)
        for chunk_id, chunk in enumerate(utils.chunk(sentences, chunk_size)):
            shift = chunk_id * chunk_size
            self.emit(QtCore.SIGNAL(InputDataLookup.SENTENCES_LOADED_EVENT), chunk, shift, total)

    def run(self):
        sentences = self._load_sentences()
        max_sentence_length = self._set_table_size(sentences)
        headers = self._prepare_headers(max_sentence_length)

        self.emit(QtCore.SIGNAL(AsyncProgressDialog.CHANGE_STEP_EVENT), 'Filling table...')
        self._fill_table(sentences, headers, max_sentence_length)


class InputDataLookup(GenericWidget):
    NO_FILENAME_TAG = '<no filename selected>'

    HEADERS_LOADED_EVENT = 'InputDataLookup.headers_loaded'
    SENTENCES_LOADED_EVENT = 'InputDataLookup.sentence_loaded'
    DATA_CONFIG_EXT = '*.inconf'

    def __init__(self, last_directory):
        super().__init__(Ui_InputDataLookupGen)
        self.last_directory = last_directory
        self._selected_filename = None
        self._selected_learning_filename = None
        self._selected_testing_filename = None
        self.symbol_translator = None
        self.headers = None

        self._bind_gui()
        self._bind_logic()

        self.worker = LoadInputWorker(self)
        self.async_progress_dialog = AsyncProgressDialog(self, self.worker)
        self.async_progress_dialog.make_lean()

        self.widget.connect(
            self.worker, QtCore.SIGNAL(self.HEADERS_LOADED_EVENT), self._handle_headers_loaded)
        self.widget.connect(
            self.worker, QtCore.SIGNAL(self.SENTENCES_LOADED_EVENT), self._handle_sentence_loaded)

    def _bind_gui(self):
        self.selected_filename = None
        self.selected_learning_filename = None
        self.selected_testing_filename = None

    def _bind_logic(self):
        self.ui.select_file_button.clicked.connect(self.select_input_action)
        self.ui.reload_content_button.clicked.connect(self.load_file_action)
        self.ui.update_learning_with_opened_button.clicked.connect(self.select_learning_set_action)
        self.ui.update_testing_with_opened_button.clicked.connect(self.select_testing_set_action)
        self.ui.save_configuration_button.clicked.connect(self.save_config_action)
        self.ui.load_configuration_button.clicked.connect(self.load_config_action)

    @property
    def selected_filename(self):
        return self._selected_filename

    @selected_filename.setter
    def selected_filename(self, val):
        self._selected_filename = val
        self.ui.filepath_line_edit.setText(self._selected_filename if self._selected_filename
                                           else InputDataLookup.NO_FILENAME_TAG)

    @property
    def selected_learning_filename(self):
        return self._selected_learning_filename

    @selected_learning_filename.setter
    def selected_learning_filename(self, val):
        self._selected_learning_filename = val
        self.ui.filepath_learning.setText(
            self._selected_learning_filename if self._selected_learning_filename
            else InputDataLookup.NO_FILENAME_TAG)
        self._update_saving_status()

    @property
    def selected_testing_filename(self):
        return self._selected_testing_filename

    @selected_testing_filename.setter
    def selected_testing_filename(self, val):
        self._selected_testing_filename = val
        self.ui.filepath_testing.setText(
            self._selected_testing_filename if self._selected_testing_filename
            else InputDataLookup.NO_FILENAME_TAG)
        self._update_saving_status()

    def _update_saving_status(self):
        status = all([self.selected_learning_filename, self.selected_testing_filename])
        self.ui.save_configuration_button.setEnabled(status)

    def _handle_headers_loaded(self, headers):
        self.headers = headers
        self.ui.sentence_data_widget.setColumnCount(len(self.headers))
        self.ui.sentence_data_widget.setHorizontalHeaderLabels(
            list(map(lambda x: x.name, self.headers)))

    def _handle_sentence_loaded(self, sentences, shift, total):
        for row, sentence in enumerate(sentences):
            if sentence is not None:
                for col, header in enumerate(self.headers):
                    content = header.handle_cell(sentence, col)
                    self.ui.sentence_data_widget.setItem(shift + row, col, QtGui.QTableWidgetItem(content))

                    if self.async_progress_dialog.dialog.maximum() != total:
                        self.async_progress_dialog.dialog.setMaximum(total)

        new_value = min(self.async_progress_dialog.dialog.value() + len(sentences), total)
        self.async_progress_dialog.dialog.setValue(new_value)
        if new_value == total:
            self.async_progress_dialog.dialog.close()
            self.ui.reload_content_button.setEnabled(True)
            self.ui.update_learning_with_opened_button.setEnabled(True)
            self.ui.update_testing_with_opened_button.setEnabled(True)

    def select_input_action(self):
        # noinspection PyTypeChecker,PyCallByClass
        selected_filename = QtGui.QFileDialog.getOpenFileName(
            self.widget, 'Select input file...', self.last_directory)
        if selected_filename:
            self.selected_filename = selected_filename
            # noinspection PyTypeChecker
            self.last_directory = os.path.dirname(self.selected_filename)

            self.load_file_action()

    def load_file_action(self):
        self.worker.start()
        self.async_progress_dialog.show()

    def select_learning_set_action(self):
        self.selected_learning_filename = self.selected_filename

    def select_testing_set_action(self):
        self.selected_testing_filename = self.selected_filename

    def save_config_action(self):
        config = dict(
            learning=self.selected_learning_filename,
            testing=self.selected_testing_filename
        )
        serialized = json.dumps(config)

        selected_filename = QtGui.QFileDialog.getSaveFileName(
            self.widget, 'Save config...', self.last_directory, self.DATA_CONFIG_EXT)
        if selected_filename:
            with open(selected_filename, 'w+') as file:
                file.write(serialized)

    def load_config_action(self):
        selected_filename = QtGui.QFileDialog.getOpenFileName(
            self.widget, 'Load config...', self.last_directory, self.DATA_CONFIG_EXT)
        if selected_filename:
            self.selected_learning_filename, self.selected_testing_filename = \
                SimulationExecutor.load_input_config(selected_filename)

