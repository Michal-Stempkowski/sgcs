class DummyWidget(object):
    def setEnabled(self, *args):
        pass


class DummyUi(object):
    def __init__(self, root_dir):
        self.outputDirectorylineEdit = DummyLineEdit(root_dir)


class DummyLineEdit(object):
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def text(self, *args):
        return self.root_dir


class NonGuiScheduler(object):
    def __init__(self, root_dir, tasks):
        self.tasks = tasks
        self.widget = DummyWidget()
        self.ui = DummyUi(root_dir)
