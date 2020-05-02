#!/usr/bin/env bash

countries="Poland Chile Denmark Ukraine China Finland"
dir="plots/"
mkdir $dir

libs="plotly bokeh altair"
for lib in $libs; do
  mkdir ${dir}${lib}
done

for cnt in $countries; do
  echo "[*] Generating charts for $cnt"
  lib="plotly"
  ./inter.py data/population_edt_codes.csv $cnt 1960 plotly line -o ${dir}${lib}/line_${cnt}.html
  ./inter.py data/population_edt_codes.csv $cnt 1960 plotly scatter -o ${dir}${lib}/scatter_${cnt}.html
  echo "[+] plotly"
  lib="bokeh"
  ./inter.py data/population_edt_codes.csv $cnt 1960 bokeh line -o ${dir}${lib}/line_${cnt}.html
  ./inter.py data/population_edt_codes.csv $cnt 1960 bokeh scatter -o ${dir}${lib}/scatter_${cnt}.html
  echo "[+] bokeh"
  lib="altair"
  ./inter.py data/population_edt_codes.csv $cnt 1960 altair line -o ${dir}${lib}/line_${cnt}.html
  ./inter.py data/population_edt_codes.csv $cnt 1960 altair scatter -o ${dir}${lib}/scatter_${cnt}.html
  echo "[+] altair"
done