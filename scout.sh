#!/bin/bash

set -e

VENV_DIR="venv"

print_help() {
    cat <<'EOF'
LlanowarSetScout - vibe-coded mixed set lookup

Usage:
  ./scout.sh [options] [cards_list] [output_markdown]

Examples:
  ./scout.sh                         # uses example_cards.list -> sets_cards.md
  ./scout.sh my_cards.list           # outputs to sets_cards.md
  ./scout.sh my_cards.list my_sets.md

Options:
  -h, --help         Show this help message and exit.
  -q, --quiet        Suppress scout banter (minimal output).
  -r, --regrow       Force refresh of cached Scryfall data (regrow the cache).
  -c, --chronological  Sort sets by year (oldest to newest) instead of alphabetically.

Scouts will create a virtualenv if needed, refresh the Scryfall cache,
and produce a Markdown report of sets for each card.
EOF
}

QUIET=0
REGROW=0
CHRONOLOGICAL=0
ARGS=()

for arg in "$@"; do
    case "$arg" in
        -h|--help)
            print_help
            exit 0
            ;;
        -q|--quiet)
            QUIET=1
            ;;
        -r|--regrow)
            REGROW=1
            ;;
        -c|--chronological)
            CHRONOLOGICAL=1
            ;;
        *)
            ARGS+=("$arg")
            ;;
    esac
done

INPUT_FILE=${ARGS[0]:-example_cards.list}
OUTPUT_FILE=${ARGS[1]:-sets_cards.md}

log() {
    if [ "$QUIET" -eq 0 ]; then
        echo "$@"
    fi
}

if [ ! -d "$VENV_DIR" ]; then
    log "Planting a fresh Llanowar glade (virtual env)..."
    python3 -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python3"

log "Rousing the Llanowar scouts (activating venv)..."
source "$VENV_DIR/bin/activate" || true

log "Sharpening scout gear (installing dependencies)..."
"$VENV_PYTHON" -m pip install -q --upgrade pip
"$VENV_PYTHON" -m pip install -q -r requirements.txt

log "Sending scouts to map the multiverse (building cache)..."
PYTHON_GENERATE_ARGS=("$INPUT_FILE")
if [ "$QUIET" -eq 1 ]; then
    PYTHON_GENERATE_ARGS+=("--quiet")
fi
if [ "$REGROW" -eq 1 ]; then
    PYTHON_GENERATE_ARGS+=("--regrow")
fi
"$VENV_PYTHON" generate.py "${PYTHON_GENERATE_ARGS[@]}"

log "Recording set trails in $OUTPUT_FILE..."
PYTHON_CONVERT_ARGS=("$INPUT_FILE" "$OUTPUT_FILE")
if [ "$QUIET" -eq 1 ]; then
    PYTHON_CONVERT_ARGS+=("--quiet")
fi
if [ "$CHRONOLOGICAL" -eq 1 ]; then
    PYTHON_CONVERT_ARGS+=("--chronological")
fi
"$VENV_PYTHON" convert_to_sets.py "${PYTHON_CONVERT_ARGS[@]}"

