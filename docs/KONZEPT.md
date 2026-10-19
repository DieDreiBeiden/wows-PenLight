# Overmatcher – Konzept

Stand: 2026-10-19 · Client: WoWS EU · Verteilung: privat

## Ziel

Auf einen Blick erkennen, ob AP-Granaten Bug/Heck bzw. Deck overmatchen:
- **Granate** – ich als Angreifer gegen das Ziel
- **Schild** – der Gegner gegen mich

## Regeln

Overmatch: `Kaliber > 14,3 × Plattendicke` (Gleichstand = kein Overmatch).
Bug und Heck werden als gleich dick behandelt (ein Wert „bow“).

| Bug/Heck | Deck | Granate | Schild |
|---|---|---|---|
| ja | ja | Grün | Rot |
| nein | ja | Gelb | Gelb |
| ja | nein | Gelb *(Annahme)* | Gelb *(Annahme)* |
| nein | nein | Rot | Grün |

Die Zeile „Bug ja / Deck nein“ ist in der Ausgangsdefinition nicht enthalten
(kommt z. B. bei 460 mm gegen 38-mm-Decks vor). Festgelegt als Gelb,
änderbar über `BOW_ONLY_COLOR` in `src/overmatcher/logic.py`.

## Sichtbarkeit

Nur wenn eigenes Schiff **und** Gegner Kreuzer oder Schlachtschiff sind
(alle Kombinationen, inkl. BB–BB und CA–CA). DD, CV, U-Boote: keine Anzeige.
Nur gegnerisches Team.

## Anzeigeorte

1. Am Fadenkreuz, solange ein Ziel aufgeschaltet ist.
2. In der Teamübersicht am Rand (gegnerisches Team).

## Datenbasis

- Bevorzugt: live aus `shipInfo.params` im Client (siehe Erkenntnisse).
- Fallback: offline aus `GameParams.data` (Tool: `wowsunpack`), als JSON mitgeliefert.
- Annahme: Gegner fährt voll ausgebaute Module.
- Datenversion = Spielversion; Abweichung → Warnung statt falscher Farben.

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

## Offene Punkte

| # | Punkt | Klärung durch |
|---|---|---|
| 1 | Sind `armourDeck`/`armourExtremities` im Client lesbar? v2.1: `None` – Filterung oder Zugriffsfehler? | Probe v2.2 |
| 2 | Entsprechen `armourExtremities`/`armourDeck` der overmatch-relevanten Beplankung? | Abgleich bekannter Schiffe (Wiki) |
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
