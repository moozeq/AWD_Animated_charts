#!/usr/bin/env bash

mkdir images

echo "Creating venv"
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt

echo "task2"
./temp.py data/temperature.csv scatter -f none -o images/task2a
./temp.py data/temperature.csv scatter -f black -g -o images/task2b
./temp.py data/temperature.csv scatter -f black -g -a 0.05 -o images/task2c
./temp.py data/temperature.csv scatter -f black -g -a 0.05 -e blue -o images/task2d

echo "task3"
./temp.py data/temperature.csv boxplot -g -o images/task3a
./temp.py data/temperature.csv boxplot -g -p -a 0 -o images/task3b
./temp.py data/temperature.csv violin -g -o images/task3c

echo "task4"
./temp.py data/temperature.csv time -g -o images/task4a
./temp.py data/temperature.csv time -gr -o images/task4b
./temp.py data/temperature.csv time -gr -e color-graph -o images/task4c

echo "task5"
./temp.py data/temperature.csv grid -g -e color-graph -o images/task5a
./temp.py data/temperature.csv grid -gc -e color-graph -o images/task5b
./temp.py data/temperature.csv grid -gc -e color-graph -o images/task5c
./temp.py data/temperature.csv grid -gcst -e color-graph -o images/task5d
./temp.py data/temperature.csv grid -gcsb -e color-graph -o images/task5e

echo "Done, images available in directory images"