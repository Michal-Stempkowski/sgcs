class Traceback(object):
    def __init__(self, visitors):
        self.visitors = visitors

    def perform_traceback(self, cyk_service, environment, cyk_result, rules_population):
        traceback_queue = []
        traceback_queue += filter(lambda x: x.rule.parent == rules_population.starting_symbol,
                                  environment.get_last_cell_productions())
        # __traceback_queue_len = len(traceback_queue)
        while traceback_queue:
            next_production_to_visit = traceback_queue.pop(0)
            self._visit(next_production_to_visit, cyk_service.statistics,
                        environment.sentence, cyk_result, rules_population)
            traceback_queue += environment.get_child_productions(next_production_to_visit)
            # __traceback_queue_len = max(__traceback_queue_len, len(traceback_queue))

        # print('traceback_len:', __traceback_queue_len)

    def _visit(self, *args):
        for v in self.visitors:
            v(*args)
