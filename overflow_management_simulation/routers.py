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
        prioritized_packets = sorted(packets, key=self.give_priority, reverse=True)
        if 0 in [p.superpacket.id_ for p in packets]:
            a = 1

        transmitted_packets = []
        for packet in prioritized_packets:
            transmitted_size = sum(p.size for p in transmitted_packets)
            if transmitted_size + packet.size <= capacity:
                transmitted_packets.append(packet)

        prioritized_packets = [p for p in prioritized_packets if p not in transmitted_packets]

        self.buffer.clear()
        for packet in prioritized_packets:
            buffered_size = sum(p.size for p in self.buffer)
            if buffered_size > buffer_size:
                break

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
        return f"{self.NAME} - weighted: {self.weighted}"


@dataclass
class PrioritySelfEliminationsRouter(PriorityRouter):
    NAME = "Priority Self-Eliminations"
    beta: float
    alpha: float

    def is_eliminated(self, packet):
        return random.random() > (1 - self.beta - self.alpha)

    def give_priority(self, packet):
        return -1 if self.is_eliminated(packet) else self.priority(packet, self.weighted)

    def __str__(self):
        return f'{super(PrioritySelfEliminationsRouter, self).__str__()} (alpha={self.alpha})'


@dataclass
class PrioritySelfEliminationsInAdvanceRouter(PrioritySelfEliminationsRouter):
    NAME = "Priority Self-Eliminations in Advance"
    n: int
    k: int

    def __post_init__(self):
        super(PrioritySelfEliminationsInAdvanceRouter, self).__post_init__()
        self.superpacket_to_self_eliminations = {i: self.choose_indices(self.k, self.beta * self.k) for i in
                                                 range(self.n)}

    def is_eliminated(self, packet):
        return packet.index in self.superpacket_to_self_eliminations[packet.superpacket.id_]


@dataclass
class GreedyWeightedRouter(Router):
    NAME = "Greedy Weighted"

    def give_priority(self, packet):
        return packet.superpacket.weight
