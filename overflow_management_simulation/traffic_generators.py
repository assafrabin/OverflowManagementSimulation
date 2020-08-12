import random
from abc import abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict

import numpy as np

from overflow_management_simulation.superpacket import Superpacket, Packet
from overflow_management_simulation.weight_functions import WeightFunc


@dataclass
class TrafficGenerator:
    lam: float
    k: int
    weight_func: WeightFunc

    @abstractmethod
    def generate_superpackets(self) -> List[Superpacket]:
        pass

    def generate_superpacket(self, n: int, superpacket_id: int, arrival_times: List[int]) -> Superpacket:
        packets = [Packet(index=i, arrival_time=arrival_time)
                   for i, arrival_time in enumerate(arrival_times)]
        superpacket_weight = self.weight_func(superpacket_id=superpacket_id, n=n)
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
    max_time: int

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

        return [self.generate_superpacket(n, sp_id, arrival_times) for sp_id, arrival_times in
                sp_to_arrival_times.items()]

    def generate_bursts(self) -> Dict[int, int]:
        bursts = defaultdict(lambda: 0)
        lambda_off = 0.1
        lambda_on = 0.1 / self.lam
        for _ in range(self.number_of_markovs):
            current_time = 1
            while current_time <= self.max_time:
                on_times = np.random.poisson(lambda_on)
                for t in range(current_time, min(current_time + on_times, self.max_time + 1)):
                    bursts[t] += 1
                current_time += on_times
                off_times = np.random.poisson(lambda_off)
                current_time += off_times

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
