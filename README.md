# LlanowarSetScout (a vibe-coded mixed-set lookup)

Welcome to **LlanowarSetScout**, a tiny vibe-coded helper for Magic players who love rummaging through binders, bulk boxes, and dusty store cabinets. Feed it a list of cards and it will tell you which sets to hunt, so you can go full Llanowar scout mode in the wild.

## What it does

- Reads a simple list of cards (and desired quantities) from `example_cards.list` or any file you provide.
- Talks to the [Scryfall API](https://scryfall.com/docs/api) to discover every set those cards have been printed in.
- Caches card data locally under `scryfall_cache/` so repeat scouting is lightning fast.
- Outputs a Markdown field report (`sets_cards.md` by default) grouped by set, ready to skim on your phone while you dig through bulk loot.
- Automatically ignores the five basic lands—Llanowar scouts already know every Forest, after all.

## Requirements

- macOS / Linux shell (or anything that can run Bash)
- Python 3.10+
- `pip`
- Internet access the first time you scout new cards (to populate the cache)

Everything else (virtualenv, dependencies) is handled for you.

## Quick start

1. **Clone the repo**  
   ```bash
   git clone https://github.com/you/llanowar-set-scout.git
   cd Llanowar-Set-Scout
   ```

2. **Edit your card list**  
   The default file is `example_cards.list`. Each line looks like:
   ```
   1 Willow Elf
   3 Whispersilk Cloak
   ```

3. **Send the scouts out**  
   ```bash
   ./scout.sh
   ```
   - On first run, the scouts plant a fresh Llanowar glade (virtual environment) and sharpen their gear (install dependencies).
   - They venture into the multiverse, mapping every set trail your cards have walked, and compile their field notes into `sets_cards.md`.
   - Run `./scout.sh --help` to see the full expedition guide.
   - Add `--quiet` (or `-q`) to hush the scouts—they'll still map the trails, just without the chatter.
   - Add `--regrow` (or `-r`) to send scouts back to confirm the battlefield intel—useful when you suspect the terrain has changed.
   - Add `--chronological` (or `-c`) to organize the field notes by the passage of time (oldest sets first) instead of alphabetically.

4. **Optional: custom files and flags**  
   Pass a different card list or output file:
   ```bash
  ./scout.sh my_cards.list      # writes sets_cards.md
  ./scout.sh my_cards.list my_sets.md
  ./scout.sh -q my_cards.list   # quiet mode
  ./scout.sh -r my_cards.list   # regrow cache (force fresh data)
  ./scout.sh -c my_cards.list   # sort sets chronologically by year
   ```

> 🧝 **Note:** Once the cache has the intel, you can re-run `convert_to_sets.py` alone to regenerate the Markdown without hitting the network.

## Output

`sets_cards.md` is a Markdown document grouped by set:

```
Aetherdrift Commander (2025):

* 1 x Slagwoods Bridge

Historic Anthology 6 (2022):

* 1 x Drossforge Bridge
* 1 x Slagwoods Bridge
```

Take it with you to the shop, or drop it into a note-taking app for quick reference.

## Cache & vibe-coding notes

- Cached responses live under `scryfall_cache/` and are intentionally ignored by git (this is a vibe-coded project, so we keep it breezy).
- If you add new cards and want fresh data, just rerun `./scout.sh`; the Llanowar scouts will update the cache automatically.
- Feel free to rename things, remix scripts, or add more elf puns—this project thrives on vibes.

## Credits

- Card data courtesy of the amazing folks at [Scryfall](https://scryfall.com).
- Llanowar scouts for tirelessly mapping every booster pack trail.
- @josefnpat for making this while terribly drunk

Happy hunting, and may your bulk bins always yield glistening myr!

