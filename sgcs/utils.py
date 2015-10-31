class Randomizer(object):
    def __init__(self, generator):
        self.generator = generator

    def perform_with_chance(self, chance):
        return False if self.generator.random() > chance else True

    def choice(self, sequence):
        return self.generator.choice(sequence)
