#!/usr/bin/env python3
import json
import os
import sys
import time
import requests
from pathlib import Path
from urllib.parse import quote

from scout_utils import (
    BASIC_LANDS,
    CACHE_DIR,
    get_card_name,
    get_card_quantity,
    log,
    parse_flags,
    QUIET,
)
import scout_utils


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

def handle_rate_limit(response: requests.Response, retry_count: int = 0) -> bool:
    """Handle rate limit responses with exponential backoff. Returns True if should retry."""
    if response.status_code != 429:
        return False
    
    max_retries = 5
    if retry_count >= max_retries:
        print(f"  Rate limit exceeded after {max_retries} retries. Please wait and try again later.")
        return False
    
    retry_after = response.headers.get('Retry-After')
    if retry_after:
        wait_time = int(retry_after)
    else:
        wait_time = min(2 ** retry_count, 60)
    
    log(f"  Rate limited by Scryfall. Waiting {wait_time} seconds before retry {retry_count + 1}/{max_retries}...")
    time.sleep(wait_time)
    return True

def query_scryfall_batch(card_names):
    """Query multiple cards at once using Scryfall's collection endpoint."""
    if not card_names:
        return {}
    
    url = "https://api.scryfall.com/cards/collection"
    identifiers = [{"name": name} for name in card_names]
    payload = {"identifiers": identifiers}
    
    retry_count = 0
    while retry_count < 5:
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 429:
                if handle_rate_limit(response, retry_count):
                    retry_count += 1
                    continue
                else:
                    return {}
            
            response.raise_for_status()
            data = response.json()
            
            results = {}
            not_found = set(card_names)
            card_names_lower = {name.lower(): name for name in card_names}
            
            for card_data in data.get('data', []):
                returned_name = card_data.get('name', '')
                if not returned_name:
                    continue
                
                returned_lower = returned_name.lower()
                matched_original = None
                
                for query_lower, query_original in card_names_lower.items():
                    if query_lower == returned_lower or query_lower in returned_lower or returned_lower in query_lower:
                        matched_original = query_original
                        break
                
                if matched_original:
                    results[matched_original] = card_data
                    save_cached_response(matched_original, card_data)
                    not_found.discard(matched_original)
                else:
                    results[returned_name] = card_data
                    save_cached_response(returned_name, card_data)
            
            for card_name in not_found:
                log(f"  Card not found in batch: {card_name}")
            
            time.sleep(0.1)
            return results
        except requests.exceptions.RequestException as e:
            print(f"Error in batch query: {e}")
            return {}
    
    return {}

def query_scryfall(card_name):
    """Query a single card (fallback for individual queries)."""
    if not scout_utils.REGROW:
        cached = get_cached_response(card_name)
        if cached:
            return cached
    
    url = f"https://api.scryfall.com/cards/named?exact={quote(card_name)}"
    
    retry_count = 0
    while retry_count < 5:
        try:
            response = requests.get(url)
            
            if response.status_code == 429:
                if handle_rate_limit(response, retry_count):
                    retry_count += 1
                    continue
                else:
                    return None
            
            response.raise_for_status()
            data = response.json()
            
            save_cached_response(card_name, data)
            time.sleep(0.1)
            
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error querying {card_name}: {e}")
            return None
    
    return None

def get_all_printings(card_data, card_name):
    if not card_data or 'prints_search_uri' not in card_data:
        return []
    
    if not scout_utils.REGROW:
        cached_printings = get_cached_printings(card_name)
        if cached_printings:
            return cached_printings
    
    prints_url = card_data['prints_search_uri']
    all_sets = []
    
    retry_count = 0
    while prints_url:
        try:
            response = requests.get(prints_url)
            
            if response.status_code == 429:
                if handle_rate_limit(response, retry_count):
                    retry_count += 1
                    continue
                else:
                    break
            
            response.raise_for_status()
            data = response.json()
            retry_count = 0
            
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
    import scout_utils
    positional, quiet, regrow = parse_flags(sys.argv[1:])
    scout_utils.QUIET = quiet
    scout_utils.REGROW = regrow
    if not positional:
        print("Usage: python generate.py <input_file> [output_file] [--quiet] [-r|--regrow]")
        sys.exit(1)
    input_file = positional[0]
    output_file = positional[1] if len(positional) > 1 else None
    
    if regrow:
        log("Llanowar scouts are regrowing the cache from fresh seeds...")
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} file not found")
        sys.exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    card_sets = {}
    card_quantities = {}
    card_names_to_query = []
    card_name_to_line = {}
    
    for line in lines:
        card_name = get_card_name(line)
        if not card_name:
            continue
        if card_name.lower() in BASIC_LANDS:
            log(f"Scouts skip {card_name}; every Llanowar grove knows those paths.")
            continue
        
        quantity = get_card_quantity(line)
        card_quantities[card_name] = quantity
        card_name_to_line[card_name] = line
        
        if scout_utils.REGROW:
            card_names_to_query.append(card_name)
        else:
            cached = get_cached_response(card_name)
            if not cached:
                card_names_to_query.append(card_name)
    
    fresh_card_data = {}
    if card_names_to_query:
        log(f"Llanowar scouts preparing batch expedition for {len(card_names_to_query)} card(s)...")
        batch_size = 75
        batch_found = set()
        for i in range(0, len(card_names_to_query), batch_size):
            batch = card_names_to_query[i:i + batch_size]
            log(f"  Batch querying {len(batch)} card(s)...")
            batch_results = query_scryfall_batch(batch)
            fresh_card_data.update(batch_results)
            batch_found.update(batch_results.keys())
        
        for card_name in card_names_to_query:
            if card_name not in batch_found:
                if scout_utils.REGROW:
                    log(f"  Falling back to individual query for {card_name}...")
                    individual_result = query_scryfall(card_name)
                    if individual_result:
                        fresh_card_data[card_name] = individual_result
                elif not get_cached_response(card_name):
                    log(f"  Falling back to individual query for {card_name}...")
                    individual_result = query_scryfall(card_name)
                    if individual_result:
                        fresh_card_data[card_name] = individual_result
    
    for card_name in card_name_to_line.keys():
        log(f"Llanowar scouts sighted {card_name} (x{card_quantities[card_name]})")
        
        if scout_utils.REGROW:
            card_data = fresh_card_data.get(card_name)
        else:
            card_data = fresh_card_data.get(card_name) or get_cached_response(card_name)
        
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
        
        log(f"  Scouts mapped {len(set_names)} set trail(s)")
    
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
        
        log(f"\nScout logs stored at {output_path}")
    else:
        log("\nLlanowar scouts have refreshed the cache")

if __name__ == "__main__":
    main()

