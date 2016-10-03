#!/bin/bash

date_start=$(date)
now_start=$(date +%s)
echo $date_start: Expermient Started

ls /mnt/data/problems/*.PDDL | parallel --gnu -j 1 /mnt/data/bin/CEIScripts/exp-scripts/processProblem.py

date_end=$(date)
now_end=$(date +%s)
runtime=$( echo "$now_end - $now_start" | bc -l )
echo $date_end: Experiment Completed
echo Runtime: $runtime seconds.ch