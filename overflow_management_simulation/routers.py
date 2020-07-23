import random
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import ClassVar


class Router(metaclass=ABCMeta):
    NAME: ClassVar[str] = NotImplemented

    def __post_init__(self):
        self.buffer = []

    def route(self, packets, capacity, buffer_size):
        packets_to_route = packets + self.buffer
        if not packets_to_route:
            return []
        random.shuffle(packets)
        ordered_packets = sorted(packets, key=self.give_priority, reverse=True)
        self.buffer = ordered_packets[capacity:capacity + buffer_size]
        return ordered_packets[:capacity]

    def __str__(self):
        return self.NAME

    @abstractmethod
    def give_priority(self, packet):
        pass


@dataclass
class TailDropRouter(Router):
    NAME = "Tail Drop"

    def give_priority(self, packet):
        return random.random()


@dataclass
class PriorityRouter(Router):
    NAME = "Priority"

    def give_priority(self, packet):
        return packet.superpacket.id_


@dataclass
class WeightedPriorityRouter(Router):
    NAME = "Weighted Priority"
    n: int

    def give_priority(self, packet):
        h_s = packet.superpacket.id_ / float(self.n)
        r_s = h_s ** (1 / float(packet.superpacket.weight))
        return r_s


@dataclass
class PrioritySelfEliminationsRouter(Router):
    NAME = "Priority Self-Eliminations"
    beta: float
    alpha: float = 0

    def give_priority(self, packet):
        return -1 if random.random() > (1 - self.beta - self.alpha) else packet.superpacket.id_

    def __str__(self):
        return f'{self.NAME} (alpha={self.alpha})'


@dataclass
class PrioritySelfEliminationsGenCapRouter(Router):
    NAME = "Priority Self-Eliminations Gen-Cap"
    beta: float
    alpha: float = 0

    def route(self, packets, capacity, buffer_size):
        packets_to_route = packets + self.buffer
        if not packets_to_route:
            return []
        ordered_packets = sorted(packets_to_route, key=self.give_priority, reverse=True)
        self.buffer = ordered_packets[capacity:capacity + buffer_size]
        return ordered_packets[:capacity]


    def give_priority(self, packet):
        return -1 if random.random() > (1 - self.beta - self.alpha) else packet.superpacket.id_

    def __str__(self):
        return f'{self.NAME} (alpha={self.alpha})'


@dataclass
class PrioritySelfEliminationsInAdvanceRouter(Router):
    NAME = "Priority Self-Eliminations in Advance"
    n: int
    k: int
    beta: float
    alpha: float = 0

    def __post_init__(self):
        super(PrioritySelfEliminationsInAdvanceRouter, self).__post_init__()
        self.superpacket_to_self_eliminations = {i: self.choose_indices(self.k, self.beta * self.k) for i in
                                                 range(self.n)}

    def give_priority(self, packet):
        return -1 if packet.index in self.superpacket_to_self_eliminations[
            packet.superpacket.id_] else packet.superpacket.id_

    def __str__(self):
        return f'{self.NAME} (alpha={self.alpha})'

    @staticmethod
    def choose_indices(a, b):
        return random.sample(list(range(a)), k=int(b))


@dataclass
class WeightedPrioritySelfEliminationsRouter(Router):
    NAME = "Weighted Priority Self-Eliminations"
    n: int
    beta: float
    alpha: float = 0

    def give_priority(self, packet):
        h_s = packet.superpacket.id_ / float(self.n)
        r_s = h_s ** (1 / float(packet.superpacket.weight))
        return -1 if random.random() > (1 - self.beta - self.alpha) else r_s


@dataclass
class GreedyWeightedRouter(Router):
    NAME = "Greedy Weighted"

    def give_priority(self, packet):
        return packet.superpacket.weight
