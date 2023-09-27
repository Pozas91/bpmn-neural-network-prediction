import os
import pathlib
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from utils.paths import OUTPUTS_PATH, PLOTS_PATH

plot_size = 5
plt.rcParams["figure.figsize"] = (plot_size * 4, plot_size * 3)


def sort_by_name(x: tuple[str, float]):
    var_split = x[0].split(' ')
    tbc = int(var_split[0].split('=')[1])
    ci_lat = int(var_split[1].split('=')[1])

    # Sort first by TBC and later by CI/LAT
    return tbc, ci_lat


def sort_by_value(x: tuple):
    return x[-1]


def main(process_name: str = 'delivery'):
    # Get output
    process_path = OUTPUTS_PATH.joinpath(process_name)
    plots_path = PLOTS_PATH.joinpath(process_name)

    process_path.mkdir(parents=True, exist_ok=True)
    plots_path.mkdir(parents=True, exist_ok=True)

    # Define list of values
    data = {}

    # Get resources name
    resources_name = None

    # Get all directories
    for path, sub_dirs, files in os.walk(process_path):
        # Get path_to_save
        path = Path(path)

        # Get only summary files
        summary_files = list(filter(lambda f: 'summary' in f, files))
        header_files = list(filter(lambda f: 'header' in f, files))

        if len(summary_files) > 0:
            # Prepare headers
            header_file = header_files[0]

            with open(path.joinpath(header_file), 'r') as file:
                # Get content file (first line)
                content = file.readlines()[0]
                # Get only resources information
                resources_name = content.strip('\n').split('\t')[3:]

            # Prepare summary
            summary_file = summary_files[0]

            # Group data by strategy
            strategy_name: str = path.parent.name
            data_strategy = data.get(strategy_name, dict())

            tbc, ci_ps = path.name.split('-')

            # Get strategy info
            if 'predictive' in strategy_name:
                strategy_info: str = f'TBC={tbc} CI/LAT={ci_ps}'
            else:
                strategy_info: str = f'TBC={tbc} CI/LAT={ci_ps}'

            # Open file
            with open(path.joinpath(summary_file), 'r') as file:
                # Get content file (first line)
                content = file.readlines()[0]
                # Get all information
                content = content.strip('\n').split('\t')

                # Append information
                data_name = data_strategy.get('name', list())
                data_name.append(strategy_info)
                data_strategy.update({'name': data_name})

                data_avg_times = data_strategy.get('avg_time', list())
                data_avg_times.append(float(content[1]))
                data_strategy.update({'avg_time': data_avg_times})

                data_var_times = data_strategy.get('var_time', list())
                data_var_times.append(float(content[2]))
                data_strategy.update({'var_time': data_var_times})

                data_costs = data_strategy.get('cost', list())
                data_costs.append(float(content[3]))
                data_strategy.update({'cost': data_costs})

                # Save resources name
                for i, res_name in enumerate(resources_name):
                    data_resource = data_strategy.get(res_name, list())
                    data_resource.append(float(content[4 + i]))
                    data_strategy.update({res_name: data_resource})

                # Update information
                data.update({strategy_name: data_strategy})

    # for col in [*resources_name, 'avg_times', 'costs', 'objective', 'bests']:
    for col in ['bests']:
        # Plot data
        plot_data(data, col=col, path_to_save=plots_path, resources_name=resources_name)


