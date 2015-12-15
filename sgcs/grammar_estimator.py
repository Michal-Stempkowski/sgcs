import math
from abc import ABCMeta, abstractmethod


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


class GrammarCriteria(metaclass=ABCMeta):
    @staticmethod
    def nan_safe_min(a, b):
        return min(a, b) if not math.isnan(a) else b

    @staticmethod
    def nan_safe_max(a, b):
        return max(a, b) if not math.isnan(a) else b

    @staticmethod
    def nan_safe_ladd(a, b):
        return a + b if not math.isnan(a) else b

    @staticmethod
    def nan_safe_rsub(a, b):
        return a - b if not math.isnan(b) else a

    def __init__(self):
        self._occurrences = dict()
        self._global_min = float('nan')
        self._global_max = float('nan')
        self._global_average = float('nan')

    def update(self, step, estimation):
        data = self._occurrences.get(step, (0, 0, float('nan'), float('nan')))
        if self._data_guard(estimation):
            val = self._calculate(estimation)

            self._occurrences[step] = self._add_and_pack(data, (val, 1))

    @abstractmethod
    def _data_guard(self, estimation):
        pass

    @abstractmethod
    def _calculate(self, estimation):
        pass

    def _add_and_pack(self, a, b):
        accum, count, min_val, max_val = a
        new_val, delta = b
        new_acum = accum + new_val
        new_count = count + delta
        old_attrib = accum / count if count else float('nan')
        current_attrib = new_acum / new_count

        step_min = self.nan_safe_min(min_val, current_attrib)
        step_max = self.nan_safe_max(max_val, current_attrib)

        self._global_average = self.nan_safe_rsub(
            self.nan_safe_ladd(self._global_average, current_attrib), old_attrib)

        self._global_min = self.nan_safe_min(self._global_min, step_min)

        self._global_max = self.nan_safe_max(self._global_max, step_max)

        return new_acum, new_count, step_min, step_max

    def get(self, step):
        data = self._occurrences.get(step)
        return data[0] / data[1] if data else float('nan')

    def get_min(self, step):
        data = self._occurrences.get(step)
        return data[2] if data else float('nan')

    def get_max(self, step):
        data = self._occurrences.get(step)
        return data[3] if data else float('nan')

    def get_global_average(self):
        return self._global_average / len(self._occurrences) \
            if len(self._occurrences) else float('nan')

    def get_global_min(self):
        return self._global_min

    def get_global_max(self):
        return self._global_max


class FitnessGrammarCriteria(GrammarCriteria):
    def _calculate(self, estimation):
        return estimation.fitness

    def _data_guard(self, estimation):
        return True


class PositiveGrammarCriteria(GrammarCriteria):
    def _calculate(self, estimation):
        return estimation.true_positive / estimation.positives_that_has_occurred

    def _data_guard(self, estimation):
        return estimation.positives_that_has_occurred != 0


class NegativeGrammarCriteria(GrammarCriteria):
    def _calculate(self, estimation):
        return estimation.false_positive / estimation.negatives_that_has_occurred

    def _data_guard(self, estimation):
        return estimation.negatives_that_has_occurred != 0


class SensitivityGrammarCriteria(GrammarCriteria):
    def _calculate(self, estimation):
        return estimation.true_negative / estimation.positives_that_has_occurred

    def _data_guard(self, estimation):
        return estimation.positives_that_has_occurred != 0


class SpecifityGrammarCriteria(GrammarCriteria):
    def _calculate(self, estimation):
        return estimation.true_negative / estimation.negatives_that_has_occurred

    def _data_guard(self, estimation):
        return estimation.negatives_that_has_occurred != 0


class AccuracyGrammarCriteria(GrammarCriteria):
    def _calculate(self, estimation):
        return estimation.parsed_correctly / estimation.total

    def _data_guard(self, estimation):
        return estimation.total != 0


class GrammarEstimator(object):
    def __init__(self):
        self.criterias = dict(
            fitness=FitnessGrammarCriteria(),
            positive=PositiveGrammarCriteria(),
            negative=NegativeGrammarCriteria(),
            sensivity=SensitivityGrammarCriteria(),
            specifity=SpecifityGrammarCriteria(),
            accuracy=AccuracyGrammarCriteria()
        )

    def __getitem__(self, item):
        return self.criterias[item]

    def append_step_estimation(self, step, estimation):
        any(criteria.update(step, estimation) for criteria in self.criterias.values())
