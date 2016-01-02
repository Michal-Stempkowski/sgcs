from PyQt4 import QtGui

from gui.dynamic_gui import AutoUpdater


class MainBoxAutoUpdater(AutoUpdater):
    def __init__(self, options_configurator):
        super().__init__(
            lambda: self._bind(options_configurator),
            lambda: self._update_model(options_configurator),
            lambda: self._update_gui(options_configurator),
            lambda: self._init_gui(options_configurator)
        )

    @staticmethod
    def _init_gui(options_configurator):
        pass

    def _bind(self, options_configurator):
        options_configurator.ui.buttonBox.button(QtGui.QDialogButtonBox.Reset).clicked.connect(
            lambda: self.on_reset_clicked(options_configurator))

    @staticmethod
    def on_reset_clicked(options_configurator):
        options_configurator.on_variant_changed(options_configurator.current_variant.name)

    @staticmethod
    def _update_model(options_configurator):
        pass

    @staticmethod
    def _update_gui(options_configurator):
        pass
