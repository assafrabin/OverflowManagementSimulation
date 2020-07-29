from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations, chain, product
from typing import Dict, List

from cached_property import cached_property

from overflow_management_simulation.routers import Router
from overflow_management_simulation.simulation_results import SimulationResult
from overflow_management_simulation.superpacket import Superpacket, Packet


@dataclass
class Burst:
    time: int
    packets: List[Packet]

    def to_dict(self):
        return {
            "time": self.time,
            "size": len(self.packets)
        }


class Simulation:
    def __init__(self, superpackets, beta, k, capacity, buffer_size):
        self.superpackets = superpackets
        self.k = k
        self.beta = beta
        self.capacity = capacity
        self.buffer_size = buffer_size

    @cached_property
    def T(self):
        return max(sp.max_time for sp in self.superpackets)

    @cached_property
    def completed_threshold(self):
        return (1 - self.beta) * self.k

    def is_superpacket_completed(self, packets: List[Packet]):
        return len(packets) >= self.completed_threshold

    @cached_property
    def bursts(self) -> List[Burst]:
        res = []
        for t in range(self.T):
            participating_packets = [p for sp in self.superpackets for p in sp.packets if p.arrival_time == t]
            if participating_packets:
                res.append(Burst(time=t, packets=participating_packets))
        return res

    @cached_property
    def average_burst_size(self):
        return sum(len(burst.packets) for burst in self.bursts) / float(len(self.bursts))

    def run(self, router: Router) -> SimulationResult:
        transmitted_packets: List[Packet] = [packet
                                             for burst in self.bursts
                                             for packet in router.route(burst.packets, self.capacity, self.buffer_size)]

        return self.evaluate_assignment(transmitted_packets)

    def evaluate_assignment(self, transmitted_packets: List[Packet]) -> SimulationResult:
        superpacket_to_transmitted_packets: Dict[Superpacket, List[Packet]] = defaultdict(list)
        for packet in transmitted_packets:
            superpacket_to_transmitted_packets[packet.superpacket].append(packet)

        completed_superpackets = [sp for sp, packets in superpacket_to_transmitted_packets.items()
                                  if self.is_superpacket_completed(packets)]
        return SimulationResult(self, self.superpackets, completed_superpackets)

    def find_opt(self):
        if self.buffer_size > 0:
            raise ValueError("Cannot find OPT in the buffered case")

        combinations_by_time = []
        for burst in self.bursts:
            combinations_by_time.append(list(combinations(burst.packets, r=self.capacity)
                                             if len(burst.packets) > self.capacity else [burst.packets]))

        possible_assignments = [
            list(chain(*chunked_assignment))
            for chunked_assignment in product(*combinations_by_time)
        ]

        results = sorted([self.evaluate_assignment(assignment) for assignment in possible_assignments],
                         key=lambda res: res.completed_weight, reverse=True)

        return results[0]
