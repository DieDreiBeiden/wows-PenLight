# Overmatcher

**English** · [Deutsch](README.de.md)

**Overmatch indicator for World of Warships.** When you lock onto a cruiser or a battleship,
Overmatcher shows two traffic lights right next to your crosshair:

- **Shell:** can my armour-piercing (AP) shells overmatch the target?
- **Shield:** can the target's AP overmatch me?

Hold **Alt** for a detail view: the game's own ship silhouettes, split into **bow/stern**,
**midship** and **deck**, each green (overmatch) or red (no overmatch).

<p align="center">
  <img src="docs/images/ampel.png" alt="Shell and shield in every state, standard and colour-blind palettes" width="610">
</p>

> Interface mod built on the game's official ModsAPI. Tested with the EU client,
> build 15.9.0.13357625 (Linux/Steam).

---

## Contents

- [What it shows](#what-it-shows)
- [Editions and branches](#editions-and-branches)
- [Installation](#installation)
- [Usage](#usage)
- [After a game patch](#after-a-game-patch)
- [Development](#development)
- [Repository layout](#repository-layout)
- [Data sources and credits](#data-sources-and-credits)

---

## What it shows

### The overmatch rule

A shell overmatches an armour plate when

```
calibre > 14.3 × plate thickness
```

It then penetrates the plate regardless of impact angle, even against an angled ship.
A tie does not count as overmatch.

### The traffic light

Bow/stern is the precondition; green requires midship **and** deck to be overmatched as well.
Shell (me → target) and shield (target → me) use the same colours:

| Bow/stern | Midship and deck | Colour | Shell | Shield |
|---|---|---|---|---|
| yes | both yes | Green | penetrates everywhere, even angled | the enemy gets through everywhere – dodge |
| yes | not both | Orange | aim at bow/stern | protect your bow/stern |
| no | – | Red | only a broadside is worth it | angling works |
| – | – | Grey | no target, or the target is a destroyer/carrier/submarine | |

Each state also has its own **shape**, so it can be read without relying on colour:
all segments filled = overmatch everywhere, partly filled = bow/stern only, slash = no
overmatch, empty = no target.

Only pairings of **cruisers and battleships** are rated; everything else stays grey.
A colour-blind scheme in blue/yellow/orange (Okabe-Ito palette) is available for red-green
colour vision deficiency.

### Detail view (Alt)

<img src="docs/images/detail.png" alt="Detail view: Target on top, Me below, each in a frame with label and ship name" align="right" width="210">

Holding **Alt** replaces shell and shield with two ships stacked on top of each other:

- **TARGET** on top: where my AP overmatches the target.
- **ME** below: where the target's AP overmatches me.
- Each ship sits in a dark band that fades out to the sides, with hairlines and a slightly
  lighter header. The small shell/shield icon in the header carries the colour of the big icon.
- In game the **ship silhouettes from the health bar** are coloured in: the hull is split into
  stern, midship and bow, everything above the deck line counts as deck. The silhouette gets a
  dark outline and a soft shadow, the ship name (in the game font) sits underneath.
- The image uses a drawn ship instead of the game silhouette, since no game assets are shipped.
  The same drawn ships also stand in when no silhouette is found.
- Optionally the detail view can replace the icons permanently, and it follows the
  colour-blind scheme as well.

Deliberate simplification: the citadel belt is not rated. Green means the plating is
overmatched, not a citadel hit.

<br clear="right">

---

## Editions and branches

| Branch | Requires | Settings | Moving the display |
|---|---|---|---|
| `main` | ModForge **and** TTaroModUtils | options page in TTaro Mod Config, gear button on the display | mouse (TTaro) |
| `main-standalone` | ModForge; TTaroModUtils **optional** | with TTaro as on `main`, otherwise hotkeys | with TTaro via TTaro, otherwise mouse via its own Flash part |

`main-standalone` detects TTaroModUtils automatically: ModForge mounts one of two wrappers
depending on what is installed, and `Main.py` switches its own controls off as soon as TTaro is present.

---

## Installation

**Requirements**

- [ModForge](https://github.com/AndrewTaro/ModForge) – mounts the display in battle.
- For `main` additionally [TTaroModUtils](https://github.com/AndrewTaro/TTaroModUtils);
  optional for `main-standalone`.

**Steps**

1. Close the game.
2. In the game folder, find the folder with the **highest number** under `bin/`,
   e.g. `bin/13357625/`.
   - Steam on Linux: `~/.local/share/Steam/steamapps/common/World of Warships/`
   - Windows: usually `C:\Games\World_of_Warships\`
3. Copy the contents of [`mod/res_mods/`](mod/res_mods) into `bin/<number>/res_mods/` and
   overwrite existing Overmatcher files.
4. Start the game. If `res_mods/PnFMods/Overmatcher/overmatcher_log.txt` exists afterwards,
   the mod was loaded.

More detailed notes and diagnostics (German): [`mod/README.md`](mod/README.md).

**Uninstall:** delete the Overmatcher files from `res_mods` (`PnFMods/Overmatcher/`,
`gui/unbound2/PnFMods/Overmatcher*.unbound`, `ForgeBlueprints/OvermatcherContainer.xml`,
`ModSchemas/diedreibeiden-overmatcher.schema.json`, `texts/*/overmatcher.mo`).

---

## Usage

### With TTaroModUtils

In battle, hold **Ctrl** to show the mouse cursor:

- Grab the icons and **drag** to move the display.
- The **gear** to the left of the display opens the Overmatcher page in TTaro Mod Config:
  display mode (detail on Alt / always), colours (standard / colour-blind),
  size scale, lock dragging, reset position.

### Without TTaroModUtils (`main-standalone`)

- **Drag** with the mouse: hold Ctrl, hover over shell | shield (a thin frame appears), drag.
- **Hotkeys** with **Ctrl+Alt**:

| Key | Effect |
|---|---|
| Arrow keys | move, 5 px (1 px with Shift) |
| Home | reset position |
| D | detail view: on Alt ↔ always |
| F | colours: standard ↔ colour-blind |
| + / − | size 0.5–2.0 |

Settings are stored in `World of Warships/ModPrefs/` and survive game patches.

---

## After a game patch

Armour and calibres come from the game file `content/GameParams.data` and apply to exactly one
game version. If `ships.json` does not match the running version, the mod switches itself off
(better nothing than wrong colours) and says so in its log.

```bash
# 1. Extract GameParams.data from the client with the WoWs Unpack Tool
# 2. Build the table (version as written in python.log)
python3 -I tools/gameparams.py GameParams.data ships_full.json \
    mod/res_mods/PnFMods/Overmatcher/ships.json 15,9,0,13357625
# 3. Build and test the mod
python3 -I tools/build_mod.py
python3 -m unittest discover -s tests
```

The ship silhouettes come from the game itself and follow every patch automatically.

---

## Development

| Task | Command |
|---|---|
| Tests | `python3 -m unittest discover -s tests` |
| Generate `Main.py` (from `src/overmatcher/`) | `python3 -I tools/build_mod.py` |
| Draw shell/shield icons | `python3 -I tools/make_ampel_icons.py` |
| Detail images, labels, frames | `python3 -I tools/make_detail_icons.py` |
| README images | `python3 -I tools/make_readme_images.py` |
| Texts of the TTaro options page | `python3 -I tools/make_texts.py` |
| Flash part `Main.swf` (`main-standalone`) | `tools/build_flash.py`, requirements in the file header |

- The game logic (`src/overmatcher/logic.py`) runs on Python 2.7 (client) and 3.x (tests).
- `mod/res_mods/PnFMods/Overmatcher/Main.py` is generated – edit `src/overmatcher/` instead.
- All graphics are drawn by scripts; no game assets are shipped.
- Concept, traffic-light logic and notes on the client (German): [`docs/KONZEPT.md`](docs/KONZEPT.md).

---

## Repository layout

```
mod/res_mods/                     files as they belong in bin/<build>/res_mods/
  PnFMods/Overmatcher/            Main.py (generated), ships.json, icons, (Main.swf)
  gui/unbound2/PnFMods/           Overmatcher*.unbound – the display (Unbound 2)
  ForgeBlueprints/                ModForge manifest
  ModSchemas/, texts/             options page for TTaro Mod Config
src/overmatcher/                  logic.py (traffic light), mod_main.py (client binding)
src/as3/                          Flash part for dragging without TTaro (main-standalone)
tools/                            GameParams parsing, build, icon generators
tests/                            unit tests incl. a mocked client
docs/                             concept, images
```

---

## Data sources and credits

- **Armour and calibres:** the client's `GameParams.data`, parsed with
  [`tools/gameparams.py`](tools/gameparams.py); armour material names from
  [wowsunpack](https://github.com/landaire/wowsunpack) (MIT).
- **ModsAPI and ModSDK** by Wargaming/Lesta (official documentation and `wows_library.swc`).
- **ModForge** and **TTaroModUtils** by [AndrewTaro](https://github.com/AndrewTaro): used as
  dependencies, not shipped. Their code served as reference only; nothing was copied.
- Target detection follows the pattern of XTargetTracker (Battle Expert).

Overmatcher only uses the official ModsAPI and the published interfaces of the mods above.
A licence for this repository has not been chosen yet.
