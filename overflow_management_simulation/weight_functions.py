import random


class WeightFunc:
    def __call__(self, *args, **kwargs):
        pass


class NoWeights(WeightFunc):
    def __call__(self, *args, **kwargs):
        return 1


class RandomWeights(WeightFunc):
    def __init__(self, max_weight):
        self.max_weight = max_weight

    def __call__(self, *args, **kwargs):
        return random.randint(0, self.max_weight)


class SomeHeavyWeights(WeightFunc):
    def __init__(self, heavy_count, heavy_weight):
        self.heavy_count = heavy_count
        self.heavy_weight = heavy_weight

    def __call__(self, *args, **kwargs):
        return self.heavy_weight if kwargs['superpacket_id'] < self.heavy_count else 1
