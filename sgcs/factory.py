import inspect


class Factory(object):
    def __init__(self, implementation=None):
        self.implementation = implementation if implementation else dict()

    def create(self, type_id, *args):
        creator = self.implementation.get(type_id)

        if not creator:
            caller_frame_record = inspect.stack()[1]
            frame = caller_frame_record[0]
            info = inspect.getframeinfo(frame)

            raise Exception('Invalid type_id: {0} (occurred in {1}, line {2})'.format(
                            type_id, info.filename, info.lineno))

        return creator(*args)
