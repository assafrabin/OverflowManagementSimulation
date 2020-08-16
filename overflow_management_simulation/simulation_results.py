import pandas as pd

from typing import List

from cached_property import cached_property

from overflow_management_simulation.superpacket import Superpacket


class SimulationResult:
    def __init__(self, simulation, superpackets: List[Superpacket], completed_superpackets: List[Superpacket]):
        self.simulation = simulation
        self.superpackets = superpackets
        self.completed_superpackets = completed_superpackets

    @property
    def max_time(self):
        return max(sp.max_time for sp in self.superpackets)

    @property
    def total_weight(self) -> int:
        return sum(sp.weight for sp in self.superpackets)

    @property
    def completed_weight(self):
        return sum(sp.weight for sp in self.completed_superpackets)

    @cached_property
    def completed_upper_bound(self):
        return min((self.simulation.T * self.simulation.capacity) / ((1 - self.simulation.beta) * self.simulation.k),
                   len(self.superpackets))

    @property
    def success_rate(self):
        if self.simulation.weighted:
            return self.completed_weight / self.total_weight
        else:
            return len(self.completed_superpackets) / self.completed_upper_bound


class SimulationsResult:
    def __init__(self, router_name, k, beta, lam, capacity, buffer_size, results):
        self.router_name = router_name
        self.k = k
        self.beta = beta
        self.lam = lam
        self.capacity = capacity
        self.buffer_size = buffer_size
        self.results = results


    def _average(self, attr_getter):
        return sum([attr_getter(result) for result in self.results]) / len(self.results)

    @cached_property
    def average_success_rate(self):
        return self._average(lambda x: x.success_rate)

    @cached_property
    def average_n(self):
        return self._average(lambda x: len(x.superpackets))

    @cached_property
    def average_completed_superpackets(self):
        return self._average(lambda x: len(x.completed_superpackets))

    @cached_property
    def average_burst_size(self):
        return self._average(lambda x: x.simulation.average_burst_size)

    def print(self):
        print(f'{self.router_name} - {self.beta} - {self.average_success_rate:.2f}')

    def to_dict(self):
        return {
            "router": self.router_name,
            "beta": self.beta,
            "success_rate": self.average_success_rate,
            "completed_superpackets": self.average_completed_superpackets,
            "average_burst_size": self.average_burst_size,
            "average_effective_load": self.average_burst_size * (1 - self.beta),
            "lam": self.lam,
            "k": self.k,
            "capacity": self.capacity,
            "buffer_size": self.buffer_size,
        }
