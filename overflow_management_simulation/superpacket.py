from dataclasses import dataclass
from typing import List

from cached_property import cached_property


@dataclass
class Packet:
    index: int
    arrival_time: int
    transmission_time = None
    superpacket = None

    def __eq__(self, other):
        return self.superpacket == other.superpacket and self.index == other.index

    def __repr__(self):
        return f"<Packet(sp={self.superpacket.id_}, time={self.arrival_time}), transmitted_at={self.transmission_time}>"

    def __hash__(self):
        return hash((self.arrival_time, self.superpacket))


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
        return hash(self.id_)

    def __eq__(self, other):
        return hash(self) == hash(other)
