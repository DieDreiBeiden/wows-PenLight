# PenLight – Konzept

Umbenannt von Overmatcher (seit HE/SAP mehr als nur Overmatch). Alle Kennungen
(Ordner, Slug `diedreibeiden.penlight`, ModPrefs-Datei, Unbound-Elemente) heißen jetzt PenLight;
alte Einstellungen werden nicht übernommen.

Stand: 2026-10-19 · Client: WoWS EU · Verteilung: privat

## Ziel

Auf einen Blick erkennen, ob AP-Granaten Bug/Heck bzw. Deck overmatchen:
- **Granate** – ich als Angreifer gegen das Ziel
- **Schild** – der Gegner gegen mich

## Regeln

Overmatch: `Kaliber > 14,3 × Plattendicke` (Gleichstand = kein Overmatch).
Bug und Heck werden als gleich dick behandelt (ein Wert „bow“).

Variante B (vom Nutzer gewählt): Bug/Heck ist Grundvoraussetzung, „überall“ erst, wenn auch
Mitte **und** Deck overmatcht werden. Normale Ansicht: Farbe = gut/schlecht für mich
(siehe „Farben der normalen Ansicht“); Alt-Detailansicht: Grün = Overmatch für Target und Me.

| Bug/Heck | Mitte und Deck | Granate (ich → Ziel) | Schild (Ziel → ich) |
|---|---|---|---|
| ja | beide ja | Grün + Stern – überall durch, auch gewinkelt | Rot + Warndreieck – Gegner kommt überall durch, ausweichen |
| ja | nicht beide | Gelb – gezielt auf Bug/Heck | Gelb – Bug/Heck schützen, auf Distanz Panzerung nutzen |
| nein | egal | Rot – nur Breitseite | Grün – aggressiv anwinkeln |

Mitte = dünnste Seitenplatte mittschiffs (`Cas_Belt`, `SSC_ConstrSide`). Fehlt der Wert,
entscheiden Bug/Heck und Deck allein.

Häufigkeit Stufe VIII–X (alle Paarungen BB/CA, ungewichtet): alle drei 10,5 %,
Bug ohne alles 16,4 %, Bug nicht 73,1 % → Granate grün/gelb/rot 10,5/16,4/73,1 %.

Bewusste Vereinfachung: Der Zitadellengürtel wird nicht bewertet; Grün heißt Overmatch
der Beplankung, nicht Zitadellentreffer.

## Farben der normalen Ansicht (Nutzerentscheidung, zuletzt geändert)

Granate und Schild färben nach **gut/schlecht für mich**: Granate grün = ich komme überall durch,
Schild rot = das Ziel kommt überall durch (vorher war der Schild zwischenzeitlich „grün =
Overmatch“, das war im Gefecht verwirrend). Die Alt-Detailansicht bleibt bei „grün = Overmatch“
für Target und Me. Form der Granate = Overmatch-Umfang (voll / nur Spitze / Schrägstrich);
Form des Schilds = Schutz (voll und heil / teilweise / voll aber gebrochen) – ein
durchgestrichener grüner Schild wirkte irreführend (Nutzerentscheidung, Variante S1 nur mit Bruch bei Rot). Extremfälle zusätzlich mit Zeichen (Variante P3): Stern an der grünen Granate,
Warndreieck am roten Schild (`mark_star.png`, `mark_warning.png`, weiß mit dunklem Rand),
blinkt beim Aufschalten 4 × 0,25 s auf (`$Animation`, Einstellungen `mark*`).

## HE und SAP (geladene Munition)

