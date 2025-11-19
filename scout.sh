#!/bin/bash

set -e

VENV_DIR="venv"
INPUT_FILE=${1:-example_cards.list}
OUTPUT_FILE=${1:-sets_cards.md}

if [ ! -d "$VENV_DIR" ]; then
    echo "Planting a fresh Llanowar glade (virtual env)..."
    python3 -m venv "$VENV_DIR"
fi

echo "Rousing the Llanowar scouts (activating venv)..."
source "$VENV_DIR/bin/activate"

echo "Sharpening scout gear (installing dependencies)..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo "Sending scouts to map the multiverse (building cache)..."
python generate.py "$INPUT_FILE"

echo "Recording set trails in $OUTPUT_FILE..."
python convert_to_sets.py "$INPUT_FILE" "$OUTPUT_FILE"

deactivate

