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
        random.shuffle(packets)
        ordered_packets = sorted(packets, key=self.give_priority, reverse=True)
        self.buffer = ordered_packets[self.capacity:self.capacity + self.buffer_size]

        if self.NAME == WeightedPriorityGiveUpRouter.NAME and len(packets_to_route) > 1:
            a = 1
        return ordered_packets[:self.capacity]

    def __str__(self):
        return self.NAME

    @abstractmethod
    def give_priority(self, packet):
        pass


class TailDropRouter(Router):
    NAME = "Tail Drop"

    def give_priority(self, packet):
        return random.random()


class PriorityRouter(Router):
    NAME = "Priority"

    def give_priority(self, packet):
        return packet.superpacket.id_


class WeightedPriorityRouter(Router):
    NAME = "Weighted Priority"

    def __init__(self, capacity, buffer_size, n, **kwargs):
        super().__init__(capacity, buffer_size, **kwargs)
        self.n = n

    def give_priority(self, packet):
        h_s = packet.superpacket.id_ / float(self.n)
        r_s = h_s ** (1 / float(packet.superpacket.weight))
        return r_s


class PriorityGiveUpRouter(Router):
    NAME = "Priority GiveUp"

    def __init__(self, beta, alpha=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.beta = round(beta, 2)
        self.alpha = round(alpha, 2)

    def give_priority(self, packet):
        return -1 if random.random() > (1 - self.beta - self.alpha) else packet.superpacket.id_

    def __str__(self):
        return f'{self.NAME} (alpha={self.alpha})'


class WeightedPriorityGiveUpRouter(Router):
    NAME = "Weighted Priority GiveUp"

    def __init__(self, n, beta, alpha=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.n = n
        self.beta = round(beta, 2)
        self.alpha = round(alpha, 2)

    def give_priority(self, packet):
        h_s = packet.superpacket.id_ / float(self.n)
        r_s = h_s ** (1 / float(packet.superpacket.weight))
        return -1 if random.random() > (1 - self.beta - self.alpha) else r_s


class GreedyWeightedRouter(Router):
    NAME = "Greedy Weighted"

    def give_priority(self, packet):
        return packet.superpacket.weight
