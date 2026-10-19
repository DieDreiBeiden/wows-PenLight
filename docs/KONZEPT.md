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

- Hauptkaliber, Bug/Heck- und Deckdicke je Schiff, offline erzeugt aus
  `GameParams.data` (Tool: `wowsunpack`), als JSON mit der Mod ausgeliefert.
- Annahme: Gegner fährt voll ausgebaute Module.
- Datenversion = Spielversion; Abweichung → Warnung statt falscher Farben.

## Technik

- ModsAPI **v1.0** (Python 2.7, kein Entwickler-Schlüssel nötig).
- Ordner: `bin/<Build>/res_mods/PnFMods/Overmatcher/`, plus leere
  `res_mods/PnFModsLoader.py`.
- Gegnerliste über `battle.getPlayersInfo()` (nicht `getAllShips()` – liefert nur sichtbare Schiffe).

## Offene Punkte

| # | Punkt | Klärung durch |
|---|---|---|
| 1 | Welche Schiffs-ID liefert `getPlayerShipInfo`, welche Werte hat `subtype`? | Probe-Mod |
| 2 | Aufgeschaltetes Ziel erkennen (UI-Komponente `Target.flags`?) | Prototyp |
| 3 | Integration in die Teamliste nur über überschriebene Spieldateien möglich | Prototyp |
| 4 | Panzerungszonen aus GameParams sauber zuordnen | Daten-Generator |

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
