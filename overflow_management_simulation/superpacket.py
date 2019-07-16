from cached_property import cached_property


class Superpacket:
    def __init__(self, id_, number_of_packets, beta):
        self.beta = beta
        self.id_ = id_
        self.packets = [Packet(id_) for _ in range(number_of_packets)]

    @property
    def is_completed(self):
        transmitted_packets = [p for p in self.packets if p.is_transmitted]
        return len(transmitted_packets) / float(len(self.packets)) >= (1 - self.beta)

    @cached_property
    def max_time(self):
        return max(p.arrival_time for p in self.packets)


class Packet:
    def __init__(self, superpacket_id):
        self.superpacket_id = superpacket_id
        self.arrival_time = None
        self.is_transmitted = False
