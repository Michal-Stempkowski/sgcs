import math


class RunEstimator(object):
    def __init__(self):
        self.successes = []
        self.failures = 0

    @property
    def n_success(self):
        return len(self.successes), len(self.successes) + self.failures

    @property
    def n_evals(self):
        return float('nan') if not self.successes \
            else sum(self.successes) / len(self.successes)

    @property
    def s(self):
        if not self.successes:
            return float('nan')
        mean = self.n_evals
        return math.sqrt(sum(map(lambda s: math.pow(s - mean, 2), self.successes)) /
                         len(self.successes))

    @property
    def min_evals(self):
        return min(self.successes, default=float('nan'))

    def append_failure(self):
        self.failures += 1

    def append_success(self, steps):
        self.successes.append(steps)
