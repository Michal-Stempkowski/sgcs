import os
import unittest
from unittest.mock import create_autospec

from hamcrest import *

from datalayer.data_fetcher import EagerFileFetcher


class TestEagerFileFetcher(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.dir_path = r"C:\Users\Michał\PycharmProjects\mgr\sgcs\sgcs\data\example gramatics"
        self.filename = 'ab los 200 30'

    def test_should_be_able_to_read_file(self):
        # Given:
        sut = EagerFileFetcher(os.path.join(self.dir_path, self.filename))

        # When:
        chunk_generator = sut.get_chunk_generator()

        # Then:
        assert_that(len(chunk_generator), is_(equal_to(201)))
