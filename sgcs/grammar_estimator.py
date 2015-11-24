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
