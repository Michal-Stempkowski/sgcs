import logging
from PyQt4 import QtCore

from gui.dynamic_gui import DynamicNode
from gui.generated.main__gen import Ui_mainApp
from gui.generic_widget import GenericWidget
from gui.input_data_lookup import InputDataLookup
from gui.options_configurator import OptionsConfigurator
from gui.scheduler import Scheduler
from gui.system_status import SystemStatus


class MainApp(GenericWidget):
    def __init__(self):
        super().__init__(Ui_mainApp)
        self.logger = logging.getLogger(__name__)

        self.windows_container = dict()

        self.ui.inputDataLookupButton.clicked.connect(self.on_input_data_lookup_button_clicked)
        self.ui.optionsConfiguratorButton.clicked.connect(self.on_configuration_button_clicked)
        self.ui.schedulerButton.clicked.connect(self.on_scheduler_button_clicked)
        self.ui.systemStatusButton.clicked.connect(self.on_system_status_button_clicked)

        self.last_directory = ''

        self.dynamic_nodes += [
            DynamicNode(
                self.ui.inputDataLookupButton,
                enabling_condition=self.no_input_data_lookup
            ),
            DynamicNode(
                self.ui.optionsConfiguratorButton,
                enabling_condition=self.no_options_configurator
            ),
            DynamicNode(
                self.ui.schedulerButton,
                enabling_condition=self.no_scheduler
            ),
            DynamicNode(
                self.ui.systemStatusButton,
                enabling_condition=self.no_system_status
            )
        ]

        self.widget.connect(
            self.widget,
            QtCore.SIGNAL(GenericWidget.CLOSING_SIGNAL),
            self._close_existing_windows
        )

    @staticmethod
    def no_input_data_lookup(main_app):
        return InputDataLookup.__name__ not in main_app.windows_container

    @staticmethod
    def no_options_configurator(main_app):
        return OptionsConfigurator.__name__ not in main_app.windows_container

    @staticmethod
    def no_scheduler(main_app):
        return Scheduler.__name__ not in main_app.windows_container

    @staticmethod
    def no_system_status(main_app):
        return SystemStatus.__name__ not in main_app.windows_container

    def on_input_data_lookup_button_clicked(self):
        if self.no_input_data_lookup(self):
            self.logger.debug('Creating input data lookup')
            self._register_and_show(InputDataLookup(self.last_directory))
            self.dynamic_gui_update()

    def on_configuration_button_clicked(self):
        if self.no_options_configurator(self):
            self.logger.debug('Creating options configurator')
            self._register_and_show(OptionsConfigurator(self.last_directory))
            self.dynamic_gui_update()

    def on_scheduler_button_clicked(self):
        if self.no_scheduler(self):
            self.logger.debug('Creating tasks scheduler')
            self._register_and_show(Scheduler())
            self.dynamic_gui_update()

    def on_system_status_button_clicked(self):
        if self.no_system_status(self):
            self.logger.debug('Creating system status')
            self._register_and_show(SystemStatus())
            self.dynamic_gui_update()

    def _register_and_show(self, window):
        window.widget.connect(
            window.widget,
            QtCore.SIGNAL(GenericWidget.CLOSING_SIGNAL),
            self.on_sub_window_closing
        )

        self.windows_container[window.__class__.__name__] = window
        window.show()

    def on_sub_window_closing(self, name):
        self.logger.debug(name + ' was closed')
        del self.windows_container[name]
        self.dynamic_gui_update()

    def _close_existing_windows(self):
        for window in list(self.windows_container.values()):
            window.widget.close()

