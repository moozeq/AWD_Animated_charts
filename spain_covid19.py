#!/usr/bin/env python3

import json
import math
from typing import List

import bokeh
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import datetime
import plotly.graph_objects as go

from bokeh.io import save
from bokeh.models import HoverTool, PrintfTickFormatter, Tabs, Panel
from matplotlib.animation import FuncAnimation
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as colors
import matplotlib.cm as cm

modes = ['cases', 'death', 'hosp', 'recovered']

day_min = '2020-02-21'
day_b4_max = '2020-05-18'
day_max = '2020-05-19'

start = datetime.datetime.strptime(day_min, "%Y-%m-%d")
end = datetime.datetime.strptime(day_max, "%Y-%m-%d")
date_array = [(start + datetime.timedelta(days=x)).strftime("%Y-%m-%d") for x in range(0, (end - start).days)]

days = {
    'cases': {'start': '2020-02-21', 'stop': '2020-05-18'},
    'death': {'start': '2020-03-04', 'stop': '2020-05-18'},
    'hosp': {'start': '2020-02-21', 'stop': '2020-05-18'},
    'recovered': {'start': '2020-03-09', 'stop': '2020-05-18'},
}

colormaps = {
    'cases': 'Reds',
    'death': 'Greys',
    'hosp': 'Purples',
    'recovered': 'Greens',
}

files = {
    'cases': 'covid/ccaa_covid19_casos.csv',
    'death': 'covid/ccaa_covid19_fallecidos.csv',
    'hosp': 'covid/ccaa_covid19_hospitalizados.csv',
    'recovered': 'covid/ccaa_covid19_altas.csv',
}

what = {
    'cases': 'Cases',
    'death': 'Deaths',
    'hosp': 'Hospitalized',
    'recovered': 'Recovered'
}

order = 0


def prepare_dfs(modes: List[str]):
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
    population_df = pd.read_csv('covid/population.csv')

    data_dfs = {mode: pd.read_csv(files[mode]).fillna(value=0) for mode in modes}
    map_dfs = {mode: data_dfs[mode].merge(population_df, on='cod_ine') for mode in modes}

    for mode in modes:
        day0 = days[mode]['start']
        last_day = days[mode]['stop']

        first_col = map_dfs[mode][day0]
        last_col = map_dfs[mode][last_day]

        # interpolation if data not exists
        for date in date_array:
            if date not in map_dfs[mode]:
                if date < '2020-04-15':  # interpolate data before
                    map_dfs[mode][date] = first_col
                else:  # interpolate data after
                    map_dfs[mode][date] = last_col
            map_dfs[mode][f'{date}_per'] = (map_dfs[mode][date] / map_dfs[mode]['Population']) * 100
    return map_dfs, communities_df


def prepare_df_for_day(modes: List[str], day: str):
    data_dfs, map_df = prepare_dfs(modes)
    new_dfs = {mode: map_df.merge(data_dfs[mode][['cod_ine', 'CCAA', day, f'{day}_per', 'Population']], on='cod_ine') for mode in modes}
    return new_dfs


def prepare_df_for_all(modes: List[str]):
    data_dfs, map_df = prepare_dfs(modes)
    map_dfs = {mode: map_df.merge(data_dfs[mode], on='cod_ine') for mode in modes}
    return map_dfs


