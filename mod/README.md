# Installation

Spiel beenden. Ordner mit der **höchsten Nummer** unter `World_of_Warships\bin\` suchen
(z. B. `bin\13357625\`) und Folgendes nach `bin\<Nummer>\res_mods\` kopieren:

| Datei | Zweck |
|---|---|
| `PnFModsLoader.py` | leere Datei, aktiviert Python-Mods (bei dir schon vorhanden) |
| `PnFMods\PenLight\Main.py` | die Mod (generiert, siehe unten) |
| `PnFMods\PenLight\Main.swf` | Greiffläche zum Verschieben per Maus (gebaut mit `tools/build_flash.py`) |
| `PnFMods\PenLight\ships.json` | Panzerungs-/Kaliberdaten für genau eine Spielversion |
| `PnFMods\PenLight\shell_*.png`, `shield_*.png` | Icons Granate/Schild (29×29) |
| `gui\unbound2\PnFMods\PenLight.unbound` | Anzeige am Fadenkreuz (ab 0.2, benötigt ModForge) |
| `ForgeBlueprints\PenLightContainer.xml` | ModForge-Manifest für die Anzeige |

Voraussetzung: **ModForge**. **TTaroModUtils** ist optional und wird automatisch erkannt:

- **Mit TTaroModUtils:** Optionsseite in TTaro Mod Config, Zahnrad links neben der Anzeige,
  Ziehen mit der Maus über TTaro (wie bei den übrigen TTaro-Mods). Tastenkürzel und `Main.swf` sind aus.
- **Ohne TTaroModUtils:** Ziehen über `Main.swf`, Einstellungen per Tastenkürzel (unten).

| `gui\unbound2\PnFMods\PenLightTTaro.unbound` | Hülle für TTaroModUtils (nur eingehängt, wenn installiert) |
| `ModSchemas\diedreibeiden-penlight.schema.json`, `texts\<Sprache>\penlight.mo` | Optionsseite für TTaro Mod Config |

Ohne TTaroModUtils – verschieben mit der Maus: im Gefecht Mauszeiger einblenden (Strg halten), über Granate | Schild
fahren (feiner Rahmen erscheint) und ziehen. Die Position wird beim Loslassen gespeichert.
Dafür sorgt `PnFMods\PenLight\Main.swf` (Flash-Teil, offizielle ModsAPI).

Ohne TTaroModUtils – Einstellungen im Gefecht mit **Strg+Alt** und:

| Taste | Wirkung |
|---|---|
| Pfeiltasten | Anzeige verschieben, 5 px (mit Umschalt 1 px) |
| Pos1 | Position zurücksetzen |
| D | Detailansicht: mit Alt-Taste oder immer |
| F | Farben: Standard (Grün/Orange/Rot) oder Farbenblind (Blau/Gelb/Orange) |
| + / − | Größe 0,5–2,0 |

Gespeichert wird in `(wows)/ModPrefs/diedreibeiden-penlight.json`.

Ablageorte wie bei PenetrationCalculator (vom Nutzer bestätigt).

Die Mod zeigt Granate und Schild immer als Icons am Fadenkreuz: grau ohne Ziel, in Ampelfarben
bei aufgeschaltetem Kreuzer/Schlachtschiff, mit gedrückter Alt-Taste die Detailansicht (Bug/Heck, Mitte, Deck). Zusätzlich steht das Ergebnis in
`PnFMods\PenLight\penlight_last.txt`. Diagnose (wird fortlaufend angehängt):
`PnFMods\PenLight\penlight_log.txt` und `profile\python.log` (Zeilen mit `[PenLight]`).
Fehlt `penlight_log.txt` nach dem Spielstart ganz, wurde die Mod nicht geladen.

Passt `ships.json` nicht zur Spielversion, deaktiviert sich die Mod und schreibt das ins Log.

Entfernen: Ordner `PenLight` löschen. Die Probe-Mod `OvermatcherProbe` wird nicht mehr
gebraucht und kann ebenfalls gelöscht werden.

# Nach einem Patch

1. `content/GameParams.data` mit dem WoWs Unpack Tool extrahieren.
2. `python3 -I tools/gameparams.py GameParams.data ships_full.json mod/res_mods/PnFMods/PenLight/ships.json <Version>`
   (`<Version>` wie im python.log, z. B. `15,9,0,13357625`)
3. `python3 -I tools/build_mod.py`, Tests: `python3 -m unittest discover -s tests`

Texte der Optionsseite: `python3 -I tools/make_texts.py` (Quelle `tools/data/texts.json`).

Flash-Teil neu bauen (nur nach Änderung an `src/as3/Main.as`): siehe Kopf von `tools/build_flash.py`
(Apache Flex SDK 4.16.1, Adobe `playerglobal32_0.swc`, `wows_library.swc` aus dem ModSDK).

Icons neu erzeugen (nur nach Änderung der Grafiken): `python3 -I tools/make_ampel_icons.py`
(gezeichnet: AP-Granate / Wappenschild, Ampelfarbe auf Spitze bzw. Sparren) und `python3 -I tools/make_detail_icons.py` (gezeichnet: Schiff mit Sektionen, Mini-Icon + Beschriftung).
