# PenLight

[English](README.md) · **Deutsch**

*PenLight = **Pen**etration (Durchschlag) + **Light** (Ampel).*

**Overmatch- und Durchschlags-Anzeige für World of Warships.** Schaltest du ein Ziel auf, zeigt
PenLight direkt neben dem Fadenkreuz zwei kleine Ampeln:

- **Granate:** Kommt meine **geladene** Munition durch die Panzerung des Ziels? AP wird nach
  Overmatch bewertet, HE und SAP nach ihrem Durchschlagswert.
- **Schild:** Können die AP-Granaten des Ziels meine Panzerung overmatchen?

Mit gedrückter **Alt**-Taste zeigt eine Detailansicht dasselbe für jede Zone beider Schiffe:
Bug/Heck, Mitte und Deck.

Die Anzeige erscheint nur in der **gezoomten Zielansicht** (Fernglas / Zielfernrohr). In der
normalen Außenperspektive ist sie ausgeblendet.

<p align="center">
  <img src="docs/images/ampel.png" alt="Granate und Schild in allen Zuständen, Standard- und Farbenblind-Farben" width="610">
</p>

> Informationsanzeige über die offizielle ModsAPI des Spiels. Sie vergleicht nur statische
> Panzerungs- und Kaliberwerte, wie die Panzerungsansicht im Hafen – siehe [Fair Play](#fair-play).
> Getestet mit dem EU-Client, Build 15.9.0.13357625 (Linux/Steam).

---

## Inhalt

- [Was angezeigt wird](#was-angezeigt-wird)
- [Fair Play](#fair-play)
- [Fassungen und Branches](#fassungen-und-branches)
- [Installation](#installation)
- [Bedienung](#bedienung)
- [Nach einem Spiel-Patch](#nach-einem-spiel-patch)
- [Entwicklung](#entwicklung)
- [Projektstruktur](#projektstruktur)
- [Datenquellen und Danksagungen](#datenquellen-und-danksagungen)
- [Autoren](#autoren)

---

## Was angezeigt wird

### Bewertete Zonen

Jedes Schiff ist in drei Zonen geteilt: **Bug/Heck**, **Mitte** und **Deck**. Welche Schiffe
bewertet werden, hängt von der geladenen Munition ab:

- **AP** und **Schild**: nur, wenn dein eigenes Schiff und das Ziel beide **Kreuzer oder
  Schlachtschiffe** sind.
- **HE und SAP**: von Zerstörern, Kreuzern und Schlachtschiffen gegen Zerstörer, Kreuzer,
  Schlachtschiffe und Träger. Ist die Paarung keine Kreuzer/Schlachtschiff-Paarung, bleibt der
  Schild grau. Träger werden nur als Ziel bewertet, U-Boote gar nicht.

Ohne Ziel oder bei einer nicht bewerteten Paarung bleiben die Symbole grau.

### Overmatch (AP)

Eine Granate overmatcht eine Panzerplatte, wenn

```
Kaliber > 14,3 × Plattendicke
```

Dann durchschlägt sie diese Platte bei jedem Auftreffwinkel; Anwinkeln hilft nicht. Gleichstand
zählt nicht als Overmatch.

### Die Ampel

Die Farben zeigen, ob die Lage **gut oder schlecht für dich** ist. Deshalb haben Granate und
Schild beim gleichen Ergebnis entgegengesetzte Farben:

| Overmatch auf … | Granate (meine AP → Ziel) | Schild (AP des Ziels → ich) |
|---|---|---|
| allen drei Zonen | **Grün + Stern** – ich komme überall durch, auch wenn das Ziel anwinkelt | **Rot + Warndreieck** – das Ziel kommt überall durch, seinen Geschützen ausweichen |
| nur Bug/Heck | **Orange** – auf Bug/Heck zielen | **Orange** – Bug/Heck aus seinem Feuer halten |
| nicht einmal Bug/Heck | **Rot** – nur die Breitseite lohnt | **Grün** – Anwinkeln schützt dich |
| keine Bewertung | Grau | Grau |

Die **Form** trägt dieselbe Aussage, damit alles auch bei Farbsehschwäche lesbar bleibt:

- **Granate:** alle Segmente gefüllt = überall, nur die Spitze gefüllt = nur Bug/Heck,
  Schrägstrich = nirgends.
- **Schild:** voll und heil = das Ziel kommt nicht durch, unterer Teil gefüllt = nur Bug/Heck,
  **gerissen** = das Ziel kommt überall durch.
- Stern und Warndreieck blinken beim Aufschalten kurz auf.

Für Rot-Grün-Schwäche gibt es ein Farbschema in Blau/Gelb/Orange (Okabe-Ito-Palette).

### HE und SAP

Die Granate bewertet immer die **gerade geladene Munition**. Eine kleine Plakette (AP / HE / SAP)
wie an den Munitions-Slots im HUD zeigt, welche. HE und SAP haben eigene Zeichnungen nach den
Munitions-Symbolen des Spiels: HE explodiert auf einer Platte (Rauch und Blitz), SAP schlägt auf
und splittert.

HE und SAP overmatchen nicht; sie durchschlagen eine Platte, wenn ihr Durchschlagswert mindestens
so groß ist wie die Plattendicke. PenLight prüft das für **Bug/Heck** und **Deck**, die beiden
Zonen, auf die man mit HE/SAP meist zielt:

- Durchschlagswerte werden immer auf ganze Millimeter abgerundet; Gleichstand zählt als Durchschlag.
- Für HE nutzt PenLight den Durchschlags-Modifikator, den das Spiel für dein Schiff meldet; die
  Kapitänsfertigkeit **IFHE** ist also enthalten. Ist IFHE aktiv, erscheint links unten an der
  HE-Granate eine kleine Plakette **IFHE**. SAP ist von IFHE nicht betroffen.

<p align="center">
  <img src="docs/images/ammo.png" alt="Granaten-Symbole für AP, HE (mit und ohne IFHE) und SAP in allen Zuständen, mit Munitions-Plakette" width="630">
</p>

| Durchschlag Bug/Heck | Durchschlag Deck | Granate |
|---|---|---|
| ja | ja | **Grün + Stern** – Spitze, Band und hinterer Ring gefüllt |
| ja | nein | **Orange** – Spitze und Band gefüllt |
| nein | ja | **Orange** – Spitze und hinterer Ring gefüllt |
| nein | nein | **Rot** – Schrägstrich |
| – | – | Grau – keine Bewertung |

Das Band steht für Bug/Heck, der hintere Ring für das Deck. Die Spitze trägt immer die Ampelfarbe.

Der Schild hängt nicht von deiner Munition ab: Er zeigt immer, ob die **AP des Ziels** dich
overmatchen kann.

### Detailansicht (Alt)

<img src="docs/images/detail.png" alt="Detailansicht: Target oben, Me unten, jeweils im Rahmen mit Beschriftung und Schiffsname" align="right" width="210">

Mit gedrückter **Alt**-Taste ersetzen zwei untereinander stehende Schiffe Granate und Schild:

- **TARGET** oben: durch welche Zonen des Ziels meine geladene Granate kommt (AP: Overmatch,
  HE/SAP: Durchschlag, hier auch für die Mitte).
- **ME** unten: welche meiner Zonen die AP des Ziels overmatcht.
- In dieser Ansicht heißt Grün immer **kommt durch**, für TARGET und ME gleich. Nur die normale
  Ansicht färbt nach gut/schlecht für dich.
- Im Spiel werden die **Schiffs-Silhouetten aus dem Lebensbalken** eingefärbt: der Rumpf geteilt
  in Heck, Mitte und Bug, alles oberhalb der Decklinie zählt als Deck. Darunter steht der
  Schiffsname.
- Die Abbildung hier zeigt ein gezeichnetes Schiff, weil keine Spielgrafiken mitgeliefert werden.
  Dieselben gezeichneten Schiffe springen im Spiel ein, wenn eine Silhouette fehlt.
- Optional ersetzt die Detailansicht die Symbole dauerhaft; das Farbenblind-Schema gilt auch hier.

Bewusste Vereinfachung: Die Zitadelle wird nicht bewertet. Grün heißt, die äußere Beplankung wird
durchschlagen, nicht, dass du die Zitadelle triffst.

<br clear="right">

---

## Fair Play

PenLight ist eine Informationsanzeige. Sie beantwortet dieselbe Frage wie die Panzerungsansicht
im Hafen – „ist diese Platte dünner als das, was meine Granate durchschlägt?“ – für das
aufgeschaltete Schiff.

**Was sie im Gefecht liest** (offizielle ModsAPI und Oberflächendaten des Spiels):

- den Schiffstyp jedes Spielers, wie er ohnehin in den Teamlisten steht;
- welches Schiff du aufgeschaltet hast;
- deine **eigene** geladene Munition der Hauptbewaffnung mit ihren festen Werten und deinen
  **eigenen** HE-Durchschlags-Modifikator (z. B. die Kapitänsfertigkeit IFHE).

**Was sie nicht tut:**

- Über andere Spieler liest sie nichts außer dem Schiffstyp: keine Positionen, Aufklärung,
  Lebenspunkte, Nachladezeiten, Munition, Verbrauchsgüter oder Ausrüstung.
- Keine Zielhilfe, keine Vorhalte- oder Flugbahnberechnung, keine automatischen Eingaben.
- Keine Änderung an Spieldateien, Schiffswerten oder Spielregeln. Keine ausführbaren Dateien oder
  DLLs; alles liegt in `res_mods`, Einstellungen in `ModPrefs`.

Panzerung und Kaliber sind statische Schiffsdaten. Sie werden offline aus der Client-Datei
`GameParams.data` ausgelesen und als Tabelle (`ships.json`) für genau eine Spielversion
mitgeliefert.

---

## Fassungen und Branches

| Branch | Benötigt | Einstellungen | Verschieben |
|---|---|---|---|
| `main` | ModForge **und** TTaroModUtils | Optionsseite in TTaro Mod Config (Zahnrad neben der Anzeige) | mit der Maus ziehen |
| `main-standalone` | ModForge; TTaroModUtils **optional** | mit TTaro: wie `main`; ohne: Tastenkürzel | mit der Maus ziehen (mit oder ohne TTaro) |

`main-standalone` erkennt TTaroModUtils automatisch und verhält sich dann wie `main`. Ohne TTaro
nutzt es eigene Tastenkürzel und einen kleinen Flash-Teil zum Ziehen.

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
   und vorhandene PenLight-Dateien überschreiben.
4. Spiel starten. Liegt danach `res_mods/PnFMods/PenLight/penlight_log.txt` vor,
   wurde die Mod geladen.

Ausführlichere Hinweise und Diagnose: [`mod/README.md`](mod/README.md).

**Entfernen:** die PenLight-Dateien aus `res_mods` löschen (`PnFMods/PenLight/`,
`gui/unbound2/PnFMods/PenLight*.unbound`, `ForgeBlueprints/PenLightContainer.xml`,
`ModSchemas/diedreibeiden-penlight.schema.json`, `texts/*/penlight.mo`). `main-standalone` ohne
TTaro speichert seine Einstellungen zusätzlich in `World of Warships/ModPrefs/diedreibeiden-penlight.json`.

---

## Bedienung

### Mit TTaroModUtils

Im Gefecht in die Zielansicht wechseln und **Strg** halten, damit der Mauszeiger erscheint:

- Symbole greifen und **ziehen**, um die Anzeige zu verschieben.
- **Zahnrad** links neben der Anzeige öffnet die PenLight-Seite in TTaro Mod Config:
  Darstellungsmodus (Detail mit Alt / immer), Farben (Standard / Farbenblind),
  Größenskalierung, Verschieben sperren, Position zurücksetzen.

### Ohne TTaroModUtils (`main-standalone`)

- **Ziehen** mit der Maus in der Zielansicht: Strg halten, über Granate | Schild fahren (feiner Rahmen erscheint), ziehen.
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
    mod/res_mods/PnFMods/PenLight/ships.json 15,9,0,13357625
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
| `Main.py` erzeugen (aus `src/penlight/`) | `python3 -I tools/build_mod.py` |
| Icons für Granate, Schild, HE/SAP, Plaketten und Zeichen zeichnen | `python3 -I tools/make_ampel_icons.py` |
| Detail-Bilder, Beschriftungen, Rahmen | `python3 -I tools/make_detail_icons.py` |
| Abbildungen der README | `python3 -I tools/make_readme_images.py` |
| Texte der TTaro-Optionsseite | `python3 -I tools/make_texts.py` |
| Flash-Teil `Main.swf` (`main-standalone`) | `tools/build_flash.py`, Voraussetzungen siehe Dateikopf |
| To-Do-Liste | [`docs/TODO.md`](docs/TODO.md) |
| Release mit beiden Zips | `version` in `ForgeBlueprints/PenLightContainer.xml` auf beiden Branches erhöhen, dann GitHub: Actions → Release → Run workflow (auf `main`). Neuerungen = „Unreleased“ in `docs/CHANGELOG.md`, Rahmen in `docs/RELEASE_NOTES.md` |

- Die Spiel-Logik (`src/penlight/logic.py`) läuft unter Python 2.7 (Client) und 3.x (Tests).
- `mod/res_mods/PnFMods/PenLight/Main.py` ist generiert – Änderungen in `src/penlight/`.
- Alle Grafiken werden per Skript gezeichnet; es werden keine Spielgrafiken mitgeliefert.
- Konzept, Ampel-Logik und gesammelte Befunde zum Client: [`docs/KONZEPT.md`](docs/KONZEPT.md).

---

## Projektstruktur

```
mod/res_mods/                     Dateien so, wie sie in bin/<Build>/res_mods/ gehören
  PnFMods/PenLight/               Main.py (generiert), ships.json, Icons, (Main.swf)
  gui/unbound2/PnFMods/           PenLight*.unbound – die Anzeige (Unbound 2)
  ForgeBlueprints/                ModForge-Manifest
  ModSchemas/, texts/             Optionsseite für TTaro Mod Config
src/penlight/                     logic.py (Ampel), mod_main.py (Anbindung an den Client)
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
  Abhängigkeiten genutzt, aber nicht mitgeliefert. Ihr Code und der seines PenetrationCalculator
  (für die Munitions-API) diente nur als Referenz; übernommen wurde nichts.
- Die Erkennung des aufgeschalteten Ziels in Unbound folgt dem Muster von XTargetTracker
  (Battle Expert); übernommen wurde kein Code.

PenLight nutzt ausschließlich die offizielle ModsAPI bzw. die veröffentlichten Schnittstellen
der genannten Mods. Eine Lizenz für dieses Repository ist noch nicht festgelegt.

---

## Autoren

- [DieDreiBeiden](https://github.com/DieDreiBeiden) – Idee, Gestaltungsentscheidungen, Tests im Spiel
- Claude (Anthropic) – Umsetzung, als Mitautor der Commits
