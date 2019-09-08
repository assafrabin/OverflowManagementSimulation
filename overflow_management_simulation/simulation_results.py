from typing import List

from overflow_management_simulation.superpacket import Superpacket


class SimulationResult:
    def __init__(self, superpackets: List[Superpacket]):
        self.superpackets = superpackets

    @property
    def max_time(self):
        return max(sp.max_time for sp in self.superpackets)

    @property
    def completed_superpackets(self):
        return [sp for sp in self.superpackets if sp.is_completed]

    @property
    def total_weight(self) -> int:
        return sum(sp.weight for sp in self.superpackets)

    @property
    def completed_weight(self):
        return sum(sp.weight for sp in self.completed_superpackets)

    @property
    def success_rate(self):
        return self.completed_weight / self.total_weight


class SimulationResults:
    def __init__(self, router, n, k, beta, lam, results):
        self.router = router
        self.n = n
        self.k = k
        self.beta = beta
        self.lam = lam
        self.results = results

    def _average(self, attr):
        return sum([getattr(result, attr) for result in self.results]) / float(len(self.results))

    @property
    def average_packets_per_slot(self):
        return self._average('packets_per_slot')

    @property
    def average_success_rate(self):
        return self._average('success_rate')

    def print(self):
        print(f'{self.router.NAME} - {self.beta} - {self.average_success_rate:.2f}')


