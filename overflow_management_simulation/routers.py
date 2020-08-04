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
        prioritized_packets = list(sorted(packets, key=self.give_priority, reverse=True))

        transmitted_packets = []
        for packet in prioritized_packets:
            transmitted_size = sum(p.size for p in transmitted_packets)
            if transmitted_size + packet.size <= capacity:
                transmitted_packets.append(packet)

        not_transmitted_packets = [p for p in prioritized_packets if p not in transmitted_packets]

        self.buffer.clear()
        for packet in not_transmitted_packets:
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
        return f"{self.NAME}" + (f" - unweighted" if not self.weighted else "")


@dataclass
class PrioritySelfEliminationsRouter(PriorityRouter):
    NAME = "PSE"
    k: int
    beta: float
    alpha: float = 0

    def __post_init__(self):
        super(PrioritySelfEliminationsRouter, self).__post_init__()
        self.superpacket_to_self_eliminations = {}

    def give_priority(self, packet):
        return -1 if self.is_eliminated(packet) else self.priority(packet, self.weighted)

    def is_eliminated(self, packet):
        self_eliminations_indices = self.superpacket_to_self_eliminations.get(packet.superpacket.id_)
        if self_eliminations_indices is None:
            self.superpacket_to_self_eliminations[packet.superpacket.id_] = self.choose_indices(self.k,
                                                                                                self.beta * self.k)
        return packet.index in self.superpacket_to_self_eliminations[packet.superpacket.id_]

    def __str__(self):
        return f'{super().__str__()}' + \
               (f'(alpha={self.alpha})' if self.alpha else '')


@dataclass
class PriorityRandomSelfEliminationsRouter(PrioritySelfEliminationsRouter):
    NAME = "Priority Random Self-Eliminations"

    def is_eliminated(self, packet):
        return random.random() > (1 - self.beta - self.alpha)


@dataclass
class GreedyWeightedRouter(Router):
    NAME = "Greedy Weighted"

    def give_priority(self, packet):
        return packet.superpacket.weight
