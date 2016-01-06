import logging
from abc import abstractmethod

from utils import MethodDecoratorWrapper, Context

NONE_LABEL = '<None>'


class AutoUpdater(object):
    def __init__(self, bind_func, update_model_func, update_gui_func, init_gui_func):
        self.bind = bind_func
        self.init_gui = init_gui_func
        self.update_model = update_model_func
        self.update_gui = update_gui_func


class DynamicNode(object):
    @staticmethod
    def always(_):
        return True

    def __init__(self, *widgets, visibility_condition=None, enabling_condition=None,
                 auto_updater=None):
        self.logger = logging.getLogger(__name__)
        self.widgets = widgets
        self.visibility_condition = visibility_condition if visibility_condition else self.always
        self.enabling_condition = enabling_condition if enabling_condition else self.always
        self.auto_updater = auto_updater

    def update_visibility(self, root):
        for w in self.widgets:
            if self.visibility_condition(root):
                # self.logger.debug('Showing widget: %s', str(w))
                w.show()
            else:
                # self.logger.debug('Hiding widget: %s', str(w))
                w.hide()

    def update_availability(self, root):
        for w in self.widgets:
            if self.enabling_condition(root):
                w.setEnabled(True)
            else:
                w.setEnabled(False)

    def bind(self):
        if self.auto_updater is not None:
            self.auto_updater.bind()

    def init_gui(self):
        if self.auto_updater is not None:
            self.auto_updater.init_gui()

    def update_model(self, root):
        if self.auto_updater is not None and self.visibility_condition(root):
            self.auto_updater.update_model()

    def update_gui(self, root):
        if self.auto_updater is not None and self.visibility_condition(root):
            self.auto_updater.update_gui()


class DynamicRoot(object):
    def __init__(self):
        self.ui = None
        self.dynamic_nodes = []

    def update_dynamic_nodes(self):
        for node in self.dynamic_nodes:
            node.update_visibility(self)
            node.update_availability(self)

    def bind_dn(self):
        for node in self.dynamic_nodes:
            node.bind()

    def init_gui_dn(self):
        for node in self.dynamic_nodes:
            node.init_gui()

    def update_model_dn(self):
        for node in self.dynamic_nodes:
            node.update_model(self)

    def update_dn_gui(self):
        with BlockSignals(*self.ui.__dict__.values()) as _:
            for node in self.dynamic_nodes:
                node.update_gui(self)

    def dynamic_gui_update(self):
        self.update_dynamic_nodes()
        self.update_dn_gui()


def refreshes_dynamics(func):
    class RefreshesDynamicsDecorator(object):
        NO_REFRESH = 'no_refresh'

        def __init__(self, f):
            self.func = f

        def __call__(self, *args, **kwargs):
            refresh_required = not kwargs.get(self.NO_REFRESH, None)
            root, *_ = args
            kwargs.pop(self.NO_REFRESH, None)

            self.func(*args, **kwargs)

            if refresh_required:
                root.update_dynamic_nodes()

        def __get__(self, instance, _):
            return MethodDecoratorWrapper(self, instance)

    return RefreshesDynamicsDecorator(func)


class BlockSignals(Context):
    def _block_signals(self, widgets):
        for w in widgets:
            if w.signalsBlocked():
                self.ignore_exit.add(w)
            else:
                w.blockSignals(True)

        return self

    def _unblock_signals(self, widgets):
        for w in widgets:
            if w not in self.ignore_exit:
                w.blockSignals(False)

    def __init__(self, *widgets):
        self.ignore_exit = set()
        self._w = widgets
        super().__init__(
            lambda: self._block_signals(widgets),
            lambda: self._unblock_signals(widgets))


def feed_with_data(widget, data, default_item=None, clear=False):
    if clear:
        widget.clear()
    if default_item is None:
        items = data
    else:
        items = [default_item]
        items += filter(lambda x: x != default_item, data)
    widget.addItems(items)
    widget.setCurrentIndex(0)
