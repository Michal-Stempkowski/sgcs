from evolution.evolution_configuration import EvolutionConfiguration
from induction.cyk_configuration import CykConfiguration
from rule_adding import AddingRulesConfiguration


class AlgorithmConfiguration(object):
    @staticmethod
    def default():
        ga_selectors_configuration = []
        evolution_configuration = EvolutionConfiguration.create(
            selectors=ga_selectors_configuration,
            inversion_chance=0,
            mutation_chance=0,
            crossover_chance=0
        )

        induction_configuration = CykConfiguration.create(
            should_correct_grammar=False,
            terminal_chance=0,
            universal_chance=0,
            aggressive_chance=0,
            starting_chance=0,
            full_chance=0
        )

        rule_configuration = RuleConfiguration.create(
            crowding_factor=0,
            crowding_size=0,
            elitism_size=0
        )

        configuration = AlgorithmConfiguration.create(
            induction_configuration, evolution_configuration, rule_configuration)

        return configuration

    @staticmethod
    def create(induction_configuration, evolution_configuration, rule_configuration):
        configuration = AlgorithmConfiguration()
        configuration.induction = induction_configuration
        configuration.evolution = evolution_configuration
        configuration.rule = rule_configuration
        return configuration

    def __init__(self):
        self.induction = None
        self.evolution = None
        self.rule = None


class RuleConfiguration(object):
    @staticmethod
    def create(crowding_factor, crowding_size, elitism_size):
        configuration = RuleConfiguration()
        configuration.adding = AddingRulesConfiguration.create(
            crowding_factor, crowding_size, elitism_size)
        return configuration

    def __init__(self):
        self.adding = None


class GcsRunner(object):
    def __init__(self, configuration):
        self.configuration = configuration
