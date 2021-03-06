#!/bin/bash

EXP_ROOT_DIR=$(pwd)

if [[ -d "$2" ]]; then
   EXP_ROOT_DIR=$(realpath "$2")
   echo "Path set to $EXP_ROOT_DIR"
   
else
   echo "Error: Second parameter needs to be the root directory of the install." >&2
   exit 2
fi

re='^[0-9]+$'
if ! [[ $1 =~ $re ]] ; then
	echo "Error: First parameter needs to be number of worker threads." >&2
	exit 1
else
	echo "Number of worker threads set to $1."
fi

echo "Initialising experimentation server"
python "$EXP_ROOT_DIR"/exp-scripts/planning-problem-server.py "$EXP_ROOT_DIR" > "$EXP_ROOT_DIR"/server.log 2>&1 &

echo "Waiting for server to start..."
sleep 3

echo "Initialising experimentation workers"
for i in $(eval echo {1..$1})
do
	"$EXP_ROOT_DIR"/exp-scripts/planning-problem-worker.py 127.0.0.1 > "$EXP_ROOT_DIR"/worker-$i.log 2>&1 &
	echo "Worker $i created"
done

