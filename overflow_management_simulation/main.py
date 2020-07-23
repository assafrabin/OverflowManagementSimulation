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
    WeightedPriorityRouter, WeightedPrioritySelfEliminationsRouter, GreedyWeightedRouter, \
    PrioritySelfEliminationsInAdvanceRouter
from overflow_management_simulation.simulation import Simulation
from overflow_management_simulation.simulation_results import SimulationsResult
from overflow_management_simulation.traffic_generators import MarkovTrafficGenerator, PoissonTrafficGenerator

DEFAULT_CONF_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CSV_OUTPUT_PATH = os.path.join(tempfile.mkdtemp(), 'simulation_results.csv')

matplotlib.use("TKAgg")

log = logging.Logger('Overflow Logger')


def main():
    number_of_repeats = 10
    n = 15
    k = 10
    lam = 3
    capacity = 1
    buffer_size = 0
    plot_results = True
    weighted = True
    csv_output_path = DEFAULT_CSV_OUTPUT_PATH

    all_results = []
    beta_values = [i / 10.0 for i in range(10)]
    markov_traffic_generator = MarkovTrafficGenerator(lam=lam, k=k, number_of_markovs=10, number_of_intervals=10)
    poisson_Traffic_generator = PoissonTrafficGenerator(lam=lam, k=k, n=n)
    simulation1 = Simulation(superpackets=markov_traffic_generator.generate_superpackets(),
                            beta=0.1, k=k, weighted=weighted, capacity=capacity, buffer_size=buffer_size)
    rows1 = [b.to_dict() for b in simulation1.bursts]
    for r in rows1:
        r['type'] = "markov"
    simulation2 = Simulation(superpackets=poisson_Traffic_generator.generate_superpackets(),
                            beta=0.1, k=k, weighted=weighted, capacity=capacity, buffer_size=buffer_size)
    rows2 = [b.to_dict() for b in simulation2.bursts]
    for r in rows2:
        r['type'] = "poisson"
    print(f"markov - {simulation1.average_burst_size}, pois - {simulation2.average_burst_size}")
    df = pd.DataFrame(rows1 + rows2)
    sns.set_style("darkgrid")
    sns.lineplot(x="time", y="size", hue="type", data=df, legend="full")
    plt.show()
    exit()

    with tqdm(total=len(beta_values) * number_of_repeats, file=sys.stdout) as pbar:
        for beta in beta_values:
            assert int(beta * k) == beta * k
            routers = [
                # PrioritySelfEliminationsRouter(beta=beta),
                WeightedPrioritySelfEliminationsRouter(n=n, beta=beta),
                # PriorityRouter(),
                WeightedPriorityRouter(n=n),
                TailDropRouter(),
                # GreedyWeightedRouter(),
            ]
            # routers = [PrioritySelfEliminationsRouter(beta=beta),
            #            PrioritySelfEliminationsInAdvanceRouter(n=n, k=k, beta=beta)]
            results_by_router = defaultdict(list)
            for repeat in range(number_of_repeats):
                simulation = Simulation(superpackets=markov_traffic_generator.generate_superpackets(),
                                        beta=beta, k=k, weighted=weighted, capacity=capacity, buffer_size=buffer_size)
                for router in routers:
                    res = simulation.run(router=router)
                    results_by_router[str(router)].append(res)
                pbar.update(1)
            for router_name, results in results_by_router.items():
                simulations_result = SimulationsResult(router_name=router_name, n=n, k=k, beta=beta,
                                                       lam=lam, results=results)
                all_results.append(simulations_result)

    rows = [sr.to_dict() for sr in all_results]
    df = pd.DataFrame(rows)

    if plot_results:
        # plot graph
        sns.set_style("darkgrid")
        ax = sns.lineplot(x="beta", y="success_rate", hue="router", data=df, legend="full")
        ax.set_ylabel("Goodput Fraction")
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles=handles[1:], labels=labels[1:])
        plt.show()


if __name__ == '__main__':
    main()
