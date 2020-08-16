import logging
import os
import sys
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from tqdm import tqdm

from overflow_management_simulation.routers import TailDropRouter, PriorityRouter, \
    PrioritySelfEliminationsRouter, GreedyWeightedRouter, PrioritySubsetsRouter, PSESubsetsRouter, Router
from overflow_management_simulation.simulation import Simulation
from overflow_management_simulation.simulation_results import SimulationsResult
from overflow_management_simulation.traffic_generators import MarkovTrafficGenerator, PoissonTrafficGenerator
from overflow_management_simulation.weight_functions import NoWeights, SomeHeavyWeights, WeightFunc

sns.set_style("darkgrid")

DEFAULT_CONF_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
DEFAULT_CSV_OUTPUT_PATH = os.path.join(tempfile.mkdtemp(), 'simulation_results.csv')

matplotlib.use("TKAgg")

log = logging.Logger('Overflow Logger')


@dataclass
class SimulationParams:
    x_param: str
    x_title: str

    k_values: List[int] = field(default_factory=lambda: [10])
    capacity_values: List[int] = field(default_factory=lambda: [5])
    buffer_size_values: List[int] = field(default_factory=lambda: [10])
    beta_values: List[float] = field(default_factory=lambda: [i / 10 for i in range(0, 7)])
    lam_values: List[float] = field(default_factory=lambda: [0.95])

    extra_routers: List[Router] = field(default_factory=lambda: [
        PriorityRouter(weighted=True),
        TailDropRouter()
    ])
    weight_func: WeightFunc = NoWeights()

    y_param: str = "success_rate"
    y_title: str = "Goodput Fraction"

    number_of_repeats: int = 10
    number_of_markovs: int = 10
    markov_max_time: int = 100

    split_by: Optional[str] = None
    print_average_load: bool = True

    sharex: bool = True

    @property
    def simulations_count(self):
        return len(self.beta_values) * len(self.lam_values) * len(self.k_values) * len(self.capacity_values) * len(
            self.buffer_size_values) * self.number_of_repeats


pseb_simulation_params = SimulationParams(
    x_param='beta', x_title='\u03B2',
    extra_routers=[
    ])

k_values_simulation_params = SimulationParams(x_param='k', x_title='Packets in Superpacket',
                                              k_values=list(range(2, 31)), beta_values=[.2, 1 / 3, .5],
                                              capacity_values=[4],
                                              split_by="beta")

c_values_simulation_params = SimulationParams(x_param='capacity', x_title='Link Capacity (packets/slot)',
                                              capacity_values=list(range(2, 8)), beta_values=[.2, .3, .5],
                                              split_by="beta")

b_values_simulation_params = SimulationParams(x_param='buffer_size', x_title='Buffer Size (packets)',
                                              buffer_size_values=list(range(0, 11)), beta_values=[.2, .3, .5],
                                              lam_values=[1], capacity_values=[5],
                                              split_by="beta")

lam_values_simulation_params = SimulationParams(x_param='average_burst_size',
                                                x_title='Offered Load (average packets/slot)',
                                                lam_values=[i / 10 for i in range(1, 10)], beta_values=[.2, .3, .5],
                                                capacity_values=[6],
                                                split_by="beta", print_average_load=False, sharex=False)

greedy_simulation = SimulationParams(
    x_param='beta', x_title='\u03B2', weight_func=SomeHeavyWeights(heavy_fraction=0.2, heavy_weight=5),
    extra_routers=[
        PriorityRouter(weighted=True),
        TailDropRouter(),
        GreedyWeightedRouter()
    ])

completed_superpackets_simulation = SimulationParams(
    x_param='beta', x_title='\u03B2', y_param='completed_superpackets', y_title="Completed Superpackets",
    k_values=list(range(10, 21)), beta_values=[0], number_of_repeats=30
)


