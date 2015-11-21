class EagerFileFetcher(object):
    def __init__(self, path):
        self.path = path

    def get_chunk_generator(self):
        with open(self.path) as input_file:
            return iter(input_file.readlines())


class LazyFileFetcher(object):
    def __init__(self, path):
        self.path = path

    def get_chunk_generator(self):
        with open(self.path) as input_file:
            for line in input_file:
                yield line
