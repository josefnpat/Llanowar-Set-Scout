#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from scout_utils import (
    BASIC_LANDS,
    CACHE_DIR,
    get_card_name,
    get_card_quantity,
    log,
    parse_convert_flags,
    QUIET,
    CHRONOLOGICAL,
)


def load_printings(card_name):
    cache_file = CACHE_DIR / f"{card_name.replace('/', '_')}_printings.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def main():
    import scout_utils
    positional, quiet, chronological = parse_convert_flags(sys.argv[1:])
    scout_utils.QUIET = quiet
    scout_utils.CHRONOLOGICAL = chronological
    if len(positional) < 2:
        print("Usage: python convert_to_sets.py <cards_list> <output_file> [--quiet] [-c|--chronological]")
        sys.exit(1)
    cards_list_file = positional[0]
    output_file = positional[1]
    
    if not Path(cards_list_file).exists():
        print(f"Error: {cards_list_file} file not found")
        sys.exit(1)
    
    with open(cards_list_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    sets_to_cards = {}
    missing_cache = []
    
    for line in lines:
        card_name = get_card_name(line)
        if not card_name:
            continue
        if card_name.lower() in BASIC_LANDS:
            log(f"Llanowar scouts already know every {card_name}; skipping.")
            continue
        
        quantity = get_card_quantity(line)
        printings = load_printings(card_name)
        
        if not printings:
            missing_cache.append(card_name)
            continue
        
        card_display = f"{quantity} x {card_name}"
        
        for entry in printings:
            set_label = entry.get('name', '').strip()
            year = entry.get('year', '').strip()
            if not set_label:
                continue
            if year:
                set_label = f"{set_label} ({year})"
            
            sets_to_cards.setdefault(set_label, set()).add(card_display)
    
    if missing_cache:
        print("Llanowar scouts could not find cache tracks for:")
        for card in missing_cache:
            print(f"  - {card}")
        print("Send scouts out with generate.py to refresh their intel.")
    
    def get_sort_key(set_label):
        """Extract year and set name for sorting. Returns (year, set_name)."""
        if '(' in set_label and ')' in set_label:
            parts = set_label.rsplit(' (', 1)
            set_name = parts[0]
            year_str = parts[1].rstrip(')')
            try:
                year = int(year_str)
            except ValueError:
                year = 9999
        else:
            set_name = set_label
            year = 9999
        return (year, set_name)
    
    output_lines = ["# Sets", ""]
    
    if scout_utils.CHRONOLOGICAL:
        sorted_sets = sorted(sets_to_cards.keys(), key=get_sort_key)
    else:
        sorted_sets = sorted(sets_to_cards.keys())
    
    for set_name in sorted_sets:
        cards = sorted(sets_to_cards[set_name])
        output_lines.append(f"{set_name}:")
        output_lines.append("")
        for card in cards:
            output_lines.append(f"* {card}")
        output_lines.append("")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
        f.write('\n')
    
    log(f"Llanowar scouts cataloged {len(sets_to_cards)} set entries")
    log(f"Field notes compiled in {output_file}")


if __name__ == "__main__":
    main()

