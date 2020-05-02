#!/usr/bin/env python3

import argparse
import csv

import altair as alt
import pandas as pd
import plotly.express as px
from bokeh.io import save
from bokeh.models import ColumnDataSource, HoverTool

start_year = 1960
stop_year = 2018


# return {country: {year: population}} + {country: {short name}}
def parse_file(filename: str, data_type='int') -> (dict, dict):
    countries = {}
    shorts = {}
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=';')
        for row in spamreader:
            countries[row[0]] = {start_year + i - 2: int(row[i]) if data_type == 'int' else float(row[i]) for i in
                                 range(2, len(row)) if row[i]}
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
    parser.add_argument('lib', type=str, help='mode', choices=['plotly', 'bokeh', 'altair'])
    parser.add_argument('plot', type=str, help='mode', choices=['scatter', 'line'])
    parser.add_argument('-o', '--output', type=str, help='output filename')
    args = parser.parse_args()

    data, shorts = parse_file(args.database)
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

    x = []
    y = []
    cnt = []
    for i in range(start_year, stop_year):
        for cntry in closest_5_stop:
            pop = data[cntry][i]
            x.append(i)
            y.append(pop)
            cnt.append(cntry)
    df = pd.DataFrame(dict(Year=x, Population=y, Country=cnt))

    colormap = ['red', 'green', 'blue', 'orange', 'purple']

    title = f'Population in selected countries across years ({start_year} - {stop_year})'
    ax_x_title = 'Years'
    ax_y_title = 'Population'

    if args.lib == 'plotly':
        if args.plot == 'scatter':
            fig = px.scatter(df, x="Year", y="Population", color="Country")
        elif args.plot == 'line':
            fig = px.line(df, x="Year", y="Population", color="Country")
        else:
            return
        fig.update_layout(
            title=title,
            xaxis_title=ax_x_title,
            yaxis_title=ax_y_title
        )
        if args.output:
            fig.write_html(args.output)
        else:
            fig.show()
    elif args.lib == 'bokeh':
        from bokeh.plotting import figure, output_file, show

        colors = [colormap[closest_5_stop.index(country_name)] for country_name in cnt]

        p = figure(title=title)
        p.xaxis.axis_label = ax_x_title
        p.yaxis.axis_label = ax_y_title
        hover_tool = HoverTool(
            tooltips=[
                ("Country", "@Country"),
                ("Year", "$x{(0)}"),
                ("Population", "$y{(0.00 a)}"),
            ]
        )
        p.add_tools(hover_tool)

        if args.plot == 'scatter':
            source = ColumnDataSource(data=dict(
                Year=x,
                Population=y,
                Country=cnt,
                color=colors
            ))
            p.circle('Year', 'Population', source=source, fill_color='color', fill_alpha=0.2, size=10)
        elif args.plot == 'line':
            for i, cntry in enumerate(closest_5_stop):
                pop = data[cntry]
                source = ColumnDataSource(data=dict(
                    Year=[pop_key for pop_key in pop.keys()],
                    Population=[pop_val for pop_val in pop.values()],
                    Country=[cntry for _ in range(len(pop))]
                ))
                p.line('Year', 'Population', source=source, color=colormap[i])
        else:
            return

        if args.output:
            output_file(args.output, title=title)
            save(p)
        else:
            show(p)
    elif args.lib == 'altair':
        df['Year'] = pd.to_datetime(df['Year'], format='%Y')
        if args.plot == 'scatter':
            al = alt.Chart(df, title=title).mark_circle(size=60).encode(
                x='Year',
                y='Population',
                color='Country',
                tooltip=['Year', 'Population', 'Country'],
            )
        elif args.plot == 'line':
            al = alt.Chart(df, title=title).mark_line(size=4).encode(
                x='Year',
                y='Population',
                color='Country',
                tooltip=['Year', 'Population', 'Country'],
            )
        else:
            return

        if args.output:
            alt.Chart.save(al, args.output)
        else:
            alt.Chart.show(al)


if __name__ == '__main__':
    main()
