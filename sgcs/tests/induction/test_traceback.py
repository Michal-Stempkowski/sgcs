import unittest
from unittest.mock import create_autospec, PropertyMock, call
from hamcrest import *


class TestTraceback(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)