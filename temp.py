#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import math

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


def load_and_filter(database: str) -> list:
    clean_db_path = f'{database[:-len("csv")]}_clean.csv'
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


def main(args):
    temps = load_and_filter(args.database)
    fig, ax = plt.subplots(figsize=(10, 6))
    if args.grid:
        ax.grid(b=True, which='major', linestyle='-')
    if args.mode == 'scatter':
        ax.set_axisbelow(True)
        plt.ylabel('AverageTemperatureCelsius', labelpad=8, fontdict={'size': 22})
        plt.xlabel('year', labelpad=6, fontdict={'size': 22})
        years = [int(record.year) for record in temps]
        temp_points = [record.AverageTemperatureCelsius for record in temps]
        ax.scatter(years, temp_points, facecolors=args.facecolors, edgecolors=args.edgecolors, alpha=args.alpha)
    elif args.mode in ['boxplot', 'violin']:
        countries_temps = {}
        plt.ylabel('AverageTemperatureCelsius', labelpad=8, fontdict={'size': 22})
        plt.xlabel('country_id', labelpad=6, fontdict={'size': 22})
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

    plt.savefig(args.output)
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('database', type=str)
    parser.add_argument('mode', type=str, choices=['scatter', 'boxplot', 'violin'])
    parser.add_argument('-f', '--facecolors', type=str, default='none')
    parser.add_argument('-e', '--edgecolors', type=str, default='black')
    parser.add_argument('-g', '--grid', action='store_true')
    parser.add_argument('-p', '--points', action='store_true')
    parser.add_argument('-a', '--alpha', type=float, default=1)
    parser.add_argument('-o', '--output', type=str, default='fig')
    parsed_args = parser.parse_args()

    main(parsed_args)
