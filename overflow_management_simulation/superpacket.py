from dataclasses import dataclass
from typing import List

from cached_property import cached_property


@dataclass
class Packet:
    index: int
    arrival_time: int
    superpacket = None

    def __repr__(self):
        return f"Packet(sp={self.superpacket.id_}, time={self.arrival_time}"

    def __hash__(self):
        return hash((self.arrival_time, self.superpacket))


@dataclass
class Superpacket:
    id_: int
    packets: List[Packet]
    weight: int = 1

    @cached_property
    def max_time(self):
        return max(p.arrival_time for p in self.packets)

    def __hash__(self):
        return hash(self.id_)
