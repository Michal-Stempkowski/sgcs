import math
from hamcrest import is_, assert_that, close_to


def are_(matcher):
    return is_(matcher)


def assert_nearly_equal_or_both_nan(a, b, delta=0.01):
    if math.isnan(a):
        assert_that(math.isnan(b))
    else:
        assert_that(a, is_(close_to(b, delta)))
