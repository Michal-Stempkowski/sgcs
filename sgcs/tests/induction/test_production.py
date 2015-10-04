import unittest
from unittest.mock import MagicMock, create_autospec, PropertyMock
from hamcrest import *
from sgcs.induction.detector import Detector
from sgcs.induction.production import ProductionPool, Production
from sgcs.induction.rule import Rule


class TestProductionPool(unittest.TestCase):
    def test_adding_production_should_result_in_storing_it(self):
        detector = create_autospec(Detector)
        rule = create_autospec(Rule)
        type(rule).parent = PropertyMock(return_value='A')
        production = Production(detector, rule)
        sut = ProductionPool()

        sut.add_production(production)
        assert_that(sut.non_empty_productions, only_contains(production))