Main.py liest die geladene Munition über die ModsAPI (`battle.getSelectedAmmoId(constants.WeaponType.ARTILLERY)`
beim Gefechtsstart, `events.onArtilleryAmmoChanged(ammoId)` bei jedem Wechsel, Daten aus
`battle.getAmmoParams(ammoId)`: `ammoType` AP/HE/CS, Durchschlag `alphaPiercingHE` bzw.
`alphaPiercingCS`; Muster wie PenetrationCalculator). Bei HE/SAP gilt Durchschlag ≥ Platte
(Gleichstand = durch, Nutzervorgabe), Durchschlag immer auf ganze mm abgerundet (`floor_mm`).
IFHE: HE der Hauptbatterie wird mit `battle.getAmmoModifiers().GMPenetrationCoeffHE` multipliziert
(Faktor des eigenen Schiffs inkl. Kommandant, wie PenetrationCalculator; nicht lesbar -> 1.0), SAP nicht.
Faktor > 1 -> Payload `ifhe: true`, Zusatzplakette `tag_ifhe.png` links unten an der HE-Granate.
Im Spiel zu prüfen: Logzeile `ammo he raw … mm, coeff …` (Faktor vorhanden und ≈ 1.25 mit IFHE?).
Ampel nur für die Granate:
green (Bug/Heck und Deck), bow, deck, red. Schild und Me bleiben AP-Overmatch des Gegners.
HE/SAP gilt auch für Zerstörer und Träger (Ziel `PEN_CLASSES`: Zerstörer, Kreuzer, Schlachtschiffe, Träger;
eigenes Schiff `PEN_SHOOTER_CLASSES`: Zerstörer, Kreuzer, Schlachtschiffe – Träger nur als Ziel). Ohne Kreuzer/Schlachtschiff-Paarung: Schild
grau, Me-Teil von `detail` = -1. `ships.json` enthält dafür auch Zerstörer und Träger (Träger ohne
Hauptkaliber, `null`). U-Boote werden nicht bewertet (Nutzervorgabe; getaucht ohnehin nicht von HE treffbar).
Payload: `ammo` (ap/he/sap); Granate und Ziel-Teil von `detail` gelten für die geladene Munition.
Eigene Zeichnungen `he_*.png`, `sap_*.png` nach den Spiel-Symbolen (HE Aufschlag mit Rauch und
Blitz, SAP Aufschlag mit Splittern); Spitze in Ampelfarbe (Spiel-Typfarben wirkten neben der Ampel
verwirrend), dazu Band = Bug/Heck, Ring = Deck. Plaketten
`tag_ap/he/sap.png`, Mini-Icons `label_target_<he|sap>_*.png`.

## Icons: Barrierefreiheit (Variante A2)

Prüfung nach WCAG 2.1 AA (Farbkontrast, Farbe als einziges Merkmal): Im Standardschema waren
die Ampelfarben bei Deuteranopie kaum zu unterscheiden (ΔE2000 Grün–Orange 8,2), und die
Farbflächen hatten gegen das Metall fast keinen Helligkeitskontrast (1,0–1,3). Umsetzung:
- Zustand auch über die Form: je Icon drei Segmente (Granate: Spitze, Band, Heckring; Schild:
  Fuß, unterer, oberer Sparren). Grün = alle gefüllt, Orange = Granate Spitze bzw. Schild Fuß +
  unterer Sparren, Rot = Schrägstrich + leere Segmente dunkel in Zustandsfarbe getönt, Grau = leer.
