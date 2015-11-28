class Traceback(object):
    def __init__(self, visitors):
        self.visitors = visitors

    def perform_traceback(self, cyk_service, environment, cyk_result, rules_population):
        traceback_queue = []
        rules_used = set()
        traceback_queue += filter(lambda x: x.rule.parent == rules_population.starting_symbol,
                                  environment.get_last_cell_productions())

        while traceback_queue:
            next_production_to_visit = traceback_queue.pop()
            if next_production_to_visit.rule in rules_used:
                continue
            rules_used.add(next_production_to_visit.rule)
            self._visit(next_production_to_visit, cyk_service.statistics,
                        environment.sentence, cyk_result, rules_population)

            traceback_queue += environment.get_child_productions(next_production_to_visit)

    def _visit(self, *args):
        for v in self.visitors:
            v(*args)


class ThoroughTraceback(object):
    def __init__(self, visitors):
        self.visitors = visitors

    def perform_traceback(self, cyk_service, environment, cyk_result, rules_population):
        traceback_queue = []
        traceback_queue += filter(lambda x: x.rule.parent == rules_population.starting_symbol,
                                  environment.get_last_cell_productions())

        while traceback_queue:
            next_production_to_visit = traceback_queue.pop()
            self._visit(next_production_to_visit, cyk_service.statistics,
                        environment.sentence, cyk_result, rules_population)

            traceback_queue += environment.get_child_productions(next_production_to_visit)

    def _visit(self, *args):
        for v in self.visitors:
            v(*args)
