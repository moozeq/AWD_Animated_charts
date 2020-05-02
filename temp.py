#!/usr/bin/env python3

import argparse
import csv
import statistics
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import numpy as np
import math

from matplotlib.ticker import AutoMinorLocator

old_headers = [
    "record_id",
    "month",
    "day",
    "year",
    "AverageTemperatureFahr",
    "AverageTemperatureUncertaintyFahr",
    "City",
    "country_id",
    "Country",
    "Latitude",
    "Longitude"
]

new_headers = [
    "record_id",
    "month",
    "year",
    "City",
    "country_id",
    "Country",
    "Latitude",
    "Longitude",
    "AverageTemperatureCelsius",
    "AverageTemperatureUncertaintyCelsius",
]


class Record(object):
    def __init__(self, data: list, headers):
        if len(data) != len(headers):
            raise Exception('wrong data')
        for i in range(len(headers)):
            self.__dict__[headers[i]] = data[i]

    def convert_temps(self):
        self.record_id = int(self.record_id)
        self.__dict__['AverageTemperatureCelsius'] = round((float(self.AverageTemperatureFahr) - 32.0) * (5 / 9), 4)
        self.__dict__['AverageTemperatureUncertaintyCelsius'] = round(
            (float(self.AverageTemperatureUncertaintyFahr) - 32.0) * (5 / 9), 4)
        del self.AverageTemperatureFahr
        del self.AverageTemperatureUncertaintyFahr
        if 'day' in self.__dict__:
            del self.day


class Data(object):
    def __init__(self, records: List[Record]):
        self.records = records
        self.years = {}
        for record in records:
            year = int(record.year)
            if year in self.years:
                self.years[year].append(record)
            else:
                self.years[year] = [record]
        self.temps = {
            int(year): [
                record.AverageTemperatureCelsius
                for record in self.years[int(year)]
            ]
            for year in self.years
        }
        self.temps = {k: self.temps[k] for k in sorted(self.temps)}
        self.temps_years = [k for k in self.temps for _ in sorted(self.temps[k])]
        self.temps_values = [temp for k in self.temps for temp in sorted(self.temps[k])]
        self.means = {
            int(year): statistics.mean([
                record.AverageTemperatureCelsius
                for record in self.years[int(year)]
            ])
            for year in self.years
        }
        self.means = {k: self.means[k] for k in sorted(self.means)}
        self.min_temp = min(self.means.values())
        self.max_temp = max(self.means.values())
        self.min_year = min(self.means.keys())
        self.max_year = max(self.means.keys())


class CityData(Data):
    i = 0
    map = None

    def __init__(self, records: List[Record]):
        Data.__init__(self, records)
        self.name = records[0].City
        self.color = CityData.map(CityData.i)
        CityData.i += 1


class CountryData(Data):
    i = 0
    map = None

    def __init__(self, records: List[Record]):
        Data.__init__(self, records)
        self.name = records[0].Country
        self.color = CountryData.map(CountryData.i)
        CountryData.i += 1
        self.cities = {record.City for record in records}


