**PenLight 0.3.1** – the display is now shown only in the zoomed aiming view (binoculars / scope) and hidden in the normal third-person view.

Tested with the EU client, build **15.9.0.13357625**. The ship data (`ships.json`) is valid for exactly this game version; on any other version the mod switches itself off and says so in its log.

## Changes since 0.3.0

- Display, gear button and drag area appear only in the aiming view (binoculars / scope).
- Both editions now report version 0.3.1 to ModForge.

## Downloads

| File | Edition | Requires |
|---|---|---|
| `PenLight-0.3.1-ttaro.zip` | `main` | [ModForge](https://github.com/AndrewTaro/ModForge) **and** [TTaroModUtils](https://github.com/AndrewTaro/TTaroModUtils) – settings page in TTaro Mod Config |
| `PenLight-0.3.1-standalone.zip` | `main-standalone` | [ModForge](https://github.com/AndrewTaro/ModForge); TTaroModUtils optional – without it: hotkeys (Ctrl+Alt) and mouse drag |

Install only **one** of the two.

## Installation

1. Close the game.
2. Unzip the archive into `World of Warships/bin/<highest number>/` so that the `res_mods` folder from the zip merges with the existing one.
3. Start the game. If `res_mods/PnFMods/PenLight/penlight_log.txt` exists afterwards, the mod was loaded.

If you used an earlier "Overmatcher" build, delete its files first (`PnFMods/Overmatcher/`, `gui/unbound2/PnFMods/Overmatcher*.unbound`, `ForgeBlueprints/OvermatcherContainer.xml`, `ModSchemas/diedreibeiden-overmatcher.schema.json`, `texts/*/overmatcher.mo`), otherwise both run at the same time.

## What it does

- **Shell:** does your loaded ammunition get through the locked target? AP by overmatch (calibre > 14.3 × plate), HE/SAP by penetration (rounded down, tie counts; HE includes your own modifier such as IFHE, marked with a small tag).
- **Shield:** can the target's AP overmatch you?
- **Alt:** detail view per zone (bow/stern, midship, deck) for both ships, using the game's own silhouettes.
- AP and shield: cruisers and battleships. HE/SAP: from destroyers, cruisers and battleships against destroyers, cruisers, battleships and carriers. Submarines are not rated.
- Colour-blind palette and shape coding.

See the [README](https://github.com/DieDreiBeiden/wows-PenLight#readme) for details and the **Fair play** section: PenLight only compares static armour and calibre data with your own loaded ammunition; it reads nothing about other players beyond their ship type.

## Known issues

- **Nebraska, Delaware, Louisiana:** their deck is read as 6 mm from the game data, which is almost certainly wrong. As a target, their deck is shown as penetrated by any HE/SAP and overmatched by AP from 86 mm calibre; treat the deck rating of these three ships as unreliable.

## Known limitations

- Pre-release: IFHE detection is implemented but not yet confirmed in game.
- Standalone edition without TTaro: the invisible Flash drag area stays active in the third-person view (only with the mouse cursor shown).
- Mouse drag is confirmed in game with TTaroModUtils; the standalone Flash drag without TTaro is not yet confirmed.
- The citadel is not rated; green means the outer plating is penetrated.

---

**Deutsch (kurz):** 0.3.1 zeigt die Anzeige nur noch in der Zielansicht (Fernglas / Zielfernrohr). Nur **eines** der beiden Zips installieren (TTaro-Fassung oder Standalone), Inhalt nach `World of Warships/bin/<höchste Nummer>/` entpacken. Getestet mit EU-Client 15.9.0.13357625. Details und Fair-Play-Hinweise in der [README auf Deutsch](https://github.com/DieDreiBeiden/wows-PenLight/blob/main/README.de.md).
