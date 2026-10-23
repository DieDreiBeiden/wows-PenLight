# PenLight – Arbeitsregeln

- Änderungen lokal in logischen Commits sammeln, **nicht automatisch pushen**.
  Am Ende einer Antwort fragen, ob alles gepusht werden soll.
- Mod-Dateien unter `mod/res_mods/` spiegeln die Struktur im Spielordner
  `bin/<Build>/res_mods/`. `Main.py` wird mit `python3 -I tools/build_mod.py`
  aus `src/penlight/` erzeugt, nicht direkt bearbeiten.
- Tests: `python3 -m unittest discover -s tests`
- Konzept, Ampel-Logik und Client-Befunde: `docs/KONZEPT.md`
- Für Spieler sichtbare Änderungen auf `main` als englischen Eintrag unter `## Unreleased` in
  `docs/CHANGELOG.md` festhalten; daraus schreibt der Release-Workflow die Release Notes.
- Gewollte Unterschiede zwischen `main` und `main-standalone` in `.github/edition-files.txt`
  eintragen; der Check-Workflow meldet jede andere Abweichung.
- Probe-Builds (Versuche, die erst im Spiel getestet werden) nur im Branch `Test`;
  `main` und `main-standalone` bleiben dabei unangetastet, übernommen wird erst nach Freigabe.
