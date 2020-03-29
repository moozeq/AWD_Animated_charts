#!/usr/bin/env python3

import argparse
import csv
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import transforms
from matplotlib.animation import FuncAnimation
import matplotlib.ticker as ticker

# plt.style.use('greyscale')

start_year = 1960
stop_year = 2018


# return {country: {year: population}} + {country: {short name}}
def parse_file(filename: str, data_type='int') -> (dict, dict):
    countries = {}
    shorts = {}
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            countries[row[0]] = {start_year + i - 2: int(row[i]) if data_type == 'int' else float(row[i]) for i in range(2, len(row)) if row[i]}
            shorts[row[0]] = row[1]
    return countries, shorts


def pick_5_closest(country: str, data: dict, year: int):
    countries = {country: data[country][year] for country in data if year in data[country]}
    countries = {k: v for k, v in sorted(countries.items(), key=lambda item: item[1])}
    countries_names = list(countries.keys())
    countries_pop = list(countries.values())
    country_idx = countries_names.index(country)
    country_pop = countries_pop[country_idx]
    closest = {country: 0}

    for i in range(1, 5):
        up = countries_pop[country_idx + i] if country_idx + i < len(countries_pop) else 0
        up_name = countries_names[country_idx + i] if country_idx + i < len(countries_names) else ''
        down = countries_pop[country_idx - i] if country_idx - i >= 0 else 0
        down_name = countries_names[country_idx - i] if country_idx - i >= 0 else ''
        if up_name:
            closest[up_name] = abs(country_pop - up)
        if down_name:
            closest[down_name] = abs(country_pop - down)

    closest = {k: v for k, v in sorted(closest.items(), key=lambda item: item[1])}
    closest_5 = [k for k in list(closest.keys())[:5]]
    closest_5_sorted = {k: data[k][year] for k in closest_5}
    closest_5_sorted = {k: v for k, v in sorted(closest_5_sorted.items(), key=lambda item: item[1], reverse=True)}
    return list(closest_5_sorted.keys())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('database', type=str)
    parser.add_argument('country', type=str, help='selected country')
    parser.add_argument('year', type=int, help='selected year')
    parser.add_argument('-t', '--title', type=str, help='title')
    parser.add_argument('-m', '--mode', type=str, help='mode: barh, scatter, line', default='barh')
    parser.add_argument('-c', '--color', type=str, help='color: color, bw', default='color')
    parser.add_argument('-s', '--save', action='store_true', help='save plot', default=False)
    parser.add_argument('-d', '--density', type=str, help='density data filename')
    args = parser.parse_args()

    data, shorts = parse_file(args.database)
    if args.density:
        density_data, density_shorts = parse_file(args.density, 'float')
    not_countries = [
        'World',
        'IDA & IBRD total',
        'Low & middle income',
        'Middle income',
        'IBRD only',
        'Upper middle income',
        'Late-demographic dividend',
        'East Asia & Pacific',
        'Early-demographic dividend',
        'Lower middle income',
        'East Asia & Pacific (excluding high income)',
        'East Asia & Pacific (IDA & IBRD countries)',
        'OECD members',
        'High income',
        'Post-demographic dividend',
        'Europe & Central Asia',

        'South Asia',
        'South Asia (IDA & IBRD)',
        'European Union',
        'IDA total',
        'Europe & Central Asia (IDA & IBRD countries)',
        'Europe & Central Asia (excluding high income)',
        'Euro area',
        'IDA only',
        'Least developed countries: UN classification',
        'Sub-Saharan Africa',

        'Sub-Saharan Africa (IDA & IBRD countries)',
        'Sub-Saharan Africa (excluding high income)',
        'Latin America & Caribbean',
        'Latin America & the Caribbean (IDA & IBRD countries)',
        'Latin America & Caribbean (excluding high income)',
        'North America',
        'Pre-demographic dividend',

        'Heavily indebted poor countries (HIPC)',
        'Low income',
        'IDA blend',
        'Fragile and conflict affected situations',

        'Middle East & North Africa',
        'Middle East & North Africa (excluding high income)',
        'Middle East & North Africa (IDA & IBRD countries)',

        'Arab World',
        'Central Europe and the Baltics',

    ]

    for ncount in not_countries:
        if ncount in data:
            del data[ncount]

    closest_5_start = pick_5_closest(args.country, data, args.year)
    countries_5_closest_data = {country: data[country] for country in closest_5_start}
    closest_5_stop = pick_5_closest(args.country, countries_5_closest_data, stop_year)

    font = {'size': 22}

    convert_dict = {'United States': 'USA', 'Egypt, Arab Rep.': 'Egypt', 'Venezuela, RB': 'Venezuela',
                    'Russian Federation': 'Russia'}

    plt.rc('font', **font)
    fig, ax = plt.subplots(figsize=(15, 8))

    countries_names = [convert_dict.get(country_name, country_name) for country_name in closest_5_stop]
    countries_shorts = [shorts[country_name] for country_name in closest_5_stop]

    def billions(x, pos):
        return '%1.1fB' % (x * 1e-9)

    def millions(x, pos):
        return '%1.1fM' % (x * 1e-6)

    max_x = 1.1 * data[closest_5_stop[0]][stop_year]

    formatter = ticker.FuncFormatter(millions if max_x < 300000000 else billions)

    def init():
        return ax

    def animate(i):
        ax.clear()
        plt.title(
            f'Population in similar to {args.country} in {args.year} countries ({start_year} - {stop_year})' if not args.title else args.title,
            pad=20)
        pop = [data[cntry][start_year + i] for cntry in closest_5_stop]
        if args.mode == 'barh':
            plt.xlabel('Population')
            ax.set_xlim(0, 1.1 * data[closest_5_stop[0]][stop_year])
            ax.xaxis.set_major_formatter(formatter)
            ax.tick_params(axis='x', which='minor', direction='out', bottom=True, length=5)
            ax.text(0.75, 0.82, f'{(start_year + i) % (stop_year + 1)}', transform=ax.transAxes, size=44)
            if args.color == 'color':
                ax.barh(countries_names, pop, color='royalblue')
            elif args.color == 'bw':
                ax.barh(countries_names, pop, color='white', edgecolor='black', hatch='*')
            else:
                raise Exception('Wrong color')
            for j, country_name in enumerate(closest_5_stop):
                value = pop[j] + 0.01 * 1.1 * data[closest_5_stop[0]][stop_year]
                short = countries_shorts[j]
                ax.text(value, j, short)
        elif args.mode == 'pie':
            ax.text(-0.2, 0.82, f'{(start_year + i) % (stop_year + 1)}', transform=ax.transAxes, size=44)
            ax.pie(pop, labels=countries_names, autopct='%1.1f%%')
        elif args.mode == 'scatter':
            plt.ylabel('Population')
            dens = [density_data[cntry][start_year + i] * 20 for cntry in closest_5_stop]
            ax.set_ylim(0, 1.1 * data[closest_5_stop[0]][stop_year])
            ax.set_xlim(start_year, stop_year + 2)
            ax.yaxis.set_major_formatter(formatter)
            ax.set_xticks([year for year in range(start_year, stop_year + 2)], minor=True)
            ax.text(0.1, 0.82, f'{(start_year + i) % (stop_year + 1)}', transform=ax.transAxes, size=44)
            ax.scatter([start_year + i for _ in range(5)], pop, s=dens, alpha=0.3, c=['red', 'orange', 'purple', 'blue', 'green'])
            for j, country_name in enumerate(closest_5_stop):
                value = pop[j]
                short = countries_shorts[j]
                dx, dy = np.sqrt(dens[j] * 10) / fig.dpi / 2 + 10 / fig.dpi, 0.
                offset = transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
                ax.text(start_year + i, value, short, va='center', ha='left', transform=ax.transData + offset)
        elif args.mode == 'line':
            plt.ylabel('Population')
            ax.set_ylim(0, 1.1 * data[closest_5_stop[0]][stop_year])
            ax.set_xlim(start_year, stop_year + 2)
            ax.yaxis.set_major_formatter(formatter)
            ax.set_xticks([year for year in range(start_year, stop_year + 2)], minor=True)
            ax.text(0.1, 0.82, f'{(start_year + i) % (stop_year + 1)}', transform=ax.transAxes, size=44)

            # first must be present to connect lines
            prev = cpop = [data[cntry][start_year] for cntry in closest_5_stop]
            if i == 0:  # only when first frame
                ax.scatter([start_year for _ in range(5)], cpop, c=['red', 'orange', 'purple', 'blue', 'green'])

            for j in range(start_year + 1, start_year + i):
                colors = ['red', 'orange', 'purple', 'blue', 'green']
                cpop = [data[cntry][j] for cntry in closest_5_stop]
                if j == start_year + i - 1:
                    ax.scatter([j for _ in range(5)], cpop, c=colors)
                for k in range(5):
                    ax.plot([j - 1, j], [prev[k], cpop[k]], colors[k])
                prev = cpop
            for j, country_name in enumerate(closest_5_stop):
                value = pop[j]
                short = countries_shorts[j]
                dx, dy = 1 / fig.dpi / 2 + 10 / fig.dpi, 0.
                offset = transforms.ScaledTranslation(dx, dy, fig.dpi_scale_trans)
                ax.text(start_year + i, value, short, va='center', ha='left', transform=ax.transData + offset)
        else:
            raise Exception('Wrong mode')
        return ax

    anim = FuncAnimation(fig, animate, init_func=init,
                         frames=stop_year - start_year + 1, interval=200, blit=False)
    plt.show()
    if args.save:
        anim.save(f'{args.country}_{args.year}_closest_{args.mode}_{args.color}.gif', writer='imagemagick')


if __name__ == '__main__':
    main()
