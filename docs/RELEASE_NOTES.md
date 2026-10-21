First public pre-release of **PenLight** – overmatch and penetration indicator for World of Warships (formerly developed as "Overmatcher").

Tested with the EU client, build **15.9.0.13357625**. The ship data (`ships.json`) is valid for exactly this game version; on any other version the mod switches itself off and says so in its log.

## Downloads

| File | Edition | Requires |
|---|---|---|
| `PenLight-0.3.0-ttaro.zip` | `main` | [ModForge](https://github.com/AndrewTaro/ModForge) **and** [TTaroModUtils](https://github.com/AndrewTaro/TTaroModUtils) – settings page in TTaro Mod Config |
| `PenLight-0.3.0-standalone.zip` | `main-standalone` | [ModForge](https://github.com/AndrewTaro/ModForge); TTaroModUtils optional – without it: hotkeys (Ctrl+Alt) and mouse drag |

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

## Known limitations

- Pre-release: the following are implemented but not yet confirmed in game – IFHE detection, mouse drag via the Flash part (standalone without TTaro).
- The citadel is not rated; green means the outer plating is penetrated.
- The deck value of a few US battleships (Nebraska, Delaware, Louisiana: 6 mm) is probably read incorrectly from the game data and will be checked.
- The ModForge manifest of the TTaro edition still reports version 0.2.0.

---

**Deutsch (kurz):** Erste öffentliche Vorabversion. Nur **eines** der beiden Zips installieren (TTaro-Fassung oder Standalone), Inhalt nach `World of Warships/bin/<höchste Nummer>/` entpacken. Getestet mit EU-Client 15.9.0.13357625. Details und Fair-Play-Hinweise in der [README auf Deutsch](https://github.com/DieDreiBeiden/wows-PenLight/blob/main/README.de.md).
