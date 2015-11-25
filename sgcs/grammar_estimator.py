import math


class EvolutionStepEstimator(object):
    def __init__(self):
        self._true_positive = 0
        self._true_negative = 0
        self._false_positive = 0
        self._false_negative = 0

    @property
    def true_positive(self):
        return self._true_positive

    @property
    def true_negative(self):
        return self._true_negative

    @property
    def false_positive(self):
        return self._false_positive

    @property
    def false_negative(self):
        return self._false_negative

    @property
    def total(self):
        return self.positives_that_has_occurred + self.negatives_that_has_occurred

    @property
    def positives_that_has_occurred(self):
        return self.true_positive + self.false_negative

    @property
    def negatives_that_has_occurred(self):
        return self.true_negative + self.false_positive

    @property
    def parsed_correctly(self):
        return self.true_positive + self.true_negative

    @property
    def fitness(self):
        return self.parsed_correctly / self.total if self.total else float('nan')

    def append_result(self, cyk_result):
        if cyk_result.is_positive:
            if cyk_result.belongs_to_grammar:
                self._true_positive += 1
            else:
                self._false_negative += 1
        else:
            if cyk_result.belongs_to_grammar:
                self._false_positive += 1
            else:
                self._true_negative += 1


class GrammarEstimator(object):
    def __init__(self):
        self._fitness = dict()
        self._positive = dict()
        self._negative = dict()

    @staticmethod
    def nan_safe_min(a, b):
        return min(a, b) if not math.isnan(a) else b

    @staticmethod
    def nan_safe_max(a, b):
        return max(a, b) if not math.isnan(a) else b

    def _add_and_pack(self, a, b):
        accum, count, min_val, max_val = a
        new_val, delta = b
        new_acum = accum + new_val
        new_count = count + delta
        return new_acum, new_count,\
            self.nan_safe_min(min_val, new_acum / new_count),\
            self.nan_safe_max(max_val, new_acum / new_count)

    def append_step_estimation(self, step, estimation):
        self._update_fitness(step, estimation)
        self._update_positive(step, estimation)
        self._update_negative(step, estimation)

    def _generic_update(self, estimation, step, collection, data_guard, calculate_function):
        data = collection.get(step, (0, 0, float('nan'), float('nan')))
        if data_guard(estimation):
            val = calculate_function(estimation)

            collection[step] = self._add_and_pack(data, (val, 1))

    def _update_fitness(self, step, estimation):
        self._generic_update(estimation,
                             step,
                             self._fitness,
                             lambda _: True,
                             lambda est: est.fitness)

    def _update_positive(self, step, estimation):
        self._generic_update(estimation,
                             step,
                             self._positive,
                             lambda est: estimation.positives_that_has_occurred != 0,
                             lambda est: est.true_positive / est.positives_that_has_occurred)

    def _update_negative(self, step, estimation):
        self._generic_update(estimation,
                             step,
                             self._negative,
                             lambda est: estimation.negatives_that_has_occurred != 0,
                             lambda est: est.false_positive / est.negatives_that_has_occurred)

    @staticmethod
    def _generic_get(step, collection):
        data = collection.get(step)
        return data[0] / data[1] if data else float('nan')

    @staticmethod
    def _generic_get_special_val(step, collection, col):
        data = collection.get(step)
        return data[col] if data else float('nan')

    def get_fitness(self, step):
        return self._generic_get(step, self._fitness)

    def get_positive(self, step):
        return self._generic_get(step, self._positive)

    def get_negative(self, step):
        return self._generic_get(step, self._negative)

    def get_min_fitness(self, step):
        return self._generic_get_special_val(step, self._fitness, 2)

    def get_max_fitness(self, step):
        return self._generic_get_special_val(step, self._fitness, 3)

    def get_min_positive(self, step):
        return self._generic_get_special_val(step, self._positive, 2)

    def get_max_positive(self, step):
        return self._generic_get_special_val(step, self._positive, 3)
