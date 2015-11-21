class EagerTokenizer(object):
    def __init__(self, data_fetcher):
        self.data_fetcher = data_fetcher

    def get_token_generator(self):
        chunk_generator = self.data_fetcher.get_chunk_generator()

        next(chunk_generator)
        for line in chunk_generator:
            prepared = line.lower().strip().split()
            if any(x for x in prepared):
                prepared[0] = True if prepared[0] == '1' else False if prepared[0] == '0' else None
                del prepared[1]
                yield prepared
