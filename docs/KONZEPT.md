# Overmatcher – Konzept

Stand: 2026-10-19 · Client: WoWS EU · Verteilung: privat

## Ziel

Auf einen Blick erkennen, ob AP-Granaten Bug/Heck bzw. Deck overmatchen:
- **Granate** – ich als Angreifer gegen das Ziel
- **Schild** – der Gegner gegen mich

## Regeln

Overmatch: `Kaliber > 14,3 × Plattendicke` (Gleichstand = kein Overmatch).
Bug und Heck werden als gleich dick behandelt (ein Wert „bow“).

Variante B (vom Nutzer gewählt): Bug/Heck ist Grundvoraussetzung, Grün bzw. Rot erst,
wenn auch Mitte **und** Deck overmatcht werden.

| Bug/Heck | Mitte und Deck | Granate | Schild |
|---|---|---|---|
| ja | beide ja | Grün – überall durch, auch gewinkelt | Rot – aktiv ausweichen |
| ja | nicht beide | Gelb – gezielt auf Bug/Heck | Gelb – Bug/Heck schützen, auf Distanz Panzerung nutzen |
| nein | egal | Rot – nur Breitseite | Grün – aggressiv anwinkeln |

Mitte = dünnste Seitenplatte mittschiffs (`Cas_Belt`, `SSC_ConstrSide`). Fehlt der Wert,
entscheiden Bug/Heck und Deck allein.

Häufigkeit Stufe VIII–X (alle Paarungen BB/CA, ungewichtet): alle drei 10,5 %,
Bug ohne alles 16,4 %, Bug nicht 73,1 % → Granate grün/gelb/rot 10,5/16,4/73,1 %.

Bewusste Vereinfachung: Der Zitadellengürtel wird nicht bewertet; Grün heißt Overmatch
der Beplankung, nicht Zitadellentreffer.

## Detailansicht (Alt gedrückt)

Layout (rechts unter dem Fadenkreuz, linke obere Ecke Standard x +30, y +8):
- ohne Alt: Granate | Schild (29×29) kompakt, 4 px Abstand
- mit Alt: die Symbole werden ausgeblendet, an ihrer Stelle zwei beschriftete Schiffe
  (125×75, 8 px Abstand): „Me“ = eigenes Schiff (Ziel → ich), „Target“ = Ziel (ich → Ziel);
  Bug/Heck, Mitte, Deck grün/rot = gut/schlecht für mich. Die Schiffszeile liegt absolut an
  der Position der Symbole, damit nichts springt.
PenetrationCalculator liegt links unter dem Fadenkreuz (rechtsbündig bis x −19, ab y +34).

Position im Spiel per Ziehen über TTaroModUtils (wie BuildViewer): eigenes Schema
`ModSchemas/diedreibeiden-overmatcher.schema.json` (eigene `id`, nicht kopiert – TTaro warnt,
doppelte IDs sperren beide Mods), Schlüssel `diedreibeiden.overmatcher.position` und
`…disableDragDrop`. Ohne gespeicherte Position gilt der Rückfall aus `OVERMATCHER_SETTINGS`.
Abhängigkeit: ModForge + TTaroModUtils (Makros `TT_GET_PREF`, `TT_DRAGGABLE_POSITION`,
`TT_DRAGGABLE`). Referenz-Repos: github.com/AndrewTaro (ohne Lizenzdatei → nur als Referenz,
kein Code übernommen).

- 8 Bilder `detail_<bugheck>_<mitte>_<deck>.png` (g/r), erzeugt mit
  `tools/make_detail_icons.py` aus `assets/detail_ship_source.png` (weiße Flächen = Sektionen,
  Hintergrund und Umriss bleiben).
- Python wählt das Bild (`detail_icons`), fehlende Daten → Zeile ausgeblendet.
- „Mitte“ = dünnste Seitenplatte mittschiffs (`Cas_Belt`, `SSC_ConstrSide`), Teil der Ampel.

Abgleich Mitte mit dem Wiki: Thunderer/Conqueror 32, Moskva/Stalingrad 50, Petropavlovsk 40,
Des Moines/Hindenburg/Zao 30, Worcester 25, Minotaur/Neptune 16 – alle passend;
Bismarck 320 (deutsche BB ohne dünne Kasematte).

## Sichtbarkeit

Nur wenn eigenes Schiff **und** Gegner Kreuzer oder Schlachtschiff sind
(alle Kombinationen, inkl. BB–BB und CA–CA). DD, CV, U-Boote: keine Anzeige.
Nur gegnerisches Team.

## Anzeigeorte

1. Am Fadenkreuz, solange ein Ziel aufgeschaltet ist.
2. In der Teamübersicht am Rand (gegnerisches Team).

## Datenbasis

- Der Client gibt GameParams-Werte an Mods nicht heraus (Probe v2.2: Werte `None`,
  `__dict__` → `RuntimeError`). Daten kommen daher offline aus `content/GameParams.data`.
- Generator: `tools/gameparams.py` → `mod/res_mods/PnFMods/Overmatcher/ships.json`
  (`{gameVersion, ships: {name: [klasse, bug, deck, kaliber]}}`).
