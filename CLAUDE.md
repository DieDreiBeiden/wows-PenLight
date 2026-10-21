# PenLight – Arbeitsregeln

- Änderungen lokal in logischen Commits sammeln, **nicht automatisch pushen**.
  Am Ende einer Antwort fragen, ob alles gepusht werden soll.
- Mod-Dateien unter `mod/res_mods/` spiegeln die Struktur im Spielordner
  `bin/<Build>/res_mods/`. `Main.py` wird mit `python3 -I tools/build_mod.py`
  aus `src/penlight/` erzeugt, nicht direkt bearbeiten.
- Tests: `python3 -m unittest discover -s tests`
- Konzept, Ampel-Logik und Client-Befunde: `docs/KONZEPT.md`
