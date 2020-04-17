#!/bin/bash

mkdir barh
mkdir scatter
mkdir event
mkdir gantt

# generate barh plots for populations in color and bw
./anim.py "data/population_edt_codes.csv" China 2018 -t "Population in 5 most populated countries (1960 - 2018)" -s -o "barh/"
./anim.py "data/population_edt_codes.csv" China 2018 -t "Population in 5 most populated countries (1960 - 2018)" -c bw -s -o "barh/"
./anim.py "data/population_edt_codes.csv" Poland 1960 -s -o "barh/"
./anim.py "data/population_edt_codes.csv" Poland 1960 -c bw -s -o "barh/"
./anim.py "data/population_edt_codes.csv" Chile 1960 -s -o "barh/"
./anim.py "data/population_edt_codes.csv" Chile 1960 -c bw -s -o "barh/"

# generate scatter (bubble) plots for populations
./anim.py "data/population_edt_codes.csv" China 2018 -t "Population in 5 most populated countries with density (1960 - 2018)" -m scatter -d "data/density_edt_codes.csv" -s -o "scatter/"
./anim.py "data/population_edt_codes.csv" Poland 1960 -m scatter -d "data/density_edt_codes.csv" -s -o "scatter/"
./anim.py "data/population_edt_codes.csv" Chile 1960 -m scatter -d "data/density_edt_codes.csv" -s -o "scatter/"

# generate linear plots for populations
./anim.py "data/population_edt_codes.csv" China 2018 -t "Population in 5 most populated countries (1960 - 2018)" -m line -s -o "line/"
./anim.py "data/population_edt_codes.csv" Poland 1960 -m line -s -o "line/"
./anim.py "data/population_edt_codes.csv" Chile 1960 -m line -s -o "line/"

# generate pie plots for populations
./anim.py "data/population_edt_codes.csv" China 2018 -t "Population % share within 5 most populated countries (1960 - 2018)" -m pie -s -o "pie/"
./anim.py "data/population_edt_codes.csv" Poland 1960 -m pie -s -o "pie/"
./anim.py "data/population_edt_codes.csv" Chile 1960 -m pie -s -o "pie/"

# generate population plot for Gulf War
./anim_select.py "data/population_edt_codes.csv" 1990 1991 "Iraq" "Saudi Arabia" "Kuwait" "Mongolia" -t "Population in countries participated in Gulf War (and Mongolia)" -s -o "event/"

# generate Gantt plots for UW calendar, manually saved to files
./gantt.py