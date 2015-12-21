import itertools


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

    def uniform(self, min_val, max_val):
        return self.generator.uniform(min_val, max_val)


class RunTimes(object):
    def __init__(self, times):
        self.times = times

    def __call__(self, *args, **kwargs):
        result = self.times > 0
        self.times -= 1
        return result


def chunk(x, size):
    return itertools.zip_longest(fillvalue=None, *([iter(x)] * size))


class MethodDecoratorWrapper(object):
    def __init__(self, desc, subj):
        self.desc = desc
        self.subj = subj

    def __call__(self, *args, **kwargs):
        return self.desc(self.subj, *args, **kwargs)
