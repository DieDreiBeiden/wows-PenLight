# Overmatcher

[English](README.md) · **Deutsch**

**Overmatch-Anzeige für World of Warships.** Schaltest du einen Kreuzer oder ein
Schlachtschiff auf, zeigt Overmatcher direkt am Fadenkreuz zwei Ampeln:

- **Granate:** Kann meine Panzerbrechende (AP) das Ziel überwiegend durchschlagen (overmatchen)?
- **Schild:** Kann das Ziel mit seiner AP mich overmatchen?

Mit gedrückter **Alt**-Taste erscheint eine Detailansicht: die Schiffs-Silhouetten des Spiels,
aufgeteilt in **Bug/Heck**, **Mitte** und **Deck**, jeweils grün (Overmatch) oder rot (kein Overmatch).

<p align="center">
  <img src="docs/images/ampel.png" alt="Granate und Schild in allen Zuständen, Standard- und Farbenblind-Farben" width="610">
</p>

> Interface-Mod über die offizielle ModsAPI des Spiels. Getestet mit dem EU-Client,
> Build 15.9.0.13357625 (Linux/Steam).

---

## Inhalt

- [Was angezeigt wird](#was-angezeigt-wird)
- [Fassungen und Branches](#fassungen-und-branches)
- [Installation](#installation)
- [Bedienung](#bedienung)
- [Nach einem Spiel-Patch](#nach-einem-spiel-patch)
- [Entwicklung](#entwicklung)
- [Projektstruktur](#projektstruktur)
- [Datenquellen und Danksagungen](#datenquellen-und-danksagungen)

---

## Was angezeigt wird

### Die Overmatch-Regel

Eine Granate overmatcht eine Panzerplatte, wenn

```
Kaliber > 14,3 × Plattendicke
```

Dann durchschlägt sie die Platte unabhängig vom Auftreffwinkel, auch bei gewinkelten Schiffen.
Gleichstand zählt nicht als Overmatch.

### Die Ampel

Bug/Heck ist die Grundvoraussetzung; „überall“ heißt, dass zusätzlich Mitte **und** Deck
overmatcht werden. Die Farben zeigen, ob die Lage **gut oder schlecht für dich** ist:

| Bug/Heck | Mitte und Deck | Granate (ich → Ziel) | Schild (Ziel → ich) |
|---|---|---|---|
| ja | beide ja | **Grün + Stern** – ich komme überall durch, auch gewinkelt | **Rot + Warndreieck** – das Ziel kommt überall durch, ausweichen |
| ja | nicht beide | Orange – auf Bug/Heck zielen | Orange – Bug/Heck schützen |
| nein | – | Rot – nur die Breitseite lohnt | Grün – Anwinkeln wirkt |
| – | – | Grau – kein Ziel, oder Zerstörer/Träger/U-Boot | Grau |

Die **Form** trägt dieselbe Aussage ohne Farbe. Granate: alle Segmente gefüllt = ich komme
überall durch, nur die Spitze = nur Bug/Heck, Schrägstrich = ich komme nicht durch. Schild: voll
und heil = das Ziel kommt nicht durch, teilweise gefüllt = nur Bug/Heck, **gebrochen** = das Ziel
kommt überall durch. Stern und Warndreieck blinken beim Aufschalten kurz auf. So bleibt alles auch
bei Farbsehschwäche lesbar.

Bewertet werden nur Paarungen aus **Kreuzern und Schlachtschiffen**; für alle anderen bleiben
die Symbole grau. Für Rot-Grün-Schwäche gibt es ein Farbschema in Blau/Gelb/Orange
(Okabe-Ito-Palette).

### HE und SAP

Die Granate bewertet immer die **gerade geladene Munition**; eine kleine Plakette (AP / HE / SAP)
wie an den Munitions-Slots im HUD zeigt, welche. HE und SAP haben eigene Zeichnungen nach den
Munitions-Symbolen des Spiels: HE schlägt auf eine Fläche auf und explodiert (Rauch und Blitz), SAP
schlägt auf und splittert. Die Spitze trägt wie bei AP die Ampelfarbe. Statt
Overmatch prüfen sie den festen Durchschlag der Granate gegen die Panzerung des Ziels
(Durchschlag ≥ Platte zählt; die Kapitänsfertigkeit IFHE wird bewusst nicht berücksichtigt):

| Bug/Heck | Deck | Granate |
|---|---|---|
| ja | ja | Grün + Stern – Spitze, Band und Ring gefüllt |
| ja | nein | Orange – Spitze und Band (Mitte) gefüllt |
| nein | ja | Orange – Spitze und hinterer Ring gefüllt |
| nein | nein | Rot – Schrägstrich |

Der Schild bleibt immer der AP-Overmatch des Gegners. In der Detailansicht zeigt das TARGET-Schiff
den Durchschlag der geladenen HE/SAP.

### Detailansicht (Alt)

<img src="docs/images/detail.png" alt="Detailansicht: Target oben, Me unten, jeweils im Rahmen mit Beschriftung und Schiffsname" align="right" width="210">

Mit gedrückter **Alt**-Taste ersetzen zwei untereinander stehende Schiffe Granate und Schild:

- **TARGET** oben: wo meine AP das Ziel overmatcht.
- **ME** unten: wo die AP des Ziels mich overmatcht.
- Hier heißt Grün immer **Overmatch**, für Target und Me gleich. (Nur die normale Ansicht färbt
  nach gut/schlecht für dich.)
- Jedes Schiff liegt in einem dunklen, seitlich auslaufenden Band mit Haarlinien und leicht
  aufgehellter Kopfzeile. Das kleine Granaten-/Schild-Symbol in der Kopfzeile trägt die Farbe
  des großen Symbols.
- Im Spiel werden die **Schiffs-Silhouetten aus dem Lebensbalken** eingefärbt: der Rumpf geteilt
  in Heck, Mitte und Bug, alles oberhalb der Decklinie zählt als Deck. Die Silhouette hat eine
  dunkle Kontur und einen weichen Schatten, darunter steht der Schiffsname in der Spielschrift.
- Die Abbildung zeigt statt der Spiel-Silhouette ein gezeichnetes Schiff, weil keine
  Spielgrafiken mitgeliefert werden. Dieselben gezeichneten Schiffe springen ein, wenn keine
  Silhouette gefunden wird.
- Optional ersetzt die Detailansicht die Symbole dauerhaft; das Farbenblind-Schema gilt auch hier.

Bewusste Vereinfachung: Der Zitadellengürtel wird nicht bewertet. Grün heißt Overmatch der
Beplankung, nicht Zitadellentreffer.

<br clear="right">

---

## Fassungen und Branches

| Branch | Benötigt | Einstellungen | Verschieben |
|---|---|---|---|
| `main` | ModForge **und** TTaroModUtils | Optionsseite in TTaro Mod Config, Zahnrad an der Anzeige | Maus (TTaro) |
| `main-standalone` | ModForge; TTaroModUtils **optional** | mit TTaro wie `main`, sonst Tastenkürzel | mit TTaro per TTaro, sonst Maus über eigenen Flash-Teil |

`main-standalone` erkennt TTaroModUtils automatisch: ModForge hängt je nach Installation eine
von zwei Hüllen ein, und `Main.py` schaltet die eigenen Bedienelemente ab, sobald TTaro vorhanden ist.

---

## Installation

**Voraussetzungen**

- [ModForge](https://github.com/AndrewTaro/ModForge) – hängt die Anzeige ins Gefecht ein.
- Für `main` zusätzlich [TTaroModUtils](https://github.com/AndrewTaro/TTaroModUtils);
  für `main-standalone` optional.

**Schritte**

1. Spiel beenden.
2. Im Spielordner unter `bin/` den Ordner mit der **höchsten Nummer** suchen,
   z. B. `bin/13357625/`.
   - Steam unter Linux: `~/.local/share/Steam/steamapps/common/World of Warships/`
   - Windows: meist `C:\Games\World_of_Warships\`
3. Den Inhalt von [`mod/res_mods/`](mod/res_mods) nach `bin/<Nummer>/res_mods/` kopieren
   und vorhandene Overmatcher-Dateien überschreiben.
4. Spiel starten. Liegt danach `res_mods/PnFMods/Overmatcher/overmatcher_log.txt` vor,
   wurde die Mod geladen.

Ausführlichere Hinweise und Diagnose: [`mod/README.md`](mod/README.md).

**Entfernen:** die Overmatcher-Dateien aus `res_mods` löschen (`PnFMods/Overmatcher/`,
`gui/unbound2/PnFMods/Overmatcher*.unbound`, `ForgeBlueprints/OvermatcherContainer.xml`,
`ModSchemas/diedreibeiden-overmatcher.schema.json`, `texts/*/overmatcher.mo`).

---

## Bedienung

### Mit TTaroModUtils

Im Gefecht **Strg** halten, damit der Mauszeiger erscheint:

- Symbole greifen und **ziehen**, um die Anzeige zu verschieben.
- **Zahnrad** links neben der Anzeige öffnet die Overmatcher-Seite in TTaro Mod Config:
  Darstellungsmodus (Detail mit Alt / immer), Farben (Standard / Farbenblind),
  Größenskalierung, Verschieben sperren, Position zurücksetzen.

### Ohne TTaroModUtils (`main-standalone`)

- **Ziehen** mit der Maus: Strg halten, über Granate | Schild fahren (feiner Rahmen erscheint), ziehen.
- **Tastenkürzel** mit **Strg+Alt**:

| Taste | Wirkung |
|---|---|
| Pfeiltasten | verschieben, 5 px (mit Umschalt 1 px) |
| Pos1 | Position zurücksetzen |
| D | Detailansicht: mit Alt ↔ immer |
| F | Farben: Standard ↔ Farbenblind |
| + / − | Größe 0,5–2,0 |

Gespeichert wird in `World of Warships/ModPrefs/` – Einstellungen überleben Spiel-Patches.

---

## Nach einem Spiel-Patch

Panzerung und Kaliber stammen aus der Spieldatei `content/GameParams.data` und gelten für genau
eine Spielversion. Passt `ships.json` nicht zur laufenden Version, schaltet sich die Mod ab
(lieber nichts anzeigen als falsche Farben) und schreibt das ins Log.

```bash
# 1. GameParams.data mit dem WoWs Unpack Tool aus dem Client extrahieren
# 2. Tabelle erzeugen (Version so, wie sie im python.log steht)
python3 -I tools/gameparams.py GameParams.data ships_full.json \
    mod/res_mods/PnFMods/Overmatcher/ships.json 15,9,0,13357625
# 3. Mod bauen und testen
python3 -I tools/build_mod.py
python3 -m unittest discover -s tests
```

Die Schiffs-Silhouetten liefert das Spiel selbst; sie passen sich jedem Patch automatisch an.

---

## Entwicklung

| Aufgabe | Befehl |
|---|---|
| Tests | `python3 -m unittest discover -s tests` |
| `Main.py` erzeugen (aus `src/overmatcher/`) | `python3 -I tools/build_mod.py` |
| Granate/Schild-Icons zeichnen | `python3 -I tools/make_ampel_icons.py` |
| Detail-Bilder, Beschriftungen, Rahmen | `python3 -I tools/make_detail_icons.py` |
| Abbildungen der README | `python3 -I tools/make_readme_images.py` |
| Texte der TTaro-Optionsseite | `python3 -I tools/make_texts.py` |
| Flash-Teil `Main.swf` (`main-standalone`) | `tools/build_flash.py`, Voraussetzungen siehe Dateikopf |

- Die Spiel-Logik (`src/overmatcher/logic.py`) läuft unter Python 2.7 (Client) und 3.x (Tests).
- `mod/res_mods/PnFMods/Overmatcher/Main.py` ist generiert – Änderungen in `src/overmatcher/`.
- Alle Grafiken werden per Skript gezeichnet; es werden keine Spielgrafiken mitgeliefert.
- Konzept, Ampel-Logik und gesammelte Befunde zum Client: [`docs/KONZEPT.md`](docs/KONZEPT.md).

---

## Projektstruktur

```
mod/res_mods/                     Dateien so, wie sie in bin/<Build>/res_mods/ gehören
  PnFMods/Overmatcher/            Main.py (generiert), ships.json, Icons, (Main.swf)
  gui/unbound2/PnFMods/           Overmatcher.unbound – die Anzeige (Unbound 2)
  ForgeBlueprints/                ModForge-Manifest
  ModSchemas/, texts/             Optionsseite für TTaro Mod Config
src/overmatcher/                  logic.py (Ampel), mod_main.py (Anbindung an den Client)
src/as3/                          Flash-Teil zum Verschieben ohne TTaro (main-standalone)
tools/                            GameParams-Auswertung, Build, Icon-Generatoren
tests/                            Unit-Tests inkl. nachgebautem Client
docs/                             Konzept, Abbildungen
```

---

## Datenquellen und Danksagungen

- **Panzerung und Kaliber:** `GameParams.data` des Spielclients, ausgewertet mit
  [`tools/gameparams.py`](tools/gameparams.py); Namen der Panzerungsmaterialien aus
  [wowsunpack](https://github.com/landaire/wowsunpack) (MIT).
- **ModsAPI und ModSDK** von Wargaming/Lesta (offizielle Dokumentation und `wows_library.swc`).
- **ModForge** und **TTaroModUtils** von [AndrewTaro](https://github.com/AndrewTaro): werden als
  Abhängigkeiten genutzt, aber nicht mitgeliefert. Ihr Code dient nur als Referenz; übernommen
  wurde nichts.
- Ziel-Erkennung nach dem Muster von XTargetTracker (Battle Expert).

Overmatcher nutzt ausschließlich die offizielle ModsAPI bzw. die veröffentlichten Schnittstellen
der genannten Mods. Eine Lizenz für dieses Repository ist noch nicht festgelegt.
