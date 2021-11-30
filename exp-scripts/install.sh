#!/bin/bash

EXP_ROOT_DIR=$(pwd)

if [[ -d "$1" ]]; then
   EXP_ROOT_DIR=$(realpath "$1")
   echo "Path set to $EXP_ROOT_DIR"
   
else
   echo "Error: Parameter needs to be the root directory of the install." >&2
   exit 1
fi

echo "Creating pyton virtual environment"
python3 -m venv "$EXP_ROOT_DIR"/exp-scripts
echo "Activating environment"
source "$EXP_ROOT_DIR"/exp-scripts/bin/activate
echo "Installing required python3 packages"
python3 -m pip install -r "$EXP_ROOT_DIR"/exp-scripts/requirements.txt
echo "Deactivating environment"
deactivate
echo "Complete."




