import unittest
from unittest.mock import MagicMock, create_autospec
from hamcrest import *
from sgcs.induction.detector import Detector
from sgcs.induction.production import ProductionPool, Production
from sgcs.induction.rule import Rule


class TestProductionPool(unittest.TestCase):
    def test_adding_production_should_result_in_storing_it(self):
        detector = create_autospec(Detector)
        rule = create_autospec(Rule)
        production = Production(detector, rule)
        sut = ProductionPool()

        sut.add_production(production)
        assert_that(sut.pool, only_contains(production))

