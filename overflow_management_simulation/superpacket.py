import random


class Superpacket:
    def __init__(self, id_, number_of_packets, beta):
        self.beta = beta
        self.id_ = id_
        self.packets = [Packet(id_) for _ in range(number_of_packets)]

    def set_arrival_times(self, max_time):
        arrival_times = random.choices(range(max_time), k=len(self.packets))
        for packet, arrival_time in zip(self.packets, arrival_times):
            packet.arrival_time = arrival_time

    @property
    def is_completed(self):
        transmitted_packets = [p for p in self.packets if p.is_transmitted]
        return len(transmitted_packets) / float(len(self.packets)) >= (1 - self.beta)


class Packet:
    def __init__(self, superpacket_id):
        self.superpacket_id = superpacket_id
        self.arrival_time = None
        self.is_transmitted = False
