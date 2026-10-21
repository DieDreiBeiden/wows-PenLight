# Overmatcher – Konzept

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
für Target und Me. Die Form der Icons zeigt weiter den Overmatch-Umfang (voll / teilweise /
Schrägstrich). Extremfälle zusätzlich mit Zeichen (Variante P3): Stern an der grünen Granate,
Warndreieck am roten Schild (`mark_star.png`, `mark_warning.png`, weiß mit dunklem Rand),
blinkt beim Aufschalten 4 × 0,25 s auf (`$Animation`, Einstellungen `mark*`).

## Icons: Barrierefreiheit (Variante A2)

Prüfung nach WCAG 2.1 AA (Farbkontrast, Farbe als einziges Merkmal): Im Standardschema waren
die Ampelfarben bei Deuteranopie kaum zu unterscheiden (ΔE2000 Grün–Orange 8,2), und die
Farbflächen hatten gegen das Metall fast keinen Helligkeitskontrast (1,0–1,3). Umsetzung:
- Zustand auch über die Form: je Icon drei Segmente (Granate: Spitze, Band, Heckring; Schild:
  Fuß, unterer, oberer Sparren). Grün = alle gefüllt, Orange = Granate Spitze bzw. Schild Fuß +
  unterer Sparren, Rot = Schrägstrich + leere Segmente dunkel in Zustandsfarbe getönt, Grau = leer.
- Farbsegmente auf dunklem Grund mit dunklen Trennlinien (Kontrast Grün 7,1, Orange 5,5, Rot 3,3).
- Farbenblind-Blau kräftiger (#2B8CE8), damit es sich vom Grau abhebt.

## Detailansicht (Alt gedrückt)

Layout (rechts unter dem Fadenkreuz, linke obere Ecke Standard x +30, y +8):
- ohne Alt: Granate | Schild (29×29) kompakt, 4 px Abstand, immer sichtbar (solange das
  Fadenkreuz sichtbar ist); Ampelfarben nur bei aufgeschaltetem, bewertetem Ziel, sonst grau
  (kein Ziel, Zerstörer/Träger/U-Boot, keine Daten)
- mit Alt (nur mit Bewertung, sonst bleiben die grauen Symbole): die Symbole werden ausgeblendet, an ihrer Stelle zwei Schiffe untereinander
  (oben Target, unten Me; 125×75, 4 px Abstand), freistehend ohne Hintergrund, Rumpf metallisch grau mit dunkler Kontur wie die
  Icons; oben links graue Mini-Granate + „TARGET“ = Ziel (ich → Ziel, unter der Granate) bzw.
  Mini-Schild + „ME“ = eigenes Schiff (Ziel → ich, unter dem Schild); 16 Bilder
  `detail_<me|target>_<b>_<m>_<d>.png`, Schrift DejaVu Sans Bold 8,5 px (freie Lizenz);
  Bug/Heck, Mitte, Deck grün/rot = Overmatch/kein Overmatch, für Target und Me gleich.
  Die Mini-Icons der Beschriftung tragen die Ampelfarbe von Granate bzw. Schild. Die Schiffszeile liegt absolut an
  der Position der Symbole, damit nichts springt.
Prototyp Silhouetten (`useSilhouettes` in `OVERMATCHER_SETTINGS`, Standard an): statt der
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
weichem Schatten per `dropShadow`-Filter (`$OvermatcherSilhouetteFX`).
Unter jeder Silhouette der Schiffsname in der Spielschrift (`$TextDefaultBold13NM`,
`toUpper(tr(ship.nameIDS))` wie im Spiel-Lebensbalken), mittig. Ohne Silhouetten-Namen gelten die `detail_*.png`.
Die Silhouetten werden nicht mitgeliefert (Spieldateien), passen also nach jedem Patch.
PenetrationCalculator liegt links unter dem Fadenkreuz (rechtsbündig bis x −19, ab y +34).

Branch `main-standalone` erkennt TTaroModUtils selbst (Nutzerwunsch): Das ModForge-Manifest hat
zwei `<ubMountInBattle>` mit `<requires mods="TTaroModUtils"/>` bzw. `"not TTaroModUtils"`.
Mit TTaro wird `OvermatcherTTaroRoot` (OvermatcherTTaro.unbound) eingehängt: TTaro-Optionsseite,
Zahnrad und Ziehen wie auf `main`, Einstellungen als `_ext` an `OvermatcherRoot`. Ohne TTaro
hängt `OvermatcherRoot` direkt (Einstellungen aus Main.py). Main.py prüft dieselbe Bedingung
(`PnFMods/TTaroModUtils/Main.py` vorhanden) und schaltet dann Tasten und Main.swf-Greiffläche ab.
TTaros interne Technik (Sandbox-Umgehung über `xml.sax.saxutils.os`, verschlüsselte Namen) wird
bewusst nicht übernommen; genutzt werden nur dessen veröffentlichte Makros/Elemente.
Offene Frage: Der Client liest alle Dateien in `gui/unbound2/PnFMods/`; ohne TTaro sind die
TT_-Makros in OvermatcherTTaro.unbound unbekannt – ob das nur einen Logeintrag erzeugt, ist ungetestet.

Ohne TTaro (ModForge bleibt für das Einhängen
der Anzeige nötig – es ist laut README zum Mitliefern in Mod-Paketen gedacht):
Einen offiziellen Rückkanal Unbound → Python gibt es in der ModsAPI nur über einen Flash-Teil
(`flash.addExternalCallback`); TTaro nutzt dafür interne Client-Zugriffe. Deshalb kein
Optionsmenü per Maus, sondern Tastenkürzel über `events.onKeyEvent` (offiziell):

| Strg+Alt + | Wirkung |
|---|---|
| Pfeiltasten | Anzeige verschieben, 5 px (mit Umschalt 1 px) |
| Pos1 | Position zurücksetzen (Mitte +30 / +8) |
| D | Detailansicht: mit Alt ↔ immer |
| F | Farben: Standard ↔ Farbenblind |
| + / − | Größe in 0,1-Schritten, 0,5–2,0 |

Drag & Drop per Maus über einen Flash-Teil (`Main.swf`, Quelle `src/as3/Main.as`, offizielle
FlashAPI): unsichtbare Greiffläche über Granate | Schild auf `gameAPI.stage`, Rahmen beim
Überfahren; Python → Flash `omSetHandle [x, y, b, h, aktiv]`, Flash → Python `omDragMove [x, y]`
(Anzeige folgt live) und `omDragEnd [x, y]` (speichern). x/y = Abstand zur Bildschirmmitte.
Kompiliert mit Apache Flex 4.16.1 gegen `wows_library.swc` (extern, der Client stellt `ModBase`),
SWF-Version 13 wie die Spieldateien.
Gespeichert in `(wows)/ModPrefs/diedreibeiden-overmatcher.json` (Rückfall: Mod-Ordner),
übergeben an die Anzeige als `omData.settings` ({x, y, detailMode, colorMode, scale}).
Farbenblind-Schema: an Okabe-Ito angelehnt, Blau #2B8CE8 = Overmatch, Gelb #F0E442 = nur Bug/Heck,
Orange #D55E00 = kein Overmatch (Icons mit Präfix `cb_`, Silhouetten per `OVERMATCHER_CT_CB`).
Silhouetten an/aus nur als `useSilhouettes` in `OVERMATCHER_SETTINGS`.

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
