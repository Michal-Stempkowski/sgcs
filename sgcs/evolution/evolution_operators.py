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

    @staticmethod
    def arity_keyfunc(operator):
        return operator.arity

    def apply(self, service, rule_population, *rules):
        if len(rules) != self.arity:
            raise InvalidArityException(len(rules))
        elif service.randomizer.perform_with_chance(self.get_execution_chance(service)):
            return self.apply_impl(service, rule_population, *rules)
        else:
            return rules

    @abstractmethod
    def apply_impl(self, service, rule_population, *rules):
        pass

    @abstractmethod
    def get_execution_chance(self, service):
        pass


class InversionOperator(EvolutionOperator):
    def get_execution_chance(self, service):
        return service.configuration.operators.inversion.chance

    def __init__(self):
        super().__init__(arity=1)

    def apply_impl(self, service, rule_population, *rules):
        rule, = rules
        return Rule(rule.parent, rule.right_child, rule.left_child),


# noinspection PyAbstractClass
class MutationOperator(EvolutionOperator):
    def get_execution_chance(self, service):
        return service.configuration.operators.mutation.chance

    def __init__(self):
        super().__init__(arity=1)


# noinspection PyAbstractClass
class ParentMutationOperator(MutationOperator):
    def apply_impl(self, service, rule_population, *rules):
        rule, = rules
        parent = rule_population.get_random_non_terminal_symbol(service.randomizer) \
            if service.randomizer.perform_with_chance(self.get_execution_chance(service)) \
            else rule.parent
        return Rule(parent, rule.left_child, rule.right_child),


# noinspection PyAbstractClass
class LeftChildMutationOperator(MutationOperator):
    def apply_impl(self, service, rule_population, *rules):
        rule, = rules
        left_child = rule_population.get_random_non_terminal_symbol(service.randomizer) \
            if service.randomizer.perform_with_chance(self.get_execution_chance(service)) \
            else rule.left_child
        return Rule(rule.parent, left_child, rule.right_child),


# noinspection PyAbstractClass
class RightChildMutationOperator(MutationOperator):
    def apply_impl(self, service, rule_population, *rules):
        rule, = rules
        right_child = rule_population.get_random_non_terminal_symbol(service.randomizer) \
            if service.randomizer.perform_with_chance(self.get_execution_chance(service)) \
            else rule.right_child
        return Rule(rule.parent, rule.left_child, right_child),


class CrossoverOperator(EvolutionOperator):
    def get_execution_chance(self, service):
        return service.configuration.operators.crossover.chance

    def __init__(self):
        super().__init__(arity=2)

    def apply_impl(self, service, rule_population, *rules):
        rule_1, rule_2 = rules
        if service.randomizer.perform_with_chance(0.5):
            rule_1, rule_2 = Rule(rule_1.parent, rule_2.left_child, rule_1.right_child), \
                             Rule(rule_2.parent, rule_1.left_child, rule_2.right_child)
        else:
            rule_1, rule_2 = Rule(rule_1.parent, rule_1.left_child, rule_2.right_child), \
                             Rule(rule_2.parent, rule_2.left_child, rule_1.right_child)

        return Rule(rule_2.parent, rule_1.left_child, rule_1.right_child), \
            Rule(rule_1.parent, rule_2.left_child, rule_2.right_child)
