import json
import os
from itertools import groupby
import matplotlib.pyplot as plt
import csv
import tempfile

from overflow_management_simulation.routers import TailDropRouter, PriorityRouter, PriorityGiveUpRouter, \
    WeightedPriorityRouter, WeightedPriorityGiveUpRouter, GreedyWeightedRouter
from overflow_management_simulation.simulation import Simulation


def main():
    with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
        conf = json.load(f)
    all_results = []
    for beta in [i / 10.0 for i in range(10)]:
        routers = [
            PriorityGiveUpRouter(capacity=conf['capacity'], buffer_size=conf['buffer_size'], beta=beta),
            WeightedPriorityGiveUpRouter(capacity=conf['capacity'], buffer_size=conf['buffer_size'], n=conf['n'],
                                         beta=beta),
            PriorityRouter(capacity=conf['capacity'], buffer_size=conf['buffer_size']),
            WeightedPriorityRouter(capacity=conf['capacity'], buffer_size=conf['buffer_size'], n=conf['n']),
            TailDropRouter(capacity=conf['capacity'], buffer_size=conf['buffer_size']),
            GreedyWeightedRouter(capacity=conf['capacity'], buffer_size=conf['buffer_size']),
        ]
        for router in routers:
            simulation = Simulation(router=router, n=conf['n'], k=conf['k'], beta=beta, lam=conf['lambda'],
                                    number_of_repeats=conf['number_of_repeats'], weighted=conf['weighted'])
            res = simulation.run()
            res.print()
            all_results.append(res)

    CSV_OUTPUT_PATH = os.path.join(tempfile.mkdtemp(), 'simulation_results.csv')
    with open(CSV_OUTPUT_PATH, 'w', newline='') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["router", "beta", "rate"])
        legend = []
        for router_name, group in groupby(sorted(all_results, key=lambda res: str(res.router)),
                                          key=lambda res: str(res.router)):
            results = list(group)
            for result in results:
                csv_writer.writerow([str(result.router), result.beta, result.average_success_rate])

            plt.plot([res.beta for res in results],
                     [res.average_success_rate for res in results])
            legend.append(router_name)

    plt.legend(legend)

    if conf['plot_results']:
        plt.show()

    print(f"Result file: {CSV_OUTPUT_PATH}")


if __name__ == '__main__':
    main()
