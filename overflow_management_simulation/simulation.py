import numpy as np

from overflow_management_simulation.simulation_results import SimulationResults, SimulationResult
from overflow_management_simulation.superpacket import Superpacket


class Simulation:
    def __init__(self, router, n, k, beta, lam, number_of_repeats):
        self.router = router
        self.n = n
        self.k = k
        self.beta = beta
        self.lam = lam
        self.number_of_repeats = number_of_repeats

    def run(self):
        return SimulationResults(router=self.router, n=self.n, k=self.k, beta=self.beta, lam=self.lam,
                                 results=[self.single_run() for _ in range(self.number_of_repeats)])

    def single_run(self):
        superpackets = [Superpacket(id_=i, number_of_packets=self.k, beta=self.beta) for i in range(self.n)]

        for sp in superpackets:
            self.set_arrival_times(packets=sp.packets, lam=self.lam)

        max_time = max(sp.max_time for sp in superpackets)

        for t in range(max_time):
            participating_packets = [p for sp in superpackets for p in sp.packets if p.arrival_time == t]
            transmitted_packets = self.router.route(participating_packets)
            for p in transmitted_packets:
                p.is_transmitted = True

        return SimulationResult(superpackets)

    @staticmethod
    def set_arrival_times(packets, lam):
        arrival_intervals = np.random.poisson(lam, size=len(packets))
        arrival_times = [sum(arrival_intervals[0:i]) for i in range(len(packets))]
        for packet, arrival_time in zip(packets, arrival_times):
            packet.arrival_time = arrival_time
