from pathlib import Path

CACHE_DIR = Path("scryfall_cache")
BASIC_LANDS = {"plains", "island", "swamp", "mountain", "forest"}


def get_card_name(line: str) -> str | None:
    """Extract the card name from a line like '2 Llanowar Elves'."""
    if not line:
        return None
    line = line.strip()
    if not line:
        return None
    parts = line.split(None, 1)
    if len(parts) > 1 and parts[0].isdigit():
        return parts[1]
    return line


def get_card_quantity(line: str) -> int:
    """Return the quantity prefix from a line, defaulting to 1."""
    if not line:
        return 1
    line = line.strip()
    if not line:
        return 1
    parts = line.split(None, 1)
    if len(parts) > 1 and parts[0].isdigit():
        return int(parts[0])
    return 1

