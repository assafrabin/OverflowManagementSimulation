import csv
from itertools import groupby
from typing import Iterable

from overflow_management_simulation.simulation_results import SimulationsResult


class CsvWriter:
    def __init__(self, path: str):
        self.path = path

    def write_results(self, simulation_results: Iterable[SimulationsResult]):
        with open(self.path, 'w', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow(["router", "beta", "rate"])

            for router_name, group in groupby(sorted(simulation_results, key=lambda res: str(res.router)),
                                              key=lambda res: str(res.router)):
                results = list(group)
                for result in results:
                    csv_writer.writerow([str(result.router), result.beta, result.average_success_rate])
