import random
from abc import ABCMeta, abstractmethod


class Router(metaclass=ABCMeta):
    NAME = NotImplemented

    def __init__(self, capacity, buffer_size, **kwargs):
        self.capacity = capacity
        self.buffer_size = buffer_size
        self.buffer = []

    def route(self, packets):
        packets_to_route = packets + self.buffer
        if not packets_to_route:
            return []
        ordered_packets = self._order(packets_to_route)
        self.buffer = ordered_packets[self.capacity:self.capacity + self.buffer_size]
        return ordered_packets[:self.capacity]

    @abstractmethod
    def _order(self, packets):
        pass

    def __str__(self):
        return self.NAME


class TailDropRouter(Router):
    NAME = "Tail Drop"

    def _order(self, packets):
        random.shuffle(packets)
        return packets


class PriorityRouter(Router):
    NAME = "Priority"

    def _order(self, packets):
        return sorted(packets, key=lambda packet: packet.superpacket_id, reverse=True)


class PriorityGiveUpRouter(Router):
    NAME = "Priority GiveUp"

    def __init__(self, beta, alpha, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beta = round(beta, 2)
        self.alpha = round(alpha, 2)

    def _order(self, packets):
        def give_up_key(packet):
            return 0 if random.random() > (1 - self.beta - self.alpha) else packet.superpacket_id

        return sorted(packets, key=lambda packet: give_up_key(packet), reverse=True)

    def __str__(self):
        return f'{self.NAME} (alpha={self.alpha})'
