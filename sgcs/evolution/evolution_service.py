import copy
from itertools import groupby

from evolution.evolution_operators import InversionOperator, MutationOperator, CrossoverOperator, \
    EvolutionOperator, ParentMutationOperator, LeftChildMutationOperator, RightChildMutationOperator
from evolution.evolution_selectors import RandomSelector, TournamentSelector, RouletteSelector
from rule_adding import AddingRuleStrategyHint


class EvolutionService(object):
    def __init__(self, configuration, randomizer):
        self.randomizer = randomizer
        self.configuration = configuration
        self.selectors = [RandomSelector(), TournamentSelector(), RouletteSelector()]
        self.operators = [InversionOperator(), ParentMutationOperator(),
                          LeftChildMutationOperator(), RightChildMutationOperator(),
                          CrossoverOperator()]

    @staticmethod
    def _chunk(x, size):
        return zip(*[iter(x)]*size)

    def run_genetic_algorithm(self, grammar_statistics, rule_population, rule_adding):
        selector_map = {x.type(): x for x in self.selectors}
        selected_rules = [copy.copy(selector_map[x.type].select(self, grammar_statistics,
                                                                rule_population))
                          for x in self.configuration.selectors]

        rule_adding.update_elite_if_supported(rule_population, grammar_statistics)

        operators_by_arity = groupby(sorted(self.operators, key=EvolutionOperator.arity_keyfunc),
                                     key=EvolutionOperator.arity_keyfunc)

        for arity, operators in operators_by_arity:
            for op in operators:
                new_rules = []
                chunks = self._chunk(selected_rules, arity)
                for arg_list in chunks:
                    new_rules += op.apply(self, rule_population, *arg_list)
                selected_rules = new_rules

        for rule in selected_rules:
            rule_adding.add_rule(rule, rule_population, grammar_statistics, strategy_hint=
                                 AddingRuleStrategyHint.control_population_size_with_elitism)

