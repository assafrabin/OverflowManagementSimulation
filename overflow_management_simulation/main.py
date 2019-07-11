from itertools import groupby
import matplotlib.pyplot as plt

from routers import TailDropRouter, PriorityRouter, PriorityGiveUpRouter
from simulation import Simulation
import csv

NUMBER_OF_REPEATS = 10
N = 30
K = 5
T = 50
CAPACITY = 1
CSV_OUTPUT_PATH = r'c:\a\simulation_results.csv'


def main():
    all_results = []
    for beta in [i / 50.0 for i in range(50)]:
        for router in [TailDropRouter(capacity=CAPACITY),
                       PriorityRouter(capacity=CAPACITY),
                       PriorityGiveUpRouter(capacity=CAPACITY, beta=beta)]:
            simulation = Simulation(router=router, n=N, k=K, beta=beta, max_time=T,
                                    number_of_repeats=NUMBER_OF_REPEATS)
            res = simulation.run()
            res.print()
            all_results.append(res)

    with open(CSV_OUTPUT_PATH, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(["router", "beta", "rate"])
        legend = []
        for router_name, group in groupby(sorted(all_results, key=lambda res: res.router.NAME),
                                          key=lambda res: res.router.NAME):
            results = list(group)
            for result in results:
                csv_writer.writerow([result.router.NAME, result.beta, result.average_success_rate])

            plt.plot([res.beta for res in results], [res.average_success_rate for res in results])
            legend.append(router_name)

    plt.legend(legend)
    plt.show()


if __name__ == '__main__':
    main()