def communities_interactive(modes: List[str], i_date_str: str, save_file: bool = False):
    from bokeh.io import show, output_file
    from bokeh.plotting import figure
    from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
    from bokeh.palettes import brewer
    i_date_str_per = f'{i_date_str}_per'
    map_dfs = prepare_df_for_day(modes, i_date_str)

    # Input GeoJSON source that contains features for plotting.
    geosources = {mode: GeoJSONDataSource(geojson=map_dfs[mode].to_json()) for mode in modes}

    tabs_arr = {}
    for mode in modes:
        # Define color palette.
        palette = brewer[colormaps[mode]][8]
        # Reverse color order so that dark blue is highest.
        palette = palette[::-1]
        # Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors.
        max_cnt = map_dfs[mode][i_date_str].max()
        min_cnt = map_dfs[mode][i_date_str].min()

        max_per = map_dfs[mode][i_date_str_per].max()
        min_per = map_dfs[mode][i_date_str_per].min()
        color_mapper_cnt = LinearColorMapper(palette=palette, low=min_cnt, high=max_cnt)
        color_mapper_per = LinearColorMapper(palette=palette, low=min_per, high=max_per)
        # Create color bar.
        color_bar_cnt = ColorBar(color_mapper=color_mapper_cnt, label_standoff=10, border_line_color=None, location=(0, 0))
        color_bar_per = ColorBar(color_mapper=color_mapper_per, label_standoff=10, border_line_color=None, location=(0, 0), formatter=PrintfTickFormatter(format="%0.2f%%"))
        title = f'Spain COVID-19 {what[mode]}, {i_date_str}'

        # Create figure object.
        p_con_cnt = figure(title=title, plot_height=600, plot_width=950, toolbar_location=None, x_range=(-10, 5), y_range=(35, 44))
        p_con_per = figure(title=title, plot_height=600, plot_width=950, toolbar_location=None, x_range=(-10, 5), y_range=(35, 44))
        ps = [p_con_cnt, p_con_per]

        hover_tool = HoverTool(
            tooltips=[
                ("Community", "@CCAA"),
                ("Population", f"@Population"),
                (what[mode], f"@{{{i_date_str}}}"),
                (f"% {what[mode]}", f"@{{{i_date_str_per}}}{{0.2f}}%")
            ]
        )

        for p in ps:
            p.xgrid.grid_line_color = None
            p.ygrid.grid_line_color = None
            p.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
            p.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
            p.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
            p.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
            p.xaxis.major_label_text_font_size = '0pt'  # turn off x-axis tick labels
            p.yaxis.major_label_text_font_size = '0pt'  # turn off y-axis tick labels
            p.add_tools(hover_tool)

        p_con_cnt.patches('xs', 'ys', source=geosources[mode], fill_color={'field': i_date_str, 'transform': color_mapper_cnt},
                  line_color='black', line_width=0.25, fill_alpha=1)
        p_con_per.patches('xs', 'ys', source=geosources[mode], fill_color={'field': i_date_str_per, 'transform': color_mapper_per},
                  line_color='black', line_width=0.25, fill_alpha=1)

        p_con_cnt.add_layout(color_bar_cnt, 'right')
        p_con_per.add_layout(color_bar_per, 'right')

        tabs_arr[mode] = [
            Panel(child=p_con_cnt, title=f'{what[mode]}'),
            Panel(child=p_con_per, title=f'% {what[mode]}'),
        ]

    # Display figure.
    tabs = Tabs(tabs=[tab for tabs in tabs_arr.values() for tab in tabs])
    if save_file:
        global order
        output_file(f'spain_plots/{order}_spain_com_interactive_{i_date_str}.html')
        order += 1
        save(tabs)
    else:
        show(tabs)


def communities_cases(modes: List[str], save_file: bool = False):
    map_dfs = prepare_df_for_all(modes)

    n = 2
    fig, axs = plt.subplots(2, 2, figsize=(15, 8))
    normalizes = {}
    for mode in modes:
        max_cnt = map_dfs[mode][date_array].values.max(1).max()
        min_cnt = map_dfs[mode][date_array].values.min(1).min()
        normalize = colors.Normalize(min_cnt, max_cnt)
        normalizes[mode] = normalize

    def init():
        for i, mode in enumerate(modes):
            ax = axs[math.floor(i / n), i % n]
            ax.clear()
            ax.set_xlim([-10, 5])
            ax.set_ylim([35, 44])

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
            ax.set_xlim([-10, 5])
            ax.set_ylim([35, 44])
            map_dfs[mode].plot(column=i_date_str, norm=normalizes[mode], cmap=colormaps[mode], edgecolor='k', ax=ax)
        if i == 0:
            fig.tight_layout()
        return axs

    anim = FuncAnimation(fig, animate, init_func=init, frames=len(date_array) + 40, interval=100, blit=False)
    if save_file:
        global order
        anim.save(f'spain_plots/{order}_spain_com_anim.gif', writer='imagemagick', dpi=120)
        order += 1
    else:
        plt.show()


def unemployment(save_file: bool = False):
    import plotly.express as px

    df = pd.read_csv('covid/unemployment.csv')
    fig = px.line(df, x="Date", y="Unemployment", title='Unemployment in Spain, 2018-2020')
    # fig.add_trace(go.Scatter(x=df["Date"], y=df["Unemployment"]))
    fig.update_layout(
        spikedistance=-1, hoverdistance=-1,
        yaxis=dict(
            type='linear', ticksuffix='%', showspikes=True, spikecolor="black", spikesnap="data",
            spikemode="across+marker", spikedash='longdash'
        )
    )
    if save_file:
        global order
        fig.write_html(f'spain_plots/{order}_spain_unemployment.html')
        order += 1
    else:
        fig.show()


def CPI(save_file: bool = False):
    import plotly.express as px

    df = pd.read_csv('covid/CPI.csv')
    fig = px.area(df, x="Date", y="CPI", text="CPI", title='Consumer Price Index in Spain (YoY), 2019-2020')

    fig.update_traces(textposition='top left')
    if save_file:
        global order
        fig.write_html(f'spain_plots/{order}_spain_CPI.html')
        order += 1
    else:
        fig.show()


if __name__ == '__main__':
    communities_cases(['cases', 'death', 'hosp', 'recovered'], True)
    communities_interactive(modes, day_b4_max, True)

    unemployment(True)
    CPI(True)
