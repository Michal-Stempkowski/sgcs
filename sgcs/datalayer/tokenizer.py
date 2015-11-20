class EagerTokenizer(object):
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher

    def get_token_generator(self):
        chunk_generator = self.data_fetcher.get_chunk_generator()

        for line in chunk_generator:
            prepared = line.lower().strip().split()
            if any(x for x in prepared):
                yield line.lower().strip().split()
        yield None