def main():
    simulations_params = [k_values_simulation_params, b_values_simulation_params,
                          c_values_simulation_params, greedy_simulation, lam_values_simulation_params]
    simulations_params = [b_values_simulation_params]

    all_dfs = []
    with tqdm(total=sum(simulation_params.simulations_count for simulation_params in simulations_params),
              file=sys.stdout) as pbar:
        for simulation_params in simulations_params:
            all_results = []
            for lam in simulation_params.lam_values:
                for k in simulation_params.k_values:
                    for capacity in simulation_params.capacity_values:
                        for buffer_size in simulation_params.buffer_size_values:
                            for beta in simulation_params.beta_values:
                                # beta = (k - simulation_params.k_values[0]) / k
                                # traffic_generator = PoissonTrafficGenerator(lam=8, k=k, n=50,
                                #                                             weight_func=simulation_params.weight_func)
                                traffic_generator = MarkovTrafficGenerator(lam=lam, k=k, c=capacity,
                                                                           number_of_markovs=round(
                                                                               simulation_params.number_of_markovs
                                                                               / (1 - beta)
                                                                           ),
                                                                           max_time=simulation_params.markov_max_time,
                                                                           weight_func=simulation_params.weight_func)
                                routers = [
                                    PrioritySelfEliminationsRouter(weighted=True, beta=beta, alpha=0, k=k),
                                    # PSESubsetsRouter(weighted=True, beta=beta, alpha=0, k=k)
                                ]
                                routers.extend(simulation_params.extra_routers)

                                # routers = [PrioritySelfEliminationsRouter(weighted=True, beta=beta, alpha=alpha, k=k)
                                #            for alpha in [0.1, 0.05, 0, -0.05, -0.1]]

                                if not (beta * k).is_integer():
                                    pbar.update(simulation_params.number_of_repeats)
                                    continue

                                results_by_router = defaultdict(list)
                                for repeat in range(simulation_params.number_of_repeats):
                                    simulation = Simulation(superpackets=traffic_generator.generate_superpackets(),
                                                            beta=beta, k=k, capacity=capacity, buffer_size=buffer_size)
                                    for router in routers:
                                        res = simulation.run(router=router)
                                        results_by_router[str(router)].append(res)
                                    pbar.update(1)

                                all_results.extend([
                                    SimulationsResult(router_name=router_name, k=k, beta=beta, lam=lam,
                                                      capacity=capacity, buffer_size=buffer_size, results=results)
                                    for router_name, results in results_by_router.items()])
            rows = [r.to_dict() for r in all_results]
            df = pd.DataFrame(rows)
            all_dfs.append(df)

    for simulation_params, df in zip(simulations_params, all_dfs):
        print(df.groupby('beta')['average_burst_size'].mean())
        print(df.groupby('beta')['average_effective_load'].mean().mean())

        g = sns.relplot(x=simulation_params.x_param,
                        y=simulation_params.y_param,
                        hue="router", data=df, kind="line",
                        markers=True, dashes=False, style="router",
                        # palette=('C0', 'C4'),
                        col=simulation_params.split_by,
                        # col_wrap=(2 if simulation_params.split_by_beta else None),
                        # height=5, aspect=2,
                        facet_kws={'sharex': simulation_params.sharex}
                        )
        for ax, beta in zip(g.axes.flat, simulation_params.beta_values):
            x_label = simulation_params.x_title
            if simulation_params.split_by:
                ax_data = df[df[simulation_params.split_by] == beta]
                average_burst_size = ax_data['average_burst_size'].mean()
                average_effective_load = average_burst_size * (1 - beta)
                if simulation_params.print_average_load:
                    x_label += f"\n \u03C3\u0305 = {round(average_burst_size, 2)}, " \
                               f"\u03C3\u0303 = {round(average_effective_load, 2)}"
                else:
                    ax.set_xlim(ax_data['average_burst_size'].min(), ax_data['average_burst_size'].max())
                ax.set_title(f"\u03B2 = {round(beta, 2)}")
            print()
            ax.set_xlabel(x_label)
            ax.set_ylabel(simulation_params.y_title)
            # ax.set_ylim(bottom=0.4)

        g._legend.texts[0].set_text("")
        plt.show()


if __name__ == '__main__':
    main()
