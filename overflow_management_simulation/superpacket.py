from dataclasses import dataclass
from typing import List

from cached_property import cached_property


@dataclass
class Packet:
    index: int
    arrival_time: int
    superpacket = None
    transmission_time = None

    def __eq__(self, other):
        return self.superpacket == other.superpacket and self.index == other.index

    def __repr__(self):
        return f"<Packet(sp={self.superpacket.id_}, time={self.arrival_time}), transmitted_at={self.transmission_time}>"

    def __hash__(self):
        return hash((self.arrival_time, self.superpacket))

    def clone(self):
        p = Packet(self.index, self.arrival_time)
        p.superpacket = self.superpacket
        return p


@dataclass
class Superpacket:
    id_: int
    packets: List[Packet]
    weight: int
    weighted_priority: float

    @cached_property
    def max_time(self):
        return max(p.arrival_time for p in self.packets)

    def __hash__(self):
        return self.id_

    def __eq__(self, other):
        return hash(self) == hash(other)

    def clone(self):
        cloned_packets = [p.clone() for p in self.packets]
        return Superpacket(self.id_, cloned_packets, self.weight, self.weighted_priority)

    @property
    def transmitted_packets(self):
        return [p for p in self.packets if p.transmission_time is not None]
