class Randomizer(object):
    def __init__(self, generator):
        self.generator = generator

    def perform_with_chance(self, chance):
        return False if self.generator.random() > chance else True

    def choice(self, sequence):
        return self.generator.choice(sequence)

    def randint(self, min_val, max_val):
        return self.generator.randint(min_val, max_val)

    def sample(self, sequence, size):
        return self.generator.sample(sequence, size)

    def shuffle(self, sequence):
        return self.generator.shuffle(sequence)
