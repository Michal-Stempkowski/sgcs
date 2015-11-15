class GrammarCorrector(object):
    def correct_grammar(self, rule_population, cyk_service):
        self.remove_non_productive(rule_population, cyk_service)
        self.remove_not_reachable(rule_population, cyk_service)

    @staticmethod
    def _rule_remover(rule_population, cyk_service, starting_rules, select_predicate,
                      symbol_adder):
        selected_rules = set()
        selected_rules.update(starting_rules)

        while True:
            last_selected_rules = selected_rules.copy()
            for rule in rule_population.get_all_non_terminal_rules():
                if select_predicate(rule):
                    selected_rules.add(rule)
                    symbol_adder(rule)

            if len(selected_rules) == len(last_selected_rules):
                break

        for rule in rule_population.get_all_non_terminal_rules():
            if rule not in selected_rules:
                rule_population.remove_rule(rule)
                cyk_service.statistics.on_rule_removed(rule)

    def remove_non_productive(self, rule_population, cyk_service):
        starting_rules = list(rule_population.get_terminal_rules())
        symbols = set(map(lambda x: x.parent, starting_rules))
        select_predicate = lambda rule: \
            rule.left_child in symbols and rule.right_child in symbols or \
            rule_population.universal_symbol is not None and \
            rule_population.universal_symbol in symbols
        symbol_adder = lambda rule: symbols.add(rule.parent)

        self._rule_remover(rule_population, cyk_service, starting_rules, select_predicate,
                           symbol_adder)

    def remove_not_reachable(self, rule_population, cyk_service):
        starting_rules = list()
        symbols = {rule_population.starting_symbol}
        select_predicate = lambda rule: rule.parent in symbols
        symbol_adder = lambda rule: (symbols.add(rule.left_child), symbols.add(rule.right_child))

        self._rule_remover(rule_population, cyk_service, starting_rules, select_predicate,
                           symbol_adder)
