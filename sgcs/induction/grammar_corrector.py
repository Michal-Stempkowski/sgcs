class GrammarCorrector(object):
    def correct_grammar(self, rule_population, cyk_service):
        self.remove_non_productive(rule_population, cyk_service)

    def remove_non_productive(self, rule_population, cyk_service):
        productive_rules = set()
        last_productive_rules = set()

        terminal_rules = list(rule_population.get_terminal_rules())
        symbols = set(map(lambda x: x.parent, terminal_rules))
        productive_rules.update(terminal_rules)

        while len(productive_rules) != len(last_productive_rules):
            last_productive_rules = productive_rules.copy()
            for rule in rule_population.get_all_non_terminal_rules():
                if rule.left_child in symbols and rule.right_child in symbols or \
                   rule_population.universal_symbol is not None and \
                                        rule_population.universal_symbol in symbols:
                    productive_rules.add(rule)
                    symbols.add(rule.parent)

        for rule in rule_population.get_all_non_terminal_rules():
            if rule not in productive_rules:
                rule_population.remove_rule(rule)
                cyk_service.statistics.on_rule_removed(rule)
