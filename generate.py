#!/usr/bin/env python3
import json
import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import quote

CACHE_DIR = Path("scryfall_cache")

def get_card_name(line):
    line = line.strip()
    if not line:
        return None
    parts = line.split(None, 1)
    if len(parts) > 1 and parts[0].isdigit():
        return parts[1]
    return line

def get_card_quantity(line):
    line = line.strip()
    if not line:
        return 1
    parts = line.split(None, 1)
    if len(parts) > 1 and parts[0].isdigit():
        return int(parts[0])
    return 1

def get_cached_response(card_name):
    cache_file = CACHE_DIR / f"{card_name.replace('/', '_')}_card.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_cached_response(card_name, response_data):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{card_name.replace('/', '_')}_card.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(response_data, f, indent=2, ensure_ascii=False)

def get_cached_printings(card_name):
    cache_file = CACHE_DIR / f"{card_name.replace('/', '_')}_printings.json"
    if cache_file.exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def save_cached_printings(card_name, printings_data):
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"{card_name.replace('/', '_')}_printings.json"
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(printings_data, f, indent=2, ensure_ascii=False)

def query_scryfall(card_name):
    cached = get_cached_response(card_name)
    if cached:
        return cached
    
    url = f"https://api.scryfall.com/cards/named?exact={quote(card_name)}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        save_cached_response(card_name, data)
        time.sleep(0.1)
        
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error querying {card_name}: {e}")
        return None

def get_all_printings(card_data, card_name):
    if not card_data or 'prints_search_uri' not in card_data:
        return []
    
    cached_printings = get_cached_printings(card_name)
    if cached_printings:
        return cached_printings
    
    prints_url = card_data['prints_search_uri']
    all_sets = []
    
    while prints_url:
        try:
            response = requests.get(prints_url)
            response.raise_for_status()
            data = response.json()
            
            for card in data.get('data', []):
                set_name = card.get('set_name', '')
                set_code = card.get('set', '')
                released_at = card.get('released_at', '')
                year = released_at[:4] if released_at and len(released_at) >= 4 else ''
                if set_name:
                    all_sets.append({
                        'name': set_name,
                        'code': set_code,
                        'year': year
                    })
            
            prints_url = data.get('next_page')
            if prints_url:
                time.sleep(0.1)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching printings: {e}")
            break
    
    save_cached_printings(card_name, all_sets)
    return all_sets

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} file not found")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    card_sets = {}
    card_quantities = {}
    
    for line in lines:
        card_name = get_card_name(line)
        if not card_name:
            continue
        
        quantity = get_card_quantity(line)
        card_quantities[card_name] = quantity
        
        print(f"Llanowar scouts sighted {card_name} (x{quantity})")
        
        card_data = query_scryfall(card_name)
        if not card_data:
            print(f"  Scout report: {card_name} is hiding from Scryfall intel")
            card_sets[card_name] = []
            continue
        
        sets = get_all_printings(card_data, card_name)
        set_names = []
        for s in sets:
            set_name = s['name']
            year = s.get('year', '')
            if year:
                set_names.append(f"{set_name} ({year})")
            else:
                set_names.append(set_name)
        card_sets[card_name] = set_names
        
        print(f"  Scouts mapped {len(set_names)} set trail(s)")
    
    result = {
        'cards': card_sets,
        'quantities': card_quantities
    }
    
    if output_file:
        output_path = Path(output_file)
        output_dir = output_path.parent
        if output_dir and output_dir != Path('.'):
            output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\nScout logs stored at {output_path}")
    else:
        print("\nLlanowar scouts have refreshed the cache")

if __name__ == "__main__":
    main()

