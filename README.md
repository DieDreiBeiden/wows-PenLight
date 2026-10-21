# PenLight

**English** · [Deutsch](README.de.md)

*PenLight = **pen**etration + traffic **light**.*

**Overmatch and penetration indicator for World of Warships.** When you lock onto a target,
PenLight shows two small traffic lights right next to your crosshair:

- **Shell:** does my **loaded** ammunition get through the target's armour? AP is rated by
  overmatch, HE and SAP by their penetration value.
- **Shield:** can the target's AP shells overmatch my armour?

Hold **Alt** for a detail view that shows the same for each zone of both ships: bow/stern,
midship and deck.

<p align="center">
  <img src="docs/images/ampel.png" alt="Shell and shield in every state, standard and colour-blind palettes" width="610">
</p>

> Information display built on the game's official ModsAPI. It only compares static armour and
> calibre values, like the armour viewer in port – see [Fair play](#fair-play).
> Tested with the EU client, build 15.9.0.13357625 (Linux/Steam).

---

## Contents

- [What it shows](#what-it-shows)
- [Fair play](#fair-play)
- [Editions and branches](#editions-and-branches)
- [Installation](#installation)
- [Usage](#usage)
- [After a game patch](#after-a-game-patch)
- [Development](#development)
- [Repository layout](#repository-layout)
- [Data sources and credits](#data-sources-and-credits)

---

## What it shows

### Rated zones

Each ship is split into three zones: **bow/stern**, **midship** and **deck**. Which ships are
rated depends on the loaded ammunition:

- **AP** and the **shield**: only if your own ship and the target are both **cruisers or
  battleships**.
- **HE and SAP**: from destroyers, cruisers and battleships against destroyers, cruisers,
  battleships and carriers. If the pairing is not a cruiser/battleship pairing, the shield stays
  grey. Carriers are only rated as a target, submarines not at all.

Without a target, or for a pairing that is not rated, the icons stay grey.

### Overmatch (AP)

A shell overmatches an armour plate when

```
calibre > 14.3 × plate thickness
```

It then penetrates that plate at any impact angle, so angling does not help. A tie does not
count as overmatch.

### The traffic light

The colours show whether the situation is **good or bad for you**. That is why shell and shield
use opposite colours for the same result:

| Overmatch on… | Shell (my AP → target) | Shield (target's AP → me) |
|---|---|---|
| all three zones | **Green + star** – I get through everywhere, even if the target angles | **Red + warning triangle** – the target gets through everywhere, avoid its guns |
| bow/stern only | **Orange** – aim at bow/stern | **Orange** – keep your bow/stern out of its fire |
| not even bow/stern | **Red** – only a broadside is worth it | **Green** – angling protects you |
| no rating | Grey | Grey |

The **shape** carries the same message, so it stays readable with colour vision deficiency:

- **Shell:** all segments filled = everywhere, only the tip filled = bow/stern only, slash = nowhere.
- **Shield:** full and intact = the target does not get through, lower part filled = bow/stern
  only, **cracked** = the target gets through everywhere.
- Star and warning triangle flash briefly when you lock a target.

A colour-blind scheme in blue/yellow/orange (Okabe-Ito palette) is available for red-green
colour vision deficiency.

### HE and SAP

The shell always rates the **ammunition currently loaded**. A small tag (AP / HE / SAP), like on
the ammo slots in the HUD, shows which one. HE and SAP have their own drawings based on the game's
ammo icons: HE explodes on a plate (smoke and flash), SAP hits a plate and splinters.

HE and SAP do not overmatch; they penetrate a plate when their penetration value is at least as
thick as the plate. PenLight checks this for **bow/stern** and **deck** – the two zones you
usually aim HE/SAP at:

- Penetration values are always rounded down to whole millimetres; a tie counts as penetration.
- For HE, PenLight uses the penetration modifier the game reports for your ship, so the **IFHE**
  commander skill is included. When IFHE is active, a small **IFHE** tag appears at the bottom
  left of the HE shell. SAP is not affected by IFHE.

<p align="center">
  <img src="docs/images/ammo.png" alt="Shell icons for AP, HE (with and without IFHE) and SAP in every state, with ammo tag" width="630">
</p>

| Penetrates bow/stern | Penetrates deck | Shell |
|---|---|---|
| yes | yes | **Green + star** – tip, band and rear ring filled |
| yes | no | **Orange** – tip and band filled |
| no | yes | **Orange** – tip and rear ring filled |
| no | no | **Red** – slash |
| – | – | Grey – no rating |

The band stands for bow/stern, the rear ring for the deck. The tip always carries the
traffic-light colour.

The shield does not depend on your ammunition: it always shows whether the **target's AP** can
overmatch you.

### Detail view (Alt)

<img src="docs/images/detail.png" alt="Detail view: Target on top, Me below, each in a frame with label and ship name" align="right" width="210">

Holding **Alt** replaces shell and shield with two ships, one above the other:

- **TARGET** on top: which zones of the target my loaded shell gets through (AP: overmatch,
  HE/SAP: penetration, here including midship).
- **ME** below: which of my zones the target's AP overmatches.
- In this view green always means **gets through**, for TARGET and ME alike. Only the normal
  view colours by good/bad for you.
- In game, the **ship silhouettes from the health bar** are coloured in: the hull is split into
  stern, midship and bow, everything above the deck line counts as deck. The ship name is shown
  underneath.
- The picture here uses a drawn ship, because no game graphics are shipped with the mod. The
  same drawn ships are used in game if a silhouette is missing.
- Optionally the detail view can be shown permanently instead of the icons. It also follows the
  colour-blind scheme.

Deliberate simplification: the citadel is not rated. Green means the outer plating is
penetrated, not that you hit the citadel.

<br clear="right">

---

## Fair play

PenLight is an information display. It answers the same question the armour viewer in port
answers – "is this plate thinner than what my shell gets through?" – for the ship you have locked.

**What it reads in battle** (official ModsAPI and the game's own UI data):

- the ship type of each player, as shown in the team lists anyway;
- which ship you have locked;
- your **own** loaded main-battery ammunition and its fixed values, and your **own** HE
  penetration modifier (e.g. the IFHE commander skill).

**What it does not do:**

- It reads nothing about other players beyond their ship type: no positions, spotting, health,
  reload, ammunition, consumables or builds.
- No aiming help, no lead or trajectory prediction, no automatic input.
- No changes to game files, ship characteristics or game rules. No executables or DLLs;
  everything lives in `res_mods`, settings in `ModPrefs`.

Armour and calibres are static ship data. They are extracted offline from the client's
`GameParams.data` and shipped as a table (`ships.json`) for exactly one game version.

---

## Editions and branches

| Branch | Requires | Settings | Moving the display |
|---|---|---|---|
| `main` | ModForge **and** TTaroModUtils | options page in TTaro Mod Config (gear button next to the display) | drag with the mouse |
| `main-standalone` | ModForge; TTaroModUtils **optional** | with TTaro: as on `main`; without: hotkeys | drag with the mouse (with or without TTaro) |

`main-standalone` detects TTaroModUtils automatically and then behaves like `main`. Without
TTaro it uses its own hotkeys and a small Flash part for dragging.

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
   overwrite existing PenLight files.
4. Start the game. If `res_mods/PnFMods/PenLight/penlight_log.txt` exists afterwards,
   the mod was loaded.

More detailed notes and diagnostics (German): [`mod/README.md`](mod/README.md).

**Uninstall:** delete the PenLight files from `res_mods` (`PnFMods/PenLight/`,
`gui/unbound2/PnFMods/PenLight*.unbound`, `ForgeBlueprints/PenLightContainer.xml`,
`ModSchemas/diedreibeiden-penlight.schema.json`, `texts/*/penlight.mo`). `main-standalone` without
TTaro also keeps its settings in `World of Warships/ModPrefs/diedreibeiden-penlight.json`.

---

## Usage

### With TTaroModUtils

In battle, hold **Ctrl** to show the mouse cursor:

- Grab the icons and **drag** to move the display.
- The **gear** to the left of the display opens the PenLight page in TTaro Mod Config:
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
    mod/res_mods/PnFMods/PenLight/ships.json 15,9,0,13357625
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
| Generate `Main.py` (from `src/penlight/`) | `python3 -I tools/build_mod.py` |
| Draw shell, shield, HE/SAP icons, tags and marks | `python3 -I tools/make_ampel_icons.py` |
| Detail images, labels, frames | `python3 -I tools/make_detail_icons.py` |
| README images | `python3 -I tools/make_readme_images.py` |
| Texts of the TTaro options page | `python3 -I tools/make_texts.py` |
| Flash part `Main.swf` (`main-standalone`) | `tools/build_flash.py`, requirements in the file header |
| Release with both zips | GitHub: Actions → Release → Run workflow (on `main`); text in `docs/RELEASE_NOTES.md` |

- The game logic (`src/penlight/logic.py`) runs on Python 2.7 (client) and 3.x (tests).
- `mod/res_mods/PnFMods/PenLight/Main.py` is generated – edit `src/penlight/` instead.
- All graphics are drawn by scripts; no game assets are shipped.
- Concept, traffic-light logic and notes on the client (German): [`docs/KONZEPT.md`](docs/KONZEPT.md).

---

## Repository layout

```
mod/res_mods/                     files as they belong in bin/<build>/res_mods/
  PnFMods/PenLight/               Main.py (generated), ships.json, icons, (Main.swf)
  gui/unbound2/PnFMods/           PenLight*.unbound – the display (Unbound 2)
  ForgeBlueprints/                ModForge manifest
  ModSchemas/, texts/             options page for TTaro Mod Config
src/penlight/                     logic.py (traffic light), mod_main.py (client binding)
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
  dependencies, not shipped. Their code, and that of his PenetrationCalculator (for the
  ammunition API), served as reference only; nothing was copied.
- Detecting the locked target in Unbound is modelled on XTargetTracker (Battle Expert); no code
  was copied.

PenLight only uses the official ModsAPI and the published interfaces of the mods above.
A licence for this repository has not been chosen yet.
