from abc import ABCMeta, abstractmethod


class RuleInfo(object):
    def __init__(self):
        self.rule_usage = 0


class LeftSideInfo(object):
    def __init__(self):
        self.left_side_usage = 0


class RuleStatistics(object):
    def __init__(self):
        self._rule_info = dict()
        self._left_side_info = dict()

    def get_rule_statistics(self, rule):
        return (self._rule_info[rule], self._left_side_info.get(rule.parent)) \
            if rule in self._rule_info else None

    def added_new_rule(self, rule):
        info = self._left_side_info.get(rule.parent, LeftSideInfo())
        self._left_side_info[rule.parent] = info

        self._rule_info[rule] = RuleInfo()

    def rule_used(self, rule):
        self._left_side_info[rule.parent].left_side_usage += 1
        self._rule_info[rule].rule_usage += 1


class DummyCykStatistics(object):
    def get_rule_statistics(self, rule):
        return None

    def on_added_new_rule(self, rule):
        pass

    def on_rule_usage(self, rule):
        pass


class CykStatistics(DummyCykStatistics):
    def __init__(self, rule_statistics):
        self.rule_statistics = rule_statistics

    def get_rule_statistics(self, rule):
        return self.rule_statistics.get_rule_statistics(rule)

    def on_added_new_rule(self, rule):
        self.rule_statistics.added_new_rule(rule)

    def on_rule_usage(self, rule):
        self.rule_statistics.rule_used(rule)


class PasiekaFitness(object):
    def calculate(self, cyk_service, rule):
        rule_info, _ = cyk_service.statistics.get_rule_statistics(rule)
        return rule_info.rule_usage
