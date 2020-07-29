import random
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

import numpy as np

from overflow_management_simulation.size_functions import SizeFunc
from overflow_management_simulation.superpacket import Superpacket, Packet
from overflow_management_simulation.weight_functions import WeightFunc


@dataclass
class TrafficGenerator:
    lam: float
    k: int
    n: int
    weight_func: WeightFunc
    size_func: SizeFunc

    @abstractmethod
    def generate_superpackets(self) -> List[Superpacket]:
        pass

    def generate_superpacket(self, superpacket_id: int, arrival_times: List[int]) -> Superpacket:
        packets = [Packet(index=i, arrival_time=arrival_time,
                          size=self.size_func(superpacket_id=superpacket_id, index=i))
                   for i, arrival_time in enumerate(arrival_times)]
        superpacket_weight = self.weight_func(superpacket_id=superpacket_id)
        weighted_priority = self.calc_weighted_priority(superpacket_weight)
        sp = Superpacket(id_=superpacket_id, packets=packets, weight=superpacket_weight,
                         weighted_priority=weighted_priority)
        for packet in packets:
            packet.superpacket = sp

        return sp

    @staticmethod
    def calc_weighted_priority(weight):
        """
        Calculates r(s)
        """
        h_s = random.random()
        p_s = (1 - h_s ** float(weight))
        return p_s


@dataclass
class MarkovTrafficGenerator(TrafficGenerator):
    number_of_markovs: int
    number_of_intervals: int

    def generate_superpackets(self) -> List[Superpacket]:
        bursts = self.generate_bursts()
        total_packets = sum(bursts.values())
        n = int(total_packets / self.k)
        sp_to_arrival_times = defaultdict(list)

        for sp_id in range(n):
            non_empty_bursts = {t: number_of_packets for t, number_of_packets in bursts.items() if number_of_packets}
            if len(non_empty_bursts) < self.k:
                break
            arrival_times = random.sample(non_empty_bursts.keys(), k=self.k)
            for t in arrival_times:
                bursts[t] -= 1
            sp_to_arrival_times[sp_id] = arrival_times

        return [self.generate_superpacket(sp_id, arrival_times) for sp_id, arrival_times in sp_to_arrival_times.items()]

    def generate_bursts(self) -> Dict[int, int]:
        bursts = defaultdict(lambda: 0)
        for _ in range(self.number_of_markovs):
            on_off_intervals = np.random.poisson(self.lam, size=self.number_of_intervals)
            t = 0
            for i, interval in enumerate(on_off_intervals):
                for _ in range(interval):
                    if i % 2 == 0:
                        bursts[t] = bursts[t] + 1
                    t += 1

        return bursts


@dataclass
class PoissonTrafficGenerator(TrafficGenerator):
    n: int

    def generate_superpackets(self):
        return [self.generate_superpacket(sp_id, self.generate_arrival_times()) for sp_id in range(self.n)]

    def generate_arrival_times(self):
        arrival_intervals = np.random.poisson(self.lam, size=self.k + 1)
        arrival_intervals[arrival_intervals == 0] = 1
        arrival_times = [sum(arrival_intervals[0:i]) for i in range(1, self.k + 1)]
        return arrival_times
