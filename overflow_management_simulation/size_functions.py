import random


class SizeFunc:
    def __call__(self, *args, **kwargs):
        pass


class NoSizes(SizeFunc):
    def __call__(self, *args, **kwargs):
        return 1


class RandomSizes(SizeFunc):
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, *args, **kwargs):
        return random.randint(0, self.max_size)


class SomeLargeSizes(SizeFunc):
    def __init__(self, large_count, large_size):
        self.large_count = large_count
        self.large_size = large_size

    def __call__(self, *args, **kwargs):
        return self.large_size if kwargs['superpacket_id'] < self.large_count else 1
