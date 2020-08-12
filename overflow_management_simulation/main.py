import logging
import os
import sys
import tempfile
from collections import defaultdict

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from numpy import average
from tqdm import tqdm

from overflow_management_simulation.routers import TailDropRouter, PriorityRouter, \
    PrioritySelfEliminationsRouter, GreedyWeightedRouter, PrioritySubsetsRouter, PSESubsetsRouter
from overflow_management_simulation.simulation import Simulation
from overflow_management_simulation.simulation_results import SimulationsResult
from overflow_management_simulation.size_functions import NoSizes, RandomSizes
from overflow_management_simulation.traffic_generators import MarkovTrafficGenerator
from overflow_management_simulation.weight_functions import NoWeights, SomeHeavyWeights

DEFAULT_CONF_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CSV_OUTPUT_PATH = os.path.join(tempfile.mkdtemp(), 'simulation_results.csv')

matplotlib.use("TKAgg")

log = logging.Logger('Overflow Logger')


def main():
    number_of_repeats = 10
    plot_results = True
    weight_func = SomeHeavyWeights(heavy_fraction=0.2, heavy_weight=5)

    beta_values = [i / 10 for i in range(0, 8)]  #
    alpha_values = [0]  # [0.1, 0.05, 0, -0.05, -0.1]#, -0.2, -0.3]  # [0]
    lam_values = [0.5]  # [i / 5 for i in range(1, 6)]
    k_values = [10]  # range(1, 31)  #
    capacity_values = [4]  # range(1, 10)  # [4]
    buffer_size_values = [10]  # range(1, 10)
    all_results = []
    running_burst_size = 0

    with tqdm(total=len(beta_values) * len(lam_values) * len(k_values) * len(capacity_values) * len(
            buffer_size_values) * number_of_repeats,
              file=sys.stdout) as pbar:
        for beta in beta_values:
            for lam in lam_values:
                for k in k_values:
                    for capacity in capacity_values:
                        for buffer_size in buffer_size_values:
                            traffic_generator = MarkovTrafficGenerator(lam=lam, k=k, weight_func=weight_func,
                                                                       number_of_markovs=10, max_time=100)

                            routers = [
                                PriorityRouter(weighted=True),
                                TailDropRouter(),
                                # PrioritySubsetsRouter(weighted=True),
                            ]

                            routers.extend([
                                # PrioritySelfEliminationsRouter(weighted=True, beta=beta, alpha=0, k=k),
                                # PSESubsetsRouter(weighted=True, beta=beta, alpha=0, k=k)
                            ])
                            routers.extend(
                                [PSESubsetsRouter(weighted=True, beta=beta, alpha=alpha, k=k)
                                 for alpha in alpha_values])
                            routers.append(GreedyWeightedRouter())

                            if not int(beta * k) == beta * k:
                                pbar.update(number_of_repeats)
                                continue

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
                                                  beta=beta, capacity=capacity, buffer_size=buffer_size,
                                                  results=results)
                                for router_name, results in results_by_router.items()])
                            a = 1
    rows = [r.to_dict() for r in all_results]
    df = pd.DataFrame(rows)

    print(average([r.average_burst_size for r in all_results]))
    if plot_results:
        # plot graph
        sns.set_style("darkgrid")
        g = sns.relplot(x="beta", y="success_rate",
                        hue="router", data=df, kind="line",
                        markers=True, dashes=False, style="router",
                        # col="beta", col_wrap=2,
                        )
        for ax, beta in zip(g.axes.flat, beta_values):
            ax.set_xlabel("\u03B2")
            ax.set_ylabel("Goodput Fraction")
            # ax.set_title(f"\u03B2 = {round(beta, 2)}")

        g._legend.texts[0].set_text("")

        # ax = sns.lineplot(x="beta", y="success_rate", hue="router", data=df, legend="full",
        #                   markers=True, dashes=True, style="router")
        # ax.set_ylabel("Goodput Fraction")
        # ax.set_xlabel("Redundancy")
        # handles, labels = ax.get_legend_handles_labels()
        # ax.legend(handles=handles[1:], labels=labels[1:])
        plt.show()


if __name__ == '__main__':
    main()