def load_and_filter(database: str) -> list:
    clean_db_path = f'{database[:-len(".csv")]}_clean.csv'
    if Path(clean_db_path).exists():
        with open(clean_db_path, 'r') as temp_file:
            spamreader = csv.reader(temp_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            next(spamreader)
            temps = [Record(temp_line, new_headers) for temp_line in spamreader]
            return temps

    with open(database, 'r') as temp_file:
        spamreader = csv.reader(temp_file, delimiter=',')
        next(spamreader)
        temps = [Record(temp_line, old_headers) for temp_line in spamreader]
    temps = [record for record in temps if record.record_id != -1]
    temps = [
        record
        for record in temps
        if record.City and record.City != 'NA' and
           record.Country and record.Country != 'NA' and
           record.AverageTemperatureFahr != 'NA' and
           record.AverageTemperatureUncertaintyFahr != 'NA'
    ]
    for record in temps:
        record.convert_temps()

    with open(clean_db_path, 'w') as temp_out_file:
        writer = csv.writer(temp_out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(new_headers)
        for record in temps:
            writer.writerow(list(record.__dict__.values()))

    return temps


def init_countries(temps):
    countries_recs = {}
    for record in temps:
        if record.country_id in countries_recs:
            countries_recs[record.country_id].append(record)
        else:
            countries_recs[record.country_id] = [record]
    CountryData.map = plt.cm.get_cmap('hsv', len(countries_recs))
    return countries_recs


def init_cities(temps):
    cities_recs = {}
    for record in temps:
        if record.City in cities_recs:
            cities_recs[record.City].append(record)
        else:
            cities_recs[record.City] = [record]
    CityData.map = plt.cm.get_cmap('hsv', len(cities_recs))
    return cities_recs


def get_countries_grouped(temps):
    countries_recs = init_countries(temps)
    countries_grouped = [CountryData(records) for records in countries_recs.values()]
    countries_grouped = {country.name: country for country in countries_grouped}
    return countries_grouped


def get_cities_grouped(temps):
    cities_recs = init_cities(temps)
    cities_grouped = [CityData(records) for records in cities_recs.values()]
    cities_grouped = {city.name: city for city in cities_grouped}
    return cities_grouped


def show_grid(ax):
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.yaxis.set_minor_locator(AutoMinorLocator())
    ax.grid(b=True, which='major', linestyle='-')
    ax.grid(b=True, which='minor', linestyle='-', alpha=0.2)


def main(args):
    temps = load_and_filter(args.database)
    font_dict = {'size': 16} if not args.bigformat else {'size': 20}
    if args.mode not in ['grid']:
        fig, ax = plt.subplots(figsize=(10, 6))
        if args.grid:
            show_grid(ax)
        if args.mode == 'scatter':
            ax.set_axisbelow(True)
            plt.ylabel('AverageTemperatureCelsius', labelpad=8, fontdict=font_dict)
            plt.xlabel('year', labelpad=6, fontdict=font_dict)
            years = [int(record.year) for record in temps]
            temp_points = [record.AverageTemperatureCelsius for record in temps]
            ax.scatter(years, temp_points, facecolors=args.facecolors, edgecolors=args.edgecolors, alpha=args.alpha)
        elif args.mode in ['boxplot', 'violin']:
            countries_temps = {}
            plt.ylabel('AverageTemperatureCelsius', labelpad=8, fontdict=font_dict)
            plt.xlabel('country_id', labelpad=6, fontdict=font_dict)
            for record in temps:
                if record.country_id in countries_temps:
                    countries_temps[record.country_id].append(record.AverageTemperatureCelsius)
                else:
                    countries_temps[record.country_id] = [record.AverageTemperatureCelsius]

            if args.mode == 'boxplot':
                if args.points:
                    for i, country_id in enumerate(countries_temps):
                        y = countries_temps[country_id]
                        x = np.random.normal(1 + i, 0.08, size=len(y))
                        ax.plot(x, y, 'r.', alpha=0.2)

                boxplot_dict = ax.boxplot(list(countries_temps.values()), patch_artist=True,
                                          labels=list(countries_temps.keys()),
                                          medianprops={'linestyle': '-', 'linewidth': 2, 'color': 'black'})
                for b in boxplot_dict['boxes']:
                    # b.set_alpha(args.alpha)
                    b.set_edgecolor('black')
                    b.set_facecolor((1.0, 1.0, 1.0, args.alpha))
                    b.set_linewidth(1)
            elif args.mode == 'violin':
                plt.xticks(np.arange(1, len(countries_temps) + 1), tuple(countries_temps.keys()))
                ax.violinplot(list(countries_temps.values()))
        elif args.mode == 'time':
            plt.ylabel('countryAverage', labelpad=8, fontdict=font_dict)
            plt.xlabel('year', labelpad=6, fontdict=font_dict)

            countries_grouped = get_countries_grouped(temps)
            if args.grouped:
                for country_data in countries_grouped.values():
                    ax.plot(list(country_data.means.keys()), list(country_data.means.values()),
                            color=country_data.color if args.edgecolors == 'color-graph' else args.edgecolors,
                            label=country_data.name)
                if args.edgecolors == 'color-graph':
                    # Shrink current axis by 20%
                    box = ax.get_position()
                    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

                    # Put a legend to the right of the current axis
                    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            else:
                all_data = {}
                for country_data in countries_grouped.values():
                    for year, avg in country_data.means.items():
                        if year in all_data:
                            all_data[year].append(avg)
                        else:
                            all_data[year] = [avg]
                all_data = {k: all_data[k] for k in sorted(all_data)}
                temps_years = [k for k in all_data for _ in sorted(all_data[k])]
                temps_values = [temp for k in all_data for temp in sorted(all_data[k])]
                ax.plot(temps_years, temps_values, color=args.edgecolors)
    elif args.mode == 'grid':
        cities_grouped = get_cities_grouped(temps)
        countries_grouped = get_countries_grouped(temps)

        if args.cities:
            min_temp = min([city_data.min_temp for city_data in cities_grouped.values()]) - 2
            max_temp = max([city_data.max_temp for city_data in cities_grouped.values()]) + 2
        else:
            min_temp = min([country_data.min_temp for country_data in countries_grouped.values()]) - 2
            max_temp = max([country_data.max_temp for country_data in countries_grouped.values()]) + 2

        min_years = min([country_data.min_year for country_data in countries_grouped.values()]) - 10
        max_years = max([country_data.max_year for country_data in countries_grouped.values()]) + 10
        n = math.ceil(math.sqrt(len(countries_grouped)))
        fig, axs = plt.subplots(n, n, figsize=(8.5, 6.5))
        lines = []
        legend_labels = []
        for i, country_data in enumerate(countries_grouped.values()):
            ax = axs[math.floor(i / n), i % n]
            # separate countries data to cities
            if args.cities:
                # all cities within one country plot with same color
                if not args.separate:
                    legend_labels.append(country_data.name)
                    for city in country_data.cities:
                        city = cities_grouped[city]
                        l, = ax.plot(list(city.means.keys()), list(city.means.values()),
                                     color=country_data.color if args.edgecolors == 'color-graph' else args.edgecolors,
                                     label=country_data.name)
                    lines.append(l)
                # all cities with separated colors
                else:
                    for city in country_data.cities:
                        city = cities_grouped[city]
                        l, = ax.plot(list(city.means.keys()), list(city.means.values()),
                                     color=city.color if args.edgecolors == 'color-graph' else args.edgecolors,
                                     label=city.name)
                        lines.append(l)
                        legend_labels.append(city.name)
            # only countries data
            else:
                l, = ax.plot(list(country_data.means.keys()), list(country_data.means.values()),
                             color=country_data.color if args.edgecolors == 'color-graph' else args.edgecolors,
                             label=country_data.name)
                lines.append(l)
                legend_labels.append(country_data.name)
            ax.set_title(country_data.name)
            ax.set_ylim(min_temp, max_temp)
            ax.set_xlim(min_years, max_years)
            if args.bigformat:
                for tick in ax.get_xticklabels():
                    tick.set_rotation(-45)
            if args.grid:
                show_grid(ax)

        if args.edgecolors == 'color-graph':
            # Create the legend

            legend_labels, lines = zip(*sorted(zip(legend_labels, lines), key=lambda t: t[0]))
            fig.legend(lines, legend_labels, loc="center right", borderaxespad=0.1,
                       title="Country" if not args.separate else "City")

            # Adjust the scaling factor to fit your legend text completely outside the plot
            # (smaller value results in more space being made for the legend)
            plt.subplots_adjust(right=0.8)

        for i in range(len(countries_grouped), n * n):
            fig.delaxes(axs[math.floor(i / n), i % n])

        # Hide x labels and tick labels for top plots and y ticks for right plots.
        for ax in axs.flat:
            ax.label_outer()

        if args.format or args.bigformat:
            fig.suptitle('Average temperature', fontsize=font_dict['size'] if not args.bigformat else 26,
                         fontweight='normal' if not args.bigformat else 'bold')
            fig.text(0.5, 0.04 if not args.bigformat else 0.01, 'Year of observation', ha='center', fontdict=font_dict)
            fig.text(0.04, 0.5, 'Average temperature', va='center', rotation='vertical', fontdict=font_dict)
        else:
            fig.text(0.5, 0.04, 'year', ha='center', fontdict=font_dict)
            fig.text(0.04, 0.5, 'countryAverage' if not args.cities else 'cityAverage', va='center',
                     rotation='vertical', fontdict=font_dict)
        # fig.tight_layout(pad=1.0)

    if args.output:
        plt.savefig(args.output)
    else:
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('database', type=str)
    parser.add_argument('mode', type=str, choices=['scatter', 'boxplot', 'violin', 'time', 'grid'])
    parser.add_argument('-f', '--facecolors', type=str, default='none', help='fulfill colors for plots')
    parser.add_argument('-e', '--edgecolors', type=str, default='black', help='edge colors for plots')
    parser.add_argument('-g', '--grid', action='store_true', help='show grid')
    parser.add_argument('-p', '--points', action='store_true', help='points instead of circles')
    parser.add_argument('-c', '--cities', action='store_true', help='countries will be divided into cities')
    parser.add_argument('-s', '--separate', action='store_true', help='different colors for each city on grid subplots')
    parser.add_argument('-r', '--grouped', action='store_true', help='group countries on time series plot')
    parser.add_argument('-t', '--format', action='store_true', help='format labels and suptitle')
    parser.add_argument('-b', '--bigformat', action='store_true', help='format labels and suptitle 2nd')
    parser.add_argument('-a', '--alpha', type=float, default=1, help='alpha channel for plots')
    parser.add_argument('-o', '--output', type=str, help='output filename')
    parsed_args = parser.parse_args()

    main(parsed_args)
