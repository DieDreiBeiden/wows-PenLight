# PenLight – To-Do

Stand: 2026-10-24. Probe-Builds entstehen im Branch `Test`, übernommen wird erst nach Freigabe.

## Neue Funktionen

- [ ] **HE-Luftschlag gegen das Deck**
  - Daten: `gameparams.py` liest je Schiff den HE-Bomben-Durchschlag des Luftschlags
    (`A_AirSupport` → Flugzeug → `bombName`, `alphaPiercingHE`) und schreibt ihn nach `ships.json`.
    Betrifft rund 20 Flugzeugtypen, fast nur niederländische Kreuzer (z. B. Gouden Leeuw 37 mm,
    Prins van Oranje 46,3 mm); die übrigen Luftschläge sind Wasserbomben gegen U-Boote.
  - Anzeige: bei gewähltem Luftschlag bewertet die obere Kapsel nur das Deck (eigenes Kürzel, z. B.
    „AS“), Alt-Ansicht mit Bomben-Durchschlag und Deckdicke.
  - Zuerst Probe-Build: Waffentyp beim Wechsel auf den Luftschlag und Verhalten des aufgeschalteten
    Ziels ins Log schreiben.
  - Offen: Modifikatoren (Kapitänsfertigkeiten) auf den Bomben-Durchschlag.
- [ ] **PenLight für Flugzeugträger**
  - Entscheidung offen: Teil von PenLight oder eigene Mod „PenLightCV“.
  - Zu klären: was bewertet wird (Bomben, Raketen, Torpedos bzw. Durchschlag gegen Deck und
    Seite) und wie die Anzeige im Flugzeugmodus aussieht.

## Darstellungen (Klassisch / Modern / Nur Text)

- [x] Status-Kapseln mit Animationen, Alt-Ansicht Variante A, Option Darstellung, Nur Text mit
      Unterlage – im Spiel getestet, nach `main` übernommen (2026-10-24)
- [ ] Texte in der Client-Sprache mit LocalizationLoader im Spiel prüfen; Übersetzungen für
      Thai, Koreanisch und Türkisch von Muttersprachlern prüfen lassen
- [ ] Munitionskürzel in den Kapseln lokalisieren (spieleigene `IDS_AMMOTYPE_*`), optional
- [ ] README-Bilder für Modern und Nur Text (eigener Hintergrund, keine Spielgrafik)
- [ ] Standard-Darstellung für Bestandsnutzer festlegen (derzeit Modern)

## Redesign „Munitionsleiste“ (Variante 1, vorgemerkt 2026-11-01)

- [ ] Alle Darstellungen (Klassisch, Modern, Nur Text, Alt-Ansicht) im Stil der Munitionsleiste:
      Spiel-Symbol der geladenen Munition (AP / HE / SAP, Luftschlag: HE-Bombe) in Farbe im Slot,
      Ampelfarbe im Rahmen, drei Zonen-Balken bzw. -Punkte; ohne Ziel die `inactive`-Symbole.
- [x] Spiel-Symbole per `img://` nicht erreichbar (Probe a87b0b9). Entscheidung 2026-11-01: Kopien der
      benötigten Symbole liegen in `PnFMods/PenLight/ammobar/game/` (aus dem WoWs Unpacker)
- [ ] Vor Übernahme nach `main`: README, Fair-Play-Abschnitt und CLAUDE.md anpassen („keine
      Spielgrafiken“ gilt nicht mehr), Quellenangabe Wargaming, in der Freigabe-Anfrage nennen
- [ ] Unterer Teil „Ziel → ich“: Schild der Kapitänsfertigkeit `planes_ap_damage`
      (`crew_commander/skills/`), neutral hellgrau wie die Granaten, ohne Ziel abgedunkelt;
      Ampelfarbe nur in Rahmen, Balken und Punkten. Ausgewählt 2026-11-01. Rückfall bei fehlendem
      Bild: eigenes Schild.
- [ ] Optional IFHE-Plakette: Fertigkeitssymbol `he_penetration` (IFHE) statt eigener Plakette
- [ ] Probe 1 auf `Test` (Schalter `ammoBarDesign`): Pfade der Spiel-Symbole, Aussehen aller Darstellungen
      im Spiel prüfen

## Standalone (Branch `Test-Standalone`, Experiment, nicht veröffentlicht)

- [ ] Darstellungen per Strg+Alt+S und Flash-Greiffläche je Darstellung im Spiel testen, mit und
      ohne TTaroModUtils; Ziehen mit der Maus ohne TTaro bestätigen
- [ ] Alten Branch `main-standalone` auf GitHub löschen (manuell; Inhalt steckt in `Test-Standalone`)

## Prüfen und Korrigieren

- [ ] IFHE-Erkennung im Spiel bestätigen (Logzeile `ammo he raw … mm, coeff …`)
- [x] Deck von Nebraska, Delaware und Louisiana (vorher 6 mm): Hangar zählt jetzt (32/38/38 mm)
- [ ] Gegenprobe im Spiel: Panzerungsansicht Louisiana auf eine 6-mm-Fläche prüfen

## Veröffentlichung

- [ ] Lizenz festlegen
- [ ] Freigabe-Anfrage an Wargaming senden (Entwurf liegt vor)
- [ ] Anfrage an AndrewTaro (Nutzung von TTaroModUtils/ModForge)
- [ ] About-Bereich des Repos ausfüllen (Beschreibung, Website, Topics)
- [ ] Alten Branch `test/game-ammo-icons` auf GitHub löschen
