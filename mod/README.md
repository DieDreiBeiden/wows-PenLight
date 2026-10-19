# Probe-Mod installieren

1. Spiel beenden.
2. Im Spielordner den Ordner mit der **höchsten Nummer** unter `bin\` suchen,
   z. B. `World_of_Warships\bin\1234567\`.
3. Den Inhalt von `mod/res_mods/` nach `bin\<Nummer>\res_mods\` kopieren:
   - `PnFModsLoader.py` (leere Datei)
   - `PnFMods\OvermatcherProbe\Main.py`
4. Spiel starten, ein Gefecht im **Trainingsraum** oder Koop starten und warten,
   bis die Karte sichtbar ist.
5. Ergebnis: `bin\<Nummer>\res_mods\PnFMods\OvermatcherProbe\probe_dump2.txt`
   (zusätzlich in `World_of_Warships\profile\python.log`).

Entfernen: Ordner `OvermatcherProbe` löschen. Die Mod liest nur Daten und
verändert keine Spieldateien.
