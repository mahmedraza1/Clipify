#!/bin/bash

# run_python.sh - Wrapper to run Python scripts with virtual environment
# Usage: ./run_python.sh script_name.py [arguments]

VENV_DIR="$HOME/automation/venv"

# Activate virtual environment if it exists
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
fi

# Run the Python script with all arguments
python "$@"