- Panzerung: Hull-Modul `armor` = `{(lage << 16) | material_id: mm}`, Lage 1 = außen;
  Material-Namen aus wowsunpack (MIT), `tools/data/collision_materials.json`.
  - Bug/Heck = `Bow_ConstrSide` (Fallback `St_ConstrSide`)
  - Deck = dünnste von `Cas_Deck`, `SSC_Deck`
  - `armourDeck`/`armourExtremities` sind in 15.9 nur Platzhalter `[-1, -1]`.
- Kaliber = größter `barrelDiameter` im Artillerie-Modul des letzten Upgrades.
- Abgeglichen mit dem Wiki (Stand 08/2024): Yamato 32/57, North Carolina 32/38, Minotaur 16/16,
  Colbert 16/16, Thunderer 32/32, Des Moines 27/30, Hindenburg 27/30, Bismarck 32/50,
  Slava 25/32, Riga 25/35, Fuso 26/35, Incomparable 25/51 – alle plausibel.
- Nicht abgedeckt: 21 Schiffe ohne `Cas_Deck`/`SSC_Deck` (v. a. leichte Kreuzer Stufe II–V,
  Event-Schiffe `PX*`) → keine Anzeige.
- Alternative Kanonenmodule (Mogami 155/203, Lion 406/419, FdG/Großdeutschland 406/420):
  verwendet wird das letzte Upgrade; welches Modul ein Spieler fährt, liefert die API nicht.
- `ships.json` gilt für genau eine Spielversion; bei Abweichung deaktiviert sich die Mod.

## Technik

- ModsAPI **v1.0** (Python 2.7, kein Entwickler-Schlüssel nötig).
- Ordner: `bin/<Build>/res_mods/PnFMods/Overmatcher/`, plus leere
  `res_mods/PnFModsLoader.py`.
- Gegnerliste über `battle.getPlayersInfo()` (nicht `getAllShips()` – liefert nur sichtbare Schiffe).

## Erkenntnisse Probe v1 (Client 15.9.0.13357625)

- `battle.getPlayersInfo()` liefert pro Spieler u. a. `teamId`, `shipId` (Entity),
  `shipParamsId` (GameParams-ID), `shipComponents` und `shipInfo`.
- `shipInfo.params` ist der **GameParams-Eintrag des Schiffs im Client**, inkl.
  `A_Hull.armourDeck`, `A_Hull.armourExtremities`, `A_Artillery`, `typeinfo`.
  Falls die Werte lesbar sind, entfällt der Offline-Daten-Generator (Probe v2).
- `Ship.subtype` liefert `'Cruiser'` (bestätigt); `shipInfo.subtypeIDS` z. B. `'IDS_BATTLESHIP'`.
- Eigenes Team `teamId` 0, Gegner 1 (Trainingsraum).
- Beim Nutzer laufen bereits ModForge, TTaroTeamPanel, Crosshair-Marks u. a. →
  Konfliktgefahr bei Teamliste und Fadenkreuz.

## Erkenntnisse Probe v2.1

- `getPlayersInfo()[pid]['shipInfo']` ist ein leeres Gerüst; gefüllt nur über `getPlayerShipInfo(pid)`.
- `getPlayerShipInfo(pid)`: `name` (Index, z. B. `PJSB018_Yamato_1944`), `level`, `subtype`
  (`'Cruiser'`/`'Battleship'`) bestätigt → Lookup-Schlüssel für die Datentabelle.
- `params.A_Hull.armourDeck` per Item-Zugriff `None`.

## Erkenntnisse 0.1.x im Client

- `open()` verlangt immer `(pfad, modus)`; Modus `'a'` nur für vorhandene Dateien.
- `print()` erscheint nicht im python.log, `utils.logInfo` schon.
- `utils.getModDir()` lieferte den Ordner `OvermatcherProbe`, solange dieser existierte;
  nach dem Löschen korrekt. Vermutlich Präfix-Zuordnung des Mod-Namens – Mod-Ordner nie
  mit einem Präfix eines anderen Mod-Namens benennen. Die Mod korrigiert den Pfad selbst.
- 0.1.2 im Client bestätigt: Hawaii gegen Minotaur ×2 und Yamato liefert die erwarteten Farben.

## Offene Punkte

| # | Punkt | Klärung durch |
|---|---|---|
| 1 | ~~Live-Zugriff auf Panzerung~~ – gesperrt (v2.2), Offline-Daten | erledigt |
| 2 | ~~Overmatch-relevante Platten~~ – `Bow_ConstrSide`, `Cas_Deck`/`SSC_Deck`, Wiki-Abgleich ok | erledigt |
| 3 | `shipComponents` aus `getPlayersInfo()` ist leer → Annahme „voll ausgebaut“ bleibt | – |
| 4 | Aufgeschaltetes Ziel erkennen | Prototyp |
| 5 | Teamliste: über ModForge-Override oder eigenes Panel, Konflikt mit TTaroTeamPanel | Prototyp |

## Umsetzungsreihenfolge

1. Probe-Mod (Datenstruktur klären)
2. Daten-Generator
3. Logik (fertig, getestet: `python3 -m unittest discover -s tests`)
4. Anzeige Teamübersicht (Fallback: eigenes Panel daneben)
5. Anzeige Fadenkreuz

## Risiken

- Patch alle 4–6 Wochen: Build-Ordner wechselt, Daten neu erzeugen, überschriebene UI-Dateien neu anpassen.
- Undokumentierte UI-Komponenten können ohne Vorwarnung entfallen.
- Fair Play: statische Daten, keine Zielhilfe – vermutlich zulässig, nicht von WG bestätigt.
