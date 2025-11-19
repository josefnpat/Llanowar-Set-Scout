from pathlib import Path

CACHE_DIR = Path("scryfall_cache")
BASIC_LANDS = {"plains", "island", "swamp", "mountain", "forest"}

# Module-level quiet flag
QUIET = False


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


def log(message: str) -> None:
    """Print message only if not in quiet mode."""
    if not QUIET:
        print(message)


def parse_quiet_flag(args: list[str]) -> tuple[list[str], bool]:
    """Extract --quiet/-q flags from args and return remaining args + quiet bool."""
    quiet = False
    positional = []
    for arg in args:
        if arg in ("-q", "--quiet"):
            quiet = True
        else:
            positional.append(arg)
    return positional, quiet