- Farbsegmente auf dunklem Grund mit dunklen Trennlinien (Kontrast Grün 7,1, Orange 5,5, Rot 3,3).
- Farbenblind-Blau kräftiger (#2B8CE8), damit es sich vom Grau abhebt.

## Darstellung (Option, Probe im Branch `Test`)

Option „Darstellung“ in TTaro Mod Config (`diedreibeiden.penlight.style`, Rückfall
`PENLIGHT_SETTINGS.defaultStyle`, derzeit Modern):

| Wert | Name | Normal | Mit Alt |
|---|---|---|---|
| 0 | Klassisch | Granate / Schild | gezeichnete Schiffe bzw. Silhouetten |
| 1 | Modern | Status-Kapseln (oben ich → Ziel, unten Ziel → ich, Punkte Bug/Heck, Mitte, Deck) | ausgeklappte Kapseln mit mm-Werten |
| 2 | Nur Text | zwei Zeilen, z. B. „HE: Bow/Stern“, „Enemy AP: everywhere“, in der Ampelfarbe | Kopfzeile, Zonenname und Wert als Text |

Nicht bewertete Paarungen (Python: `grey`, Zonen −1, z. B. Schild gegen Träger) erscheinen in allen
Darstellungen grau. Textfarbe per `colorTransform` mit Multiplikatoren (`PENLIGHT_TEXT_CT`), damit
der Schatten der Schrift dunkel bleibt.

Lesbarkeit „Nur Text“ (Prüfung 2026-10-24, Hintergründe aus Spiel-Screenshots gemessen):
- Ohne Unterlage verfehlt Text auf typischem Wasser (55,60,58) teils den Kontrast 4,5 : 1 (Rot 2,9,
  Farbenblind-Blau 3,2, -Orange 2,9), vor heller Gischt fast alle Farben (1,0–2,0). Daher jede Zeile
  auf dunkler Unterlage 0xD90E1012 (85 %) und hellere Textfarben (Rot #FF7060, Grau #B0B5BA,
  Blau #58AAFF, Orange #F58028): alle Farben ≥ 4,8 : 1 auch vor weißer Gischt.
- Standardpalette bei Deuteranopie: Grün/Rot kaum unterscheidbar (ΔE ≈ 8). Im Text trägt das Wort
  die Aussage („everywhere“, „Bow/Stern“), Farbe ist zusätzlich; sonst Farbenblind-Palette (ΔE ≥ 22).
- Ohne Ziel nur „HE“ / „Enemy AP“ in Grau, mit Ziel und ohne Bewertung „not rated“ statt „-“.
- Schrift 13 px fett (Spielschrift); größer über die Option Skalierung.

## Detailansicht (Alt gedrückt)

Layout (rechts unter dem Fadenkreuz, linke obere Ecke Standard x +30, y +8):
- ohne Alt: Granate | Schild (29×29) kompakt, 4 px Abstand, immer sichtbar (solange das
  Fadenkreuz sichtbar ist); Ampelfarben nur bei aufgeschaltetem, bewertetem Ziel, sonst grau
  (kein Ziel, keine Daten, U-Boot, AP gegen bzw. von Zerstörer/Träger)
- mit Alt (nur mit Bewertung, sonst bleiben die grauen Symbole): die Symbole werden ausgeblendet, an ihrer Stelle zwei Schiffe untereinander
  (oben Target, unten Me; 125×75, 4 px Abstand), freistehend ohne Hintergrund, Rumpf metallisch grau mit dunkler Kontur wie die
  Icons; oben links graue Mini-Granate + „TARGET“ = Ziel (ich → Ziel, unter der Granate) bzw.
  Mini-Schild + „ME“ = eigenes Schiff (Ziel → ich, unter dem Schild); 16 Bilder
  `detail_<me|target>_<b>_<m>_<d>.png`, Schrift DejaVu Sans Bold 8,5 px (freie Lizenz);
  Bug/Heck, Mitte, Deck grün/rot = Overmatch/kein Overmatch, für Target und Me gleich.
  Die Mini-Icons der Beschriftung tragen die Ampelfarbe von Granate bzw. Schild. Die Schiffszeile liegt absolut an
  der Position der Symbole, damit nichts springt.
Prototyp Silhouetten (`useSilhouettes` in `PENLIGHT_SETTINGS`, Standard an): statt der
gezeichneten Schiffe die Spiel-Silhouetten `img://gui/ship_bars/<shortName>_h.png` (wie der
Lebensbalken unten links, `own_ship_health.unbound`; `shortName` aus `shipInfo.ship.shortName`,
Ziel über `vehicleInfo.shipInfoEntityId`). Lagen mit Maske + `colorTransform`: Rumpf Heck
0–22 %, Mitte 22–78 %, Bug 78–100 % der Bildbreite (Näherung, für alle Schiffe gleich);
Deck = alles oberhalb der Decklinie (`deckLine` 0,71 der Bildhöhe, gemessen an Rhode Island,
Vermont, Trento; der erste Prototyp mit Balken über der Silhouette passte optisch nicht).
Beschriftung `label_<target|me>_<farbe>.png` (186×24, Mini-Icon 14 px + Text 13 px mittig, Text in
Zielgröße gezeichnet für Schärfe). Granate auf Schildhöhe skaliert (`SHELL_SCALE`).
Rahmen (Variante B3, Nutzerwahl): je Schiff ein dunkles Band über die ganze Höhe, das zu den
Seiten ausläuft, Haarlinien oben/unten, leicht aufgehellte Kopfzeile mit Trennlinie
(`frame_band/line/head.png` aus `tools/make_detail_icons.py`); Silhouette mit Kontur und
weichem Schatten per `dropShadow`-Filter (`$PenLightSilhouetteFX`).
Unter jeder Silhouette der Schiffsname in der Spielschrift (`$TextDefaultBold13NM`,
`toUpper(tr(ship.nameIDS))` wie im Spiel-Lebensbalken), mittig. Ohne Silhouetten-Namen gelten die `detail_*.png`.
Die Silhouetten werden nicht mitgeliefert (Spieldateien), passen also nach jedem Patch.
PenetrationCalculator liegt links unter dem Fadenkreuz (rechtsbündig bis x −19, ab y +34).

Optionen (TTaro Mod Config, Seite `diedreibeiden.penlight`; eigenes Zahnrad
`TT_ConfigButtonElement` links neben der Anzeige wie bei BuildViewer):
- `penlight.detailMode` 0 = Detail mit Alt, 1 = immer (ersetzt die Symbole bei Bewertung)
- Silhouetten an/aus nur als `useSilhouettes` in `PENLIGHT_SETTINGS` (aus der Optionsseite
  entfernt, Nutzerentscheidung)
- `penlight.colorMode` 0 = Standard, 1 = Farbenblind (Okabe-Ito: Blau #2B8CE8 = Overmatch,
  Gelb #F0E442 = nur Bug/Heck, Orange #D55E00 = kein Overmatch); Icons mit Präfix `cb_`,
  Silhouetten per `PENLIGHT_CT_CB`. Die gezeichneten Ersatzbilder bleiben Standardfarben.
- `penlight.scale` 0,5–2,0 (scaleX/scaleY der ganzen Anzeige)
Beschriftungen: vorhandene TTaro-Texte (`IDS_TT_DISPLAY_MODE`, `IDS_TT_UI_SCALE`, …) plus
eigene `IDS_OM_*` in `texts/<sprache>/penlight.mo` (wie TTaroModUtils; Quelle
`tools/data/texts.json`, erzeugt von `tools/make_texts.py`).

Position im Spiel per Ziehen über TTaroModUtils (wie BuildViewer): eigenes Schema
`ModSchemas/diedreibeiden-penlight.schema.json` (eigene `id`, nicht kopiert – TTaro warnt,
doppelte IDs sperren beide Mods), Schlüssel `diedreibeiden.penlight.position` und
`…disableDragDrop`. Ohne gespeicherte Position gilt der Rückfall aus `PENLIGHT_SETTINGS`.
Abhängigkeit: ModForge + TTaroModUtils (Makros `TT_GET_PREF`, `TT_DRAGGABLE_POSITION`,
`TT_DRAGGABLE`). Referenz-Repos: github.com/AndrewTaro (ohne Lizenzdatei → nur als Referenz,
kein Code übernommen).

- 16 Bilder `detail_<me|target>_<bugheck>_<mitte>_<deck>.png` (g/r), erzeugt mit
  `tools/make_detail_icons.py` (gezeichnet; das frühere Grund-Icon
  `assets/detail_ship_source.png` wird nicht mehr verwendet).
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

1. Am Fadenkreuz, immer; eingefärbt, solange ein Ziel aufgeschaltet ist.
2. In der Teamübersicht am Rand (gegnerisches Team).

## Datenbasis

- Der Client gibt GameParams-Werte an Mods nicht heraus (Probe v2.2: Werte `None`,
  `__dict__` → `RuntimeError`). Daten kommen daher offline aus `content/GameParams.data`.
- Generator: `tools/gameparams.py` → `mod/res_mods/PnFMods/PenLight/ships.json`
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
- Ordner: `bin/<Build>/res_mods/PnFMods/PenLight/`, plus leere
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
- Die Sandbox kennt die Builtins `globals()` (und vermutlich `locals()`/`vars()`) nicht: ein
  Aufruf beim Laden bricht die ganze Mod ab (`NameError: name 'globals' is not defined`, nur graue
  Symbole, PenLight 2026-10-21). Vom Client gesetzte Namen per `try: name / except NameError:` prüfen.
  Die Tests laufen deshalb mit Builtins ohne `globals`/`locals`/`vars`.
- 0.3.0 im Client bestätigt: Mod lädt, Ziehen mit der Maus über die vergrößerte Greiffläche
  funktioniert (TTaro-Fassung).
- 0.3.1: Anzeige (samt Zahnrad und Greifflaeche) nur in der Zielansicht, `camera.isBinocular` /
  `camera.evIsBinocularChanged` (Muster wie TTaros SmokeMarker); in der Aussenperspektive ausgeblendet.
  Der Flash-Griff der Standalone-Fassung ohne TTaro kennt die Kameraansicht nicht und bleibt aktiv.
  Im Client bestätigt (TTaro-Fassung).
- Unbound 2 zeichnet `vblock` nicht: der Container bleibt samt Inhalt unsichtbar, ohne Eintrag im
  python.log (Probe Status-Kapseln, 2026-10-24, eingegrenzt mit Diagnose-Plakette). Untereinander
  stapelt ein normaler `block`, nebeneinander `hblock`. Test `tests/test_unbound.py` verbietet `vblock`.
  Fehler in `.unbound`-Dateien erscheinen generell nicht im python.log; eingrenzen per sichtbarer
  Diagnose (Testbild, Zustandswerte als Text) direkt in der Anzeige.
- Text per `scaleX`/`scaleY` verkleinern taugt nicht: die Schrift rendert weich und schwer lesbar,
  und untereinander gestapelte `tf` in einem skalierten Block ueberlappen (Alt-Ansicht der Kapseln,
  2026-10-24). Besser Schriftklassen in Originalgroesse (`$TextDefault12NM` und groesser) und Zeilen
  absolut positionieren.
- Bekanntes Problem: Nebraska, Delaware und Louisiana haben laut `gameparams.py` ein 6-mm-Deck
  (dünnste `Cas_Deck`-Platte, vermutlich ein Kleinteil statt des eigentlichen Decks). Als Ziel
  dadurch Deck für jede HE/SAP durchschlagbar und ab 86 mm AP overmatcht. In den Release-Notes als
  Known issue geführt; Deck-Erkennung später prüfen.

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
