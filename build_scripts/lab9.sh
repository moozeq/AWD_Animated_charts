#!/usr/bin/env bash

countries="Poland Chile Denmark Ukraine China Finland"
dir="plots/"
mkdir $dir

libs="plotly bokeh altair"

for cnt in $countries; do
  echo "[*] Generating charts for $cnt"
  for lib in $libs; do
    scripts/inter.py data/population_edt_codes.csv $cnt 1960 $lib line -o ${dir}${lib}_line_${cnt}.html
    scripts/inter.py data/population_edt_codes.csv $cnt 1960 $lib scatter -o ${dir}${lib}_scatter_${cnt}.html
    echo "[+] $lib"
  done
done

scripts/merge_htmls.py plots -o report.html