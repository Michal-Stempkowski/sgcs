import logging


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
            logging.debug('%s: %s', str(next_production_to_visit.detector.coordinates),
                          str(next_production_to_visit.rule))
            self._visit(next_production_to_visit, cyk_service.statistics,
                        environment.sentence, cyk_result, rules_population)

            traceback_queue += environment.get_child_productions(next_production_to_visit)

    def _visit(self, *args):
        for v in self.visitors:
            v(*args)


class StochasticBestTreeTraceback(Traceback):
    def perform_traceback(self, cyk_service, environment, cyk_result, rules_population):
        traceback_queue = []
        root = environment.get_most_probable_production_for(rules_population.starting_symbol)
        if root is not None:
            traceback_queue.append(root)

        while traceback_queue:
            current_node = traceback_queue.pop()
            if not current_node.rule.is_terminal_rule():
                left_child = environment.get_most_probable_production_for(
                    current_node.rule.left_child,
                    environment._left_coord(*current_node.detector.coordinates))
                if left_child is not None:
                    traceback_queue.append(left_child)

                right_child = environment.get_most_probable_production_for(
                    current_node.rule.right_child,
                    environment._right_coord(*current_node.detector.coordinates))
                if right_child is not None:
                    traceback_queue.append(right_child)

            self._visit(current_node, cyk_service.statistics, environment.sentence, cyk_result,
                        rules_population)
