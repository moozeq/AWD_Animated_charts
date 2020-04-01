#!/usr/bin/env python3
import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


color = True


class GTask(object):
    def __init__(self, name, start, stop, tcolor='lightblue'):
        self.name = name
        self.start = datetime.datetime.strptime(start, "%d.%m.%Y").toordinal()
        self.stop = datetime.datetime.strptime(stop, "%d.%m.%Y").toordinal()
        self.barh = [(self.start, self.stop - self.start)]
        self.color = tcolor


def main():
    from matplotlib.dates import WE
    years = mdates.YearLocator()
    months = mdates.MonthLocator()
    days = mdates.DayLocator()
    weekdays = mdates.WeekdayLocator(byweekday=WE)
    years_fmt = mdates.DateFormatter('%Y')
    months_fmt = mdates.DateFormatter('%m')
    wd_fmt = mdates.DateFormatter('%d.%m')
    days_fmt = mdates.DateFormatter('')
    fig, ax = plt.subplots(figsize=(15, 8))

    # format the ticks
    ax.xaxis.set_major_locator(weekdays)
    ax.xaxis.set_major_formatter(wd_fmt)
    ax.xaxis.set_minor_locator(days)
    ax.xaxis.set_minor_formatter(days_fmt)

    # round to nearest years.
    datemin = datetime.date(day=1, month=4, year=2020)
    datemax = datetime.date(day=27, month=5, year=2020)
    ax.set_xlim(datemin, datemax)

    # format the coords message box
    ax.format_xdata = mdates.DateFormatter('%d.%m.%Y')
    ax.grid(b=True, which='major', linestyle='-')
    ax.grid(b=True, which='minor', linestyle='-')
    ax.set_axisbelow(True)
    ax.xaxis.set_tick_params(labelsize='large', width=4)

    # red - JN
    # green - JS
    # blue - KD
    # orange - MK

    power_rangers = {
        'JN': 'red',
        'MK': 'blue',
        'JS': 'green',
        'KD': 'black',
        'ALL': 'purple'
    }

    import matplotlib.patches as mpatches

    ax.legend(handles=[mpatches.Patch(color=power_rangers[user], label=user) for user in power_rangers])

    tasks = [
        GTask('Project', '01.04.2020', '20.05.2020', power_rangers['ALL']),
        GTask('Project presentation', '20.05.2020', '27.05.2020', power_rangers['ALL']),
        GTask('Preparing git repositories', '01.04.2020', '08.04.2020', power_rangers['ALL']),
        GTask('Setting up IDE and environment', '01.04.2020', '08.04.2020', power_rangers['ALL']),

        # JN
        GTask('API between stages definition', '15.04.2020', '20.04.2020', power_rangers['JN']),
        GTask('Preparing first version of README', '20.04.2020', '27.04.2020', power_rangers['JN']),
        GTask('Code reviewing and merging pull requests', '20.04.2020', '14.05.2020', power_rangers['JN']),
        GTask('Preparing final README', '27.04.2020', '20.05.2020', power_rangers['JN']),
        GTask('Preparing integration tests', '27.04.2020', '20.05.2020', power_rangers['JN']),

        # JS
        GTask('Import bachelor project for downloading UniProt seqs', '15.04.2020', '20.04.2020', power_rangers['JS']),
        GTask('Implementing efficient storing and getting UniProt seqs', '20.04.2020', '24.04.2020', power_rangers['JS']),
        GTask('Preparing test input data and simple test cases', '24.04.2020', '27.04.2020', power_rangers['JS']),
        GTask('Preparing complex tests for 1st step', '27.04.2020', '07.05.2020', power_rangers['JS']),
        GTask('Integration with other steps', '27.04.2020', '14.05.2020', power_rangers['JS']),

        # KD
        GTask('Preparing input (with JS) and output (with MK) format definition', '20.04.2020', '24.04.2020', power_rangers['KD']),
        GTask('Preparing test input data and simple test cases', '24.04.2020', '27.04.2020', power_rangers['KD']),
        GTask('Preparing complex tests for 2nd step', '27.04.2020', '07.05.2020', power_rangers['KD']),
        GTask('Implementing amino-acids analyzer', '27.04.2020', '07.05.2020', power_rangers['KD']),
        GTask('Integration with other steps', '07.05.2020', '14.05.2020', power_rangers['KD']),

        # MK
        GTask('Preparing input (with KD) and output format definition', '20.04.2020', '24.04.2020', power_rangers['MK']),
        GTask('Preparing test input data and simple test cases', '24.04.2020', '27.04.2020', power_rangers['MK']),
        GTask('Preparing complex tests for 3rd step', '27.04.2020', '07.05.2020', power_rangers['MK']),
        GTask('Implementing amino-acids analyzer\'s data visualization', '27.04.2020', '07.05.2020', power_rangers['MK']),
        GTask('Integration with other steps', '07.05.2020', '14.05.2020', power_rangers['MK']),
    ]

    trans_color = {
        'lightblue': '///',
        'purple': '--',
        'orange': '...',
        'green': '',
        'red': 'xxx',
    }

    labels = [task.name for task in tasks]
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)

    my_colors = [task.color for task in tasks]

    for tick_label, tick_color in zip(plt.gca().get_yticklabels(), my_colors):
        tick_label.set_color(tick_color)

    for i, task in enumerate(tasks):
        if not color:
            ax.broken_barh(task.barh, (i - 0.4, 0.8), color='white', edgecolor='black')
        else:
            ax.broken_barh(task.barh, (i - 0.4, 0.8), facecolor=task.color, edgecolor='black')

    plt.show()


if __name__ == '__main__':
    main()
