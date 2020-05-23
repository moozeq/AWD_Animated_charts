import argparse
import math
from typing import List

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import datetime
from matplotlib.animation import FuncAnimation
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
import matplotlib.cm as cm


def communities_cases(modes: List[str], place: str = 'continent', save: bool = False):
    communities_df = gpd.read_file('covid/spain-communities.geojson')
    id_map = {
        1: 1,
        2: 2,
        3: 4,
        4: 5,
        5: 6,
        6: 8,
        7: 7,
        8: 9,
        9: 18,
        10: 11,
        11: 12,
        12: 17,
        13: 13,
        14: 19,
        15: 14,
        16: 15,
        17: 16,
        18: 3,
        19: 10,
    }

    communities_df['cod_ine'] = communities_df['cartodb_id'].map(id_map)

    files = {
        'cases': 'covid/ccaa_covid19_casos.csv',
        'death': 'covid/ccaa_covid19_fallecidos.csv',
        'hosp': 'covid/ccaa_covid19_hospitalizados.csv',
        'recovered': 'covid/ccaa_covid19_altas.csv',
    }

    data_dfs = {mode: pd.read_csv(files[mode]).fillna(value=0) for mode in modes}
    map_dfs = {mode: pd.merge(communities_df, data_dfs[mode], on='cod_ine') for mode in modes}

    day_min = '2020-02-21'
    day_max = '2020-05-21'

    days = {
        'cases': {'start': '2020-02-21', 'stop': '2020-05-21'},
        'death': {'start': '2020-03-04', 'stop': '2020-05-21'},
        'hosp': {'start': '2020-02-21', 'stop': '2020-05-21'},
        'recovered': {'start': '2020-03-09', 'stop': '2020-05-18'},
    }

    date_arrays = {}
    for mode in modes:
        day0 = days[mode]['start']
        last_day = days[mode]['stop']

        start = datetime.datetime.strptime(day_min, "%Y-%m-%d")
        end = datetime.datetime.strptime(day_max, "%Y-%m-%d")
        date_array = [(start + datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, (end - start).days)]

        first_col = map_dfs[mode][day0]
        last_col = map_dfs[mode][last_day]

        # interpolation if data not exists
        for date in date_array:
            if date not in map_dfs[mode]:
                if date < '2020-03-09':
                    map_dfs[mode][date] = first_col
                else:
                    map_dfs[mode][date] = last_col

        date_arrays[mode] = date_array

    n = 2
    fig, axs = plt.subplots(2, 2, figsize=(15, 8))

    colormaps = {
        'cases': 'Reds',
        'death': 'Greys',
        'hosp': 'Purples',
        'recovered': 'Greens',
    }
    normalizes = {}
    for mode in modes:
        max_cnt = map_dfs[mode][date_arrays[mode]].values.max(1).max()
        min_cnt = map_dfs[mode][date_arrays[mode]].values.min(1).min()
        normalize = colors.Normalize(min_cnt, max_cnt)
        normalizes[mode] = normalize

    def init():
        for i, mode in enumerate(modes):
            ax = axs[math.floor(i / n), i % n]
            ax.clear()
            if place == 'continent':
                ax.set_xlim([-10, 5])
                ax.set_ylim([35, 44])
            elif place == 'canaries':
                ax.set_xlim([-19, -13])
                ax.set_ylim([27, 30])

            ax.set_xticks([])
            ax.set_yticks([])

            divider = make_axes_locatable(ax)
            cax = divider.append_axes('right', size='5%', pad=0.05)
            scalar_mappaple = cm.ScalarMappable(norm=normalizes[mode], cmap=colormaps[mode])
            scalar_mappaple.set_array(max_cnt)
            fig.colorbar(scalar_mappaple, cax=cax)
        return axs

    def animate(i):
        # stop for 20 frames after all dates
        if i >= len(date_array):
            i_date_str = date_array[-1]
        else:
            i_date_str = date_array[i % len(date_array)]

        for k, mode in enumerate(modes):
            ax = axs[math.floor(k / n), k % n]
            ax.clear()

            titles = {
                'cases': f'Spain COVID-19 cases, {i_date_str}',
                'death': f'Spain COVID-19 deaths, {i_date_str}',
                'hosp': f'Spain COVID-19 hospitalized, {i_date_str}',
                'recovered': f'Spain COVID-19 recovered, {i_date_str}',
            }
            ax.set_title(titles[mode], pad=20, fontsize=20)
            ax.set_xticks([])
            ax.set_yticks([])
            if place == 'continent':
                ax.set_xlim([-10, 5])
                ax.set_ylim([35, 44])
            elif place == 'canaries':
                ax.set_xlim([-19, -13])
                ax.set_ylim([27, 30])
            map_dfs[mode].plot(column=i_date_str, norm=normalizes[mode], cmap=colormaps[mode], edgecolor='k', ax=ax)
        if i == 0:
            fig.tight_layout()
        return axs

    anim = FuncAnimation(fig, animate, init_func=init, frames=len(date_arrays['cases']) + 40, interval=100, blit=False)
    if save:
        anim.save(f'spain_com_all_{place}.gif', writer='imagemagick', dpi=120)
    else:
        plt.show()


if __name__ == '__main__':
    communities_cases(['cases', 'death', 'hosp', 'recovered'], 'continent', True)
    communities_cases(['cases', 'death', 'hosp', 'recovered'], 'canaries', True)
    communities_cases(['cases', 'death', 'hosp', 'recovered'], 'all', True)
