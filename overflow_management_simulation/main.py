import random
import sys

from tqdm import tqdm
import logging
import os
import tempfile
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from overflow_management_simulation.routers import TailDropRouter, PriorityRouter, PrioritySelfEliminationsRouter, \
    GreedyWeightedRouter, PrioritySelfEliminationsInAdvanceRouter
from overflow_management_simulation.simulation import Simulation, Burst
from overflow_management_simulation.simulation_results import SimulationsResult
from overflow_management_simulation.traffic_generators import MarkovTrafficGenerator, PoissonTrafficGenerator
from overflow_management_simulation.weight_functions import NoWeights, SomeHeavyWeights
from overflow_management_simulation.size_functions import RandomSizes

DEFAULT_CONF_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CSV_OUTPUT_PATH = os.path.join(tempfile.mkdtemp(), 'simulation_results.csv')

matplotlib.use("TKAgg")

log = logging.Logger('Overflow Logger')


def main():
    number_of_repeats = 10
    n = 50
    k = 20
    lam = 3
    capacity = 4
    buffer_size = 0
    plot_results = True
    weight_func = SomeHeavyWeights(heavy_count=1, heavy_weight=2)
    size_func = RandomSizes(max_size=4)

    all_results = []
    beta_values = [i / 10.0 for i in range(10)]

    # traffic_generator = MarkovTrafficGenerator(lam=lam, k=k, n=n, weight_func=weight_func, size_func=size_func,
    #                                            number_of_markovs=10, number_of_intervals=20)
    traffic_generator = PoissonTrafficGenerator(lam=lam, k=k, n=n, weight_func=weight_func, size_func=size_func)

    running_burst_size = 0
    with tqdm(total=len(beta_values) * number_of_repeats, file=sys.stdout) as pbar:
        for beta in beta_values:
            assert int(beta * k) == beta * k
            routers = [
                PrioritySelfEliminationsInAdvanceRouter(weighted=True, beta=beta, alpha=0, n=n, k=k),
                PriorityRouter(weighted=True),
                TailDropRouter(),
                GreedyWeightedRouter(),
            ]
            results_by_router = defaultdict(list)
            for repeat in range(number_of_repeats):
                simulation = Simulation(superpackets=traffic_generator.generate_superpackets(),
                                        beta=beta, k=k, capacity=capacity, buffer_size=buffer_size)
                running_burst_size += simulation.average_burst_size
                for router in routers:
                    res = simulation.run(router=router)
                    results_by_router[str(router)].append(res)
                pbar.update(1)

            for router_name, results in results_by_router.items():
                simulations_result = SimulationsResult(router_name=router_name, n=n, k=k, beta=beta,
                                                       lam=lam, results=results)
                all_results.append(simulations_result)

    print(f"Average burst size: {running_burst_size / (number_of_repeats * len(beta_values))}")

    rows = [sr.to_dict() for sr in all_results]
    df = pd.DataFrame(rows)

    if plot_results:
        # plot graph
        sns.set_style("darkgrid")
        ax = sns.lineplot(x="beta", y="success_rate", hue="router", data=df, legend="full")
        ax.set_ylabel("Goodput Fraction")
        ax.set_xlabel("Redundancy")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles[1:], labels=labels[1:])
        plt.show()


if __name__ == '__main__':
    main()
