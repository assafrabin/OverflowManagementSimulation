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

    @property
    def success_rate(self):
        return self.completed_weight / self.total_weight


class SimulationsResult:
    COLUMNS = []

    def __init__(self, router_name, n, k, beta, lam, results):
        self.router_name = router_name
        self.n = n
        self.k = k
        self.beta = beta
        self.lam = lam
        self.results = results

    def _average(self, attr_getter):
        return sum([attr_getter(result) for result in self.results]) / float(len(self.results))

    @cached_property
    def average_success_rate(self):
        return self._average(lambda x: x.success_rate)

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
            "average_burst_size": self.average_burst_size,
            "lam": self.lam
        }
