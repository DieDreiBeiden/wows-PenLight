# Installation

Spiel beenden. Ordner mit der **höchsten Nummer** unter `World_of_Warships\bin\` suchen
(z. B. `bin\13357625\`) und Folgendes nach `bin\<Nummer>\res_mods\` kopieren:

| Datei | Zweck |
|---|---|
| `PnFModsLoader.py` | leere Datei, aktiviert Python-Mods (bei dir schon vorhanden) |
| `PnFMods\Overmatcher\Main.py` | die Mod (generiert, siehe unten) |
| `PnFMods\Overmatcher\ships.json` | Panzerungs-/Kaliberdaten für genau eine Spielversion |
| `PnFMods\Overmatcher\shell_*.png`, `shield_*.png` | Icons Granate/Schild (29×29) |
| `gui\unbound2\PnFMods\Overmatcher.unbound` | Anzeige am Fadenkreuz (ab 0.2, benötigt ModForge) |
| `ForgeBlueprints\OvermatcherContainer.xml` | ModForge-Manifest für die Anzeige |
| `ModSchemas\diedreibeiden-overmatcher.schema.json` | Optionsseite in TTaro Mod Config |
| `texts\<Sprache>\overmatcher.mo` | Texte der Optionsseite (Deutsch, sonst Englisch) |

Voraussetzung: **ModForge** und **TTaroModUtils** (TTaro Mod Config) müssen installiert sein.

Position: im Gefecht mit Mauszeiger (z. B. Strg halten) die Symbole greifen und ziehen.
Zurücksetzen/Sperren in TTaro Mod Config → Overmatcher. Gespeichert wird in `(wows)/ModPrefs/`.

Optionen: Zahnrad links neben der Anzeige (sichtbar bei Mauszeiger, z. B. Strg halten) oder
TTaro Mod Config → Overmatcher:
- Darstellungsmodus: Detailansicht mit Alt-Taste oder immer
- Farben: Standard (Grün/Orange/Rot) oder Farbenblind (Blau/Gelb/Orange)
- Größenskalierung 0,5–2,0

Ablageorte wie bei PenetrationCalculator (vom Nutzer bestätigt).

Die Mod zeigt Granate und Schild immer als Icons am Fadenkreuz: grau ohne Ziel, in Ampelfarben
bei aufgeschaltetem Kreuzer/Schlachtschiff, mit gedrückter Alt-Taste die Detailansicht (Bug/Heck, Mitte, Deck). Zusätzlich steht das Ergebnis in
`PnFMods\Overmatcher\overmatcher_last.txt`. Diagnose (wird fortlaufend angehängt):
`PnFMods\Overmatcher\overmatcher_log.txt` und `profile\python.log` (Zeilen mit `[Overmatcher]`).
Fehlt `overmatcher_log.txt` nach dem Spielstart ganz, wurde die Mod nicht geladen.

Passt `ships.json` nicht zur Spielversion, deaktiviert sich die Mod und schreibt das ins Log.

Entfernen: Ordner `Overmatcher` löschen. Die Probe-Mod `OvermatcherProbe` wird nicht mehr
gebraucht und kann ebenfalls gelöscht werden.

# Nach einem Patch

1. `content/GameParams.data` mit dem WoWs Unpack Tool extrahieren.
2. `python3 -I tools/gameparams.py GameParams.data ships_full.json mod/res_mods/PnFMods/Overmatcher/ships.json <Version>`
   (`<Version>` wie im python.log, z. B. `15,9,0,13357625`)
3. `python3 -I tools/build_mod.py`, Tests: `python3 -m unittest discover -s tests`

Texte der Optionsseite: `python3 -I tools/make_texts.py` (Quelle `tools/data/texts.json`).
Icons neu erzeugen (nur nach Änderung der Grafiken): `python3 -I tools/make_ampel_icons.py`
(gezeichnet: AP-Granate / Wappenschild, Ampelfarbe auf Spitze bzw. Sparren) und `python3 -I tools/make_detail_icons.py` (gezeichnet: Schiff mit Sektionen, Mini-Icon + Beschriftung).
