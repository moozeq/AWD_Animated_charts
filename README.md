# Description
Creating animated gif charts for populations.

## Generate all examples

Every plot in proper folder is generated using commands from **cmds.sh** script.

```bash
./cmds.sh
```

## COVID-19 Spain charts

```bash
./spain_covid19.py
```

<html>
<body>
    <div style="text-align: center;">
        <p>
            <img src="spain_plots/0_spain_com_anim.gif" width="70%">
        </p>
    </div>
</body>
</html>

## Example usage

Creating population changes animated plot with Poland and 4 similar by population countries in 1960.

```bash
./anim.py population_edt.csv Poland 1960
```

# Examples

<html>
<body>
    <div style="text-align: center;">
        <p>
            <img src="barh/China_2018_closest_barh_color.gif" width="70%">
        </p>
        <p>
            <img src="barh/Poland_1960_closest_barh_color.gif" width="70%">
        </p>
        <p>
            <img src="barh/Chile_1960_closest_barh_color.gif" width="70%">
        </p>
        <p>
            <img src="barh/China_2018_closest_barh_bw.gif" width="70%">
        </p>
        <p>
            <img src="barh/Poland_1960_closest_barh_bw.gif" width="70%">
        </p>
        <p>
            <img src="barh/Chile_1960_closest_barh_bw.gif" width="70%">
        </p>
        <p>
            <img src="scatter/China_2018_closest_scatter_color.gif" width="70%">
        </p>
        <p>
            <img src="scatter/Poland_1960_closest_scatter_color.gif" width="70%">
        </p>
        <p>
            <img src="scatter/Chile_1960_closest_scatter_color.gif" width="70%">
        </p>
        <p>
            <img src="line/China_2018_closest_line_color.gif" width="70%">
        </p>
        <p>
            <img src="line/Poland_1960_closest_line_color.gif" width="70%">
        </p>
        <p>
            <img src="line/Chile_1960_closest_line_color.gif" width="70%">
        </p>
        <p>
            <img src="pie/China_2018_closest_pie_color.gif" width="70%">
        </p>
        <p>
            <img src="pie/Poland_1960_closest_pie_color.gif" width="70%">
        </p>
        <p>
            <img src="pie/Chile_1960_closest_pie_color.gif" width="70%">
        </p>
        <p>
            <img src="event/gulf_war_barh_color.gif" width="70%">
        </p>
        <h4>Gantt plot for UW calendar</h4>
        <p>
            <img src="gantt/gantt_color.png" width="70%">
        </p>
        <h4>Gantt plot for UW calendar (b&w)</h4>
        <p>
            <img src="gantt/gantt_bw.png" width="70%">
        </p>
    </div>
</body>
</html>
