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


class Guard(object):
    def __init__(self, enter_func, exit_func):
        self.enter_func = enter_func
        self.exit_func = exit_func

    def __enter__(self):
        return self.enter_func()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.exit_func(exc_type, exc_val, exc_tb)


class Context(Guard):
    @staticmethod
    def exit_wrapper(exit_func):
        return lambda _1, _2, _3: (exit_func(), False)[1]

    def __init__(self, enter_func, exit_func):
        super().__init__(enter_func, self.exit_wrapper(exit_func))
