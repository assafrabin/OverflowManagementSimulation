import random
from abc import ABCMeta, abstractmethod


class Router(metaclass=ABCMeta):
    NAME = NotImplemented

    def __init__(self, capacity, **kwargs):
        self.capacity = capacity

    def route(self, packets):
        if not packets:
            return []
        return self._route(packets)

    @abstractmethod
    def _route(self, packets):
        pass


class TailDropRouter(Router):
    NAME = "Tail Drop"

    def _route(self, packets):
        return random.choices(packets, k=self.capacity)


class PriorityRouter(Router):
    NAME = "Priority"

    def _route(self, packets):
        return sorted(packets, key=lambda packet: packet.superpacket_id, reverse=True)[:self.capacity]


class PriorityGiveUpRouter(Router):
    NAME = "Priority GiveUp"

    def __init__(self, beta, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beta = beta

    def _route(self, packets):
        def give_up_key(packet):
            return 0 if random.random() > 1 - self.beta else packet.superpacket_id
        return sorted(packets, key=lambda packet: give_up_key(packet), reverse=True)[:self.capacity]
