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
    years = mdates.YearLocator()  # every year
    months = mdates.MonthLocator()  # every month
    months_fmt = mdates.DateFormatter('%m')
    years_fmt = mdates.DateFormatter('%Y')
    fig, ax = plt.subplots(figsize=(15, 8))

    # plt.title(f'Gantt plot for UW calendar', pad=20)
    # format the ticks
    ax.xaxis.set_major_locator(years)
    ax.xaxis.set_major_formatter(years_fmt)
    ax.xaxis.set_minor_locator(months)
    ax.xaxis.set_minor_formatter(months_fmt)

    # round to nearest years.
    datemin = datetime.date(day=1, month=10, year=2019)
    datemax = datetime.date(day=1, month=11, year=2020)
    ax.set_xlim(datemin, datemax)

    # format the coords message box
    ax.format_xdata = mdates.DateFormatter('%d.%m.%Y')
    ax.grid(b=True, which='major', linestyle='-')
    ax.grid(b=True, which='minor', linestyle='-')
    ax.set_axisbelow(True)
    ax.get_yaxis().set_visible(False)

    tasks = [
        GTask('Winter semester', '01.10.2019', '22.02.2020', 'purple'),
        GTask('Classes', '02.10.2019', '17.01.2020'),
        GTask('1st round of registration', '01.12.2019', '30.12.2019', 'orange'),
        GTask('Deadline for resignation', '17.01.2020', '18.01.2020', 'orange'),
        GTask('Winter holidays', '23.12.2019', '06.01.2020', 'green'),
        GTask('Winter examination session', '28.01.2020', '08.02.2020', 'red'),
        GTask('Language exams', '28.01.2020', '29.01.2020', 'red'),
        GTask('Inter-semester break', '10.02.2020', '16.02.2020', 'green'),
        GTask('Resit winter examination session', '17.02.2020', '22.02.2020', 'red'),

        GTask('Summer semester', '24.02.2020', '30.09.2020', 'purple'),
        GTask('Classes', '24.02.2020', '10.06.2020'),
        GTask('Spring holidays', '09.04.2020', '14.04.2020', 'green'),
        GTask('Juwenalia', '08.05.2020', '09.05.2020', 'green'),
        GTask('Deadline for resignation', '01.06.2020', '02.06.2020', 'orange'),
        GTask('1st round of registration', '01.06.2020', '30.06.2020', 'orange'),
        GTask('Summer examination session', '15.06.2020', '27.06.2020', 'red'),
        GTask('Language exams', '15.06.2020', '16.06.2020', 'red'),
        GTask('Summer holidays', '29.06.2020', '30.08.2020', 'green'),
        GTask('Resit summer examination session', '31.08.2020', '12.09.2020', 'red'),
        GTask('Individuals decisions', '14.09.2020', '30.09.2020', 'orange'),
    ]

    trans_color = {
        'lightblue': '///',
        'purple': '--',
        'orange': '...',
        'green': '',
        'red': 'xxx',
    }

    for i, task in enumerate(tasks):
        if not color:
            ax.broken_barh(task.barh, (i - 0.4, 0.8), color='white', edgecolor='black')
        else:
            ax.broken_barh(task.barh, (i - 0.4, 0.8), facecolor=task.color)

        ax.text(task.start + (task.stop - task.start) / 2, i, task.name, va='center', ha='center')

    plt.show()


if __name__ == '__main__':
    main()
