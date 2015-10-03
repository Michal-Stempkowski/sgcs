import inspect


class Factory(object):
    def __init__(self, impl=None):
        self.impl = impl if impl else dict()

    def create(self, type_id, *args):
        creator = self.impl.get(type_id)

        if not creator:
            caller_frame_record = inspect.stack()[1]
            frame = caller_frame_record[0]
            info = inspect.getframeinfo(frame)

            raise Exception('Invalid type_id: {0} (occurred in {1}, line {2})'.format(
                            type_id, info.filename, info.lineno))

        return creator(*args)
