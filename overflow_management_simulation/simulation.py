from superpacket import Superpacket
from simulation_results import SimulationResults, SimulationResult


class Simulation:
    def __init__(self, router, n, k, beta, max_time, number_of_repeats):
        self.router = router
        self.n = n
        self.k = k
        self.beta = beta
        self.max_time = max_time
        self.number_of_repeats = number_of_repeats

    def run(self):
        return SimulationResults(router=self.router, n=self.n, k=self.k, beta=self.beta, max_time=self.max_time,
                                 results=[self.single_run() for _ in range(self.number_of_repeats)])

    def single_run(self):
        superpackets = [Superpacket(id_=i, number_of_packets=self.k, beta=self.beta) for i in range(self.n)]

        for sp in superpackets:
            sp.set_arrival_times(max_time=self.max_time)

        for t in range(self.max_time):
            participating_packets = [p for sp in superpackets for p in sp.packets if p.arrival_time == t]
            transmitted_packets = self.router.route(participating_packets)
            for p in transmitted_packets:
                p.is_transmitted = True

        return SimulationResult(superpackets)
