#!/usr/bin/env python3
import json
import sys
from pathlib import Path

from scout_utils import (
    BASIC_LANDS,
    CACHE_DIR,
    get_card_name,
    get_card_quantity,
)


def load_printings(card_name):
    cache_file = CACHE_DIR / f"{card_name.replace('/', '_')}_printings.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_to_sets.py <cards_list> <output_file>")
        sys.exit(1)
    
    cards_list_file = sys.argv[1]
    output_file = sys.argv[2]
    
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
            print(f"Llanowar scouts already know every {card_name}; skipping.")
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
    
    output_lines = ["# Sets", ""]
    
    for set_name in sorted(sets_to_cards.keys()):
        cards = sorted(sets_to_cards[set_name])
        output_lines.append(f"{set_name}:")
        output_lines.append("")
        for card in cards:
            output_lines.append(f"* {card}")
        output_lines.append("")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
        f.write('\n')
    
    print(f"Llanowar scouts cataloged {len(sets_to_cards)} set entries")
    print(f"Field notes compiled in {output_file}")


if __name__ == "__main__":
    main()

