class SimulationResult:
    def __init__(self, superpackets):
        self.superpackets = superpackets

    @property
    def completed_superpackets(self):
        return [sp for sp in self.superpackets if sp.is_completed]

    @property
    def success_rate(self):
        return len(self.completed_superpackets) / float(len(self.superpackets))


class SimulationResults:
    def __init__(self, router, n, k, beta, max_time, results):
        self.router = router
        self.n = n
        self.k = k
        self.beta = beta
        self.max_time = max_time
        self.results = results

    @property
    def average_success_rate(self):
        return sum([result.success_rate for result in self.results]) / float(len(self.results))

    def print(self):
        print(f'{self.router.NAME} - {self.beta} - {self.average_success_rate:.2f}')


