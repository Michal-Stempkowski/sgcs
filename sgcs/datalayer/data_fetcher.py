class EagerFileFetcher(object):
    def __init__(self, path):
        self.path = path

    def get_chunk_generator(self):
        with open(self.path) as input_file:
            return input_file.readlines()
