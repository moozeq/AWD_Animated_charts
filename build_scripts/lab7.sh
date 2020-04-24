#!/usr/bin/env bash

mkdir images
mkdir docs

ENV_FILE=env/bin/activate
if [[ -f "$ENV_FILE" ]]; then
    source env/bin/activate
else
    echo "No venv detected, creating new one"
    python3 -m venv env
    source env/bin/activate
    pip3 install -r scripts/requirements.txt
fi

echo "task2"
scripts/temp.py data/temperature.csv scatter -f none -o images/task2a
scripts/temp.py data/temperature.csv scatter -f black -g -o images/task2b
scripts/temp.py data/temperature.csv scatter -f black -g -a 0.05 -o images/task2c
scripts/temp.py data/temperature.csv scatter -f black -g -a 0.05 -e blue -o images/task2d

echo "task3"
scripts/temp.py data/temperature.csv boxplot -g -o images/task3a
scripts/temp.py data/temperature.csv boxplot -g -p -a 0 -o images/task3b
scripts/temp.py data/temperature.csv violin -g -o images/task3c

echo "task4"
scripts/temp.py data/temperature.csv time -g -o images/task4a
scripts/temp.py data/temperature.csv time -gr -o images/task4b
scripts/temp.py data/temperature.csv time -gr -e color-graph -o images/task4c

echo "task5"
scripts/temp.py data/temperature.csv grid -g -e color-graph -o images/task5a
scripts/temp.py data/temperature.csv grid -gc -e color-graph -o images/task5b
scripts/temp.py data/temperature.csv grid -gc -e color-graph -o images/task5c
scripts/temp.py data/temperature.csv grid -gcst -e color-graph -o images/task5d
scripts/temp.py data/temperature.csv grid -gcsb -e color-graph -o images/task5e

echo "Done, images available in directory images"

echo "Creating pdf"
scripts/images_to_pdf.py images -o docs/plots.pdf