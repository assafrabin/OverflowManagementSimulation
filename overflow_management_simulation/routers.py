import random
from abc import ABCMeta, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import ClassVar


class Router(metaclass=ABCMeta):
    NAME: ClassVar[str] = NotImplemented

    def __post_init__(self):
        self.buffer = []

    def route(self, burst, capacity, buffer_size):
        packets_to_route = burst.packets + self.buffer
        if not packets_to_route:
            return []
        random.shuffle(packets_to_route)
        prioritized_packets = list(sorted(packets_to_route, key=self.give_priority, reverse=True))

        transmitted_packets = []
        for packet in prioritized_packets:
            if len(transmitted_packets) < capacity:
                transmitted_packets.append(packet)
                prioritized_packets.remove(packet)
                packet.transmission_time = burst.time
                if packet.transmission_time < packet.arrival_time:
                    pass

        self.buffer.clear()
        for packet in prioritized_packets:
            if len(self.buffer) < buffer_size:
                self.buffer.append(packet)

        return transmitted_packets

    def __str__(self):
        return self.NAME

    @abstractmethod
    def give_priority(self, packet):
        pass

    @staticmethod
    def choose_indices(a, b):
        return random.sample(list(range(a)), k=int(b))


@dataclass
class TailDropRouter(Router):
    NAME = "Tail Drop"

    def give_priority(self, packet):
        return random.random()


@dataclass
class PriorityRouter(Router):
    NAME = "Priority"
    weighted: bool

    def give_priority(self, packet):
        return self.priority(packet, self.weighted)

    @staticmethod
    def priority(packet, weighted):
        return packet.superpacket.weighted_priority if weighted else packet.superpacket.id_

    def __str__(self):
        return f"{self.NAME}" + (f" - unweighted" if not self.weighted else "")


class PrioritySubsetsRouter(PriorityRouter):
    NAME = 'Priority Subsets'

    def route(self, burst, capacity, buffer_size):
        packets_to_route = burst.packets + self.buffer
        if not packets_to_route:
            return []
        random.shuffle(packets_to_route)
        subsets = defaultdict(list)
        for packet in packets_to_route:
            subset = random.choice(range(capacity))
            subsets[subset].append(packet)

        transmitted_packets = []
        for subset_packets in subsets.values():
            prioritized_subset_packets = list(sorted(subset_packets, key=self.give_priority, reverse=True))
            transmitted_packets.append(prioritized_subset_packets[0])

        not_transmitted_packets = [p for p in packets_to_route if p not in transmitted_packets]
        prioritized_packets = list(sorted(not_transmitted_packets, key=self.give_priority, reverse=True))

        self.buffer.clear()
        for packet in prioritized_packets:
            if len(self.buffer) < buffer_size:
                self.buffer.append(packet)

        return transmitted_packets


@dataclass
class PrioritySelfEliminationsRouter(PriorityRouter):
    NAME = "PSE"
    k: int
    beta: float
    alpha: float = 0

    @property
    def eff_beta(self):
        return min(max(self.beta - self.alpha, 0), 1)

    def __post_init__(self):
        super(PrioritySelfEliminationsRouter, self).__post_init__()
        self.superpacket_to_self_eliminations = {}

    def give_priority(self, packet):
        return -1 if self.is_eliminated(packet) else self.priority(packet, self.weighted)

    def is_eliminated(self, packet):
        self_eliminations_indices = self.superpacket_to_self_eliminations.get(packet.superpacket.id_)
        if self_eliminations_indices is None:
            self.superpacket_to_self_eliminations[packet.superpacket.id_] = \
                self.choose_indices(self.k, self.eff_beta * self.k)
        return packet.index in self.superpacket_to_self_eliminations[packet.superpacket.id_]

    def __str__(self):
        return f'{super().__str__()}' + \
               (f'(\u03B1={self.alpha})' if self.alpha else '')


@dataclass
class PriorityRandomSelfEliminationsRouter(PrioritySelfEliminationsRouter):
    NAME = "Priority Random Self-Eliminations"

    def is_eliminated(self, packet):
        return random.random() > (1 - self.beta - self.alpha)


@dataclass
class GreedyWeightedRouter(Router):
    NAME = "Greedy"

    def give_priority(self, packet):
        return packet.superpacket.weight


class PSESubsetsRouter(PrioritySelfEliminationsRouter):
    NAME = 'PSE-B'

    def route(self, burst, capacity, buffer_size):
        packets_to_route = burst.packets + self.buffer
        if not packets_to_route:
            return []
        random.shuffle(packets_to_route)
        subsets = defaultdict(list)
        for packet in packets_to_route:
            subset = random.choice(range(capacity))
            subsets[subset].append(packet)

        transmitted_packets = []
        for subset_packets in subsets.values():
            prioritized_subset_packets = list(sorted(subset_packets, key=self.give_priority, reverse=True))
            transmitted_packets.append(prioritized_subset_packets[0])

        not_transmitted_packets = [p for p in packets_to_route if p not in transmitted_packets]
        prioritized_packets = list(sorted(not_transmitted_packets, key=self.give_priority, reverse=True))

        self.buffer.clear()
        for packet in prioritized_packets:
            if len(self.buffer) < buffer_size:
                self.buffer.append(packet)

        return transmitted_packets