def plot_data(data: dict, col: str, path_to_save: Path, resources_name: list[str]):
    n_cols: int = len(data.keys())

    # Get sub-plots
    fig, ax = plt.subplots(nrows=1, ncols=n_cols, sharey='all')

    # Define colors
    colors = [
        'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:olive',
        'tab:cyan', 'tab:grey'
    ]

    for j, strategy in enumerate(data.keys()):

        if col == 'objective':
            # Construct data and sort them by value
            values = objective_plot(data, strategy)
            pairs = sorted(zip(data[strategy]['name'], values), key=sort_by_name)
        elif col == 'bests':
            pairs = bests_plot(data, strategy)

            headers = list(data[strategy].keys())
            best_headers = headers.copy()
            best_headers.append('objective')
            best_headers.append('weights')

            headers.append('50/50')
            headers.append('60/40')
            headers.append('40/60')

            # Write information as CSV file
            write_in_file(
                headers=best_headers, data=pairs[3:], path_to_save=path_to_save.joinpath(f'{strategy}-best.csv')
            )
            write_in_file(
                headers=headers, data=pairs[:3], path_to_save=path_to_save.joinpath(f'{strategy}.csv')
            )

            continue
        else:
            pairs = sorted(zip(data[strategy]['name'], np.array(data[strategy][col])), key=sort_by_name)

        # Prepare indexes (doesn't mind)
        indexes = np.arange(len(pairs))

        ax[j].bar(indexes, [p[1] for p in pairs], label=[p[0] for p in pairs], color=colors)
        ax[j].set_title(strategy)
        ax[j].set_xticks([])
        ax[j].grid()

        # Reduce size to allow legend
        box = ax[j].get_position()
        ax[j].set_position([box.x0, box.y0 + box.height * .0, box.width, box.height * 1.])

    if col != 'bests':
        handles, labels = ax[4].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(.5, .25), ncol=10, fancybox=True, shadow=True)

        plt.suptitle(col.capitalize())
        plt.savefig(path_to_save.joinpath(f'{col}.png'), dpi='figure')


def write_in_file(headers: list, data: list, path_to_save: pathlib.Path):
    with open(path_to_save, 'w') as f:
        # Write headers
        f.write(','.join(headers))
        f.write('\n')
        # Write content
        content = '\n'.join(','.join(
            str(np.around(l, decimals=2)) if isinstance(l, float) else l
            for l in line
        ) for line in data)
        f.write(content)


def objective_plot(data: dict, strategy: str, c_w: float = .5):
    # Calculate normalization for cost
    all_costs: np.array = np.array([data[key]['cost'] for key in data]).reshape(-1)
    max_cost, min_cost = all_costs.max(initial=float('-inf')), all_costs.min(initial=float('inf'))
    n_costs = (max_cost - np.array(data[strategy]['cost'])) / (max_cost - min_cost)
    # Calculate normalization for time
    all_times: np.array = np.array([data[key]['avg_time'] for key in data]).reshape(-1)
    max_time, min_time = all_times.max(initial=float('-inf')), all_times.min(initial=float('inf'))
    n_times = (max_time - np.array(data[strategy]['avg_time'])) / (max_time - min_time)

    # Calculate objective function
    values = (n_costs * c_w) + (n_times * (1. - c_w))

    return np.around(values, decimals=2)


def bests_plot(data: dict, strategy: str, bests: int = 3):
    last_max_value = float('-inf')
    row_best = None

    # Search best and worst weight for each strategy
    for w in range(101):
        c_w = w / 100
        values = objective_plot(data=data, strategy=strategy, c_w=c_w)

        best_i = np.argmax(values)
        value = values[best_i]

        if value > last_max_value:
            row_best = *tuple(data[strategy][key][best_i] for key in data[strategy].keys()), value, f"{w}/{100 - w}"
            last_max_value = value

    # Get objective values
    objective_50 = objective_plot(data=data, strategy=strategy, c_w=.5)
    objective_60 = objective_plot(data=data, strategy=strategy, c_w=.6)
    objective_40 = objective_plot(data=data, strategy=strategy, c_w=.4)
    # Get in reverse order (from higher to lower)
    best_i = np.argsort(objective_50)[::-1][:bests]

    rows: list = list()
    for i in best_i:
        rows.append((
            *tuple(data[strategy][key][i] for key in data[strategy].keys()),
            objective_50[i], objective_60[i], objective_40[i]
        ))

    # Get only bests values
    return [*rows, row_best]


if __name__ == '__main__':
    main(process_name='delivery')
    main(process_name='recruitment')
    main(process_name='visa')
    exit(0)
