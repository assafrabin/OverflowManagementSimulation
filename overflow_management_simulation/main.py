import logging
import os
import sys
import tempfile
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from overflow_management_simulation.routers import TailDropRouter, PriorityRouter, \
    PrioritySelfEliminationsRouter
from overflow_management_simulation.simulation import Simulation
from overflow_management_simulation.simulation_results import SimulationsResult
from overflow_management_simulation.size_functions import NoSizes
from overflow_management_simulation.traffic_generators import MarkovTrafficGenerator
from overflow_management_simulation.weight_functions import NoWeights

DEFAULT_CONF_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CSV_OUTPUT_PATH = os.path.join(tempfile.mkdtemp(), 'simulation_results.csv')

matplotlib.use("TKAgg")

log = logging.Logger('Overflow Logger')


def main():
    number_of_repeats = 10
    capacity = 4
    buffer_size = 0
    plot_results = True
    weight_func = NoWeights()  # SomeHeavyWeights(heavy_count=1, heavy_weight=2)
    size_func = NoSizes()  # RandomSizes(max_size=4)

    beta_values = [0.1, 0.3, 0.5, 0.7]
    lam_values = [0.5, 1, 2, 3, 4]
    k_values = [10]
    capacity_values = [3]
    buffer_size_values = [0]

    all_results = []
    running_burst_size = 0
    with tqdm(total=len(beta_values) * len(lam_values) * number_of_repeats, file=sys.stdout) as pbar:
        for beta in beta_values:
            for lam in lam_values:
                for k in k_values:
                    for capacity in capacity_values:
                        for buffer_size in buffer_size_values:
                            traffic_generator = MarkovTrafficGenerator(lam=lam, k=k, weight_func=weight_func,
                                                                       size_func=size_func,
                                                                       number_of_markovs=10, max_time=30)
                            # traffic_generator = PoissonTrafficGenerator(lam=lam, k=k, n=n, weight_func=weight_func,
                            #                                             size_func=size_func)

                            routers = [
                                PrioritySelfEliminationsRouter(weighted=True, beta=beta, alpha=0, k=k),
                                PriorityRouter(weighted=True),
                                TailDropRouter(),
                                # GreedyWeightedRouter(),
                            ]

                            assert int(beta * k) == beta * k
                            results_by_router = defaultdict(list)
                            for repeat in range(number_of_repeats):
                                simulation = Simulation(superpackets=traffic_generator.generate_superpackets(),
                                                        beta=beta, k=k, capacity=capacity, buffer_size=buffer_size)
                                for router in routers:
                                    res = simulation.run(router=router)
                                    results_by_router[str(router)].append(res)

                                running_burst_size += simulation.average_burst_size
                                pbar.update(1)

                            all_results.extend([
                                SimulationsResult(router_name=router_name, n=len(simulation.superpackets), k=k,
                                                  beta=beta, lam=traffic_generator.lam, results=results)
                                for router_name, results in results_by_router.items()])
    rows = [r.to_dict() for r in all_results]
    df = pd.DataFrame(rows)

    if plot_results:
        # plot graph
        sns.set_style("darkgrid")
        g = sns.relplot(x="average_burst_size", y="success_rate",
                        hue="router", col="beta", col_wrap=2, data=df, kind="line",
                        markers=True, dashes=True, style="router")
        for ax in g.axes.flat:
            ax.set_xlabel("Average Burst Size")
            ax.set_ylabel("Goodput Fraction")

        # ax = sns.lineplot(x="beta", y="success_rate", hue="router", data=df, legend="full",
        #                   markers=True, dashes=True, style="router")
        # ax.set_ylabel("Goodput Fraction")
        # ax.set_xlabel("Redundancy")
        # handles, labels = ax.get_legend_handles_labels()
        # ax.legend(handles=handles[1:], labels=labels[1:])
        plt.show()


if __name__ == '__main__':
    main()
