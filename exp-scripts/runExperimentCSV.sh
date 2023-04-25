#!/bin/bash

EXP_ROOT_DIR=$(pwd)
CSV_FILE=""

re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
	echo "Error: First parameter needs to be number of worker threads." >&2
	exit 1
else
	echo "Number of worker threads set to $1."
fi

if [[ -d "$2" ]]; then
   EXP_ROOT_DIR=$(realpath "$2")
   echo "Path set to $EXP_ROOT_DIR"
   
else
   echo "Error: Second parameter needs to be the root directory of the install." >&2
   exit 2
fi

if [[ -f "$3" ]]; then
	CSV_FILE=$(realpath "$3")
	echo "Using CSV file $CSV_FILE"
else
	echo "Error: Third parameter needs to be the CSV file for experiment." >&2
	exit 3
fi

echo "Clearing ramdisk..."
rm -f /mnt/ramdisk/*

echo "Initialising experimentation server"
source "$EXP_ROOT_DIR"/exp-scripts/bin/activate
"$EXP_ROOT_DIR"/exp-scripts/bin/python3 "$EXP_ROOT_DIR"/exp-scripts/planning-problem-server.py "$EXP_ROOT_DIR" --csv "$CSV_FILE" > "$EXP_ROOT_DIR"/logs/server.log 2>&1 &

echo "Waiting for server to start..."
sleep 5

echo "Initialising experimentation workers"
for i in $(eval echo {1..$1})
do
	"$EXP_ROOT_DIR"/exp-scripts/bin/python3 "$EXP_ROOT_DIR"/exp-scripts/planning-problem-worker.py > "$EXP_ROOT_DIR"/logs/worker-$i.log 2>&1 &
	echo "Worker $i created"
done
deactivate

