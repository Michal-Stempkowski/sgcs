from abc import ABCMeta, abstractmethod

from core.rule import Rule


class InvalidArityException(Exception):
    def __init__(self, arity):
        self.arity = arity

    def __str__(self):
        return repr(self.arity)


class EvolutionOperator(metaclass=ABCMeta):
    def __init__(self, arity):
        self.arity = arity

    def apply(self, service, *rules):
        if len(rules) != self.arity:
            raise InvalidArityException(len(rules))
        if service.randomizer.perform_with_chance(service.configuration.operators.inversion.chance):
            return self.apply_impl(service, *rules)
        else:
            return rules

    @abstractmethod
    def apply_impl(self, service, *rules):
        pass


class InversionOperator(EvolutionOperator):
    def __init__(self):
        super().__init__(arity=1)

    def apply_impl(self, service, *rules):
        rule, = rules
        return Rule(rule.parent, rule.right_child, rule.left_child),
