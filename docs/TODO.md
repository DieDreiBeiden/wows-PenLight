# PenLight – To-Do

Stand: 2026-10-23. Probe-Builds entstehen im Branch `Test`, übernommen wird erst nach Freigabe.

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

## Branch `Test` (Probe, noch nicht übernommen)

- [ ] Status-Kapseln mit Animationen im Spiel testen
- [ ] Alt-Ansicht Variante A (ausgeklappte Kapseln) im Spiel testen, Textgrößen feinjustieren
- [ ] Texte in der Client-Sprache: mit und ohne LocalizationLoader prüfen; Übersetzungen für
      Thai, Koreanisch und Türkisch von Muttersprachlern prüfen lassen
- [ ] Munitionskürzel in den Kapseln lokalisieren (spieleigene `IDS_AMMOTYPE_*`), optional
- [ ] Nach Freigabe: Übernahme nach `main` und `main-standalone` (Standalone: Flash-Greiffläche
      an die Kapseln anpassen), Doku und README-Bilder

## Prüfen und Korrigieren

- [ ] IFHE-Erkennung im Spiel bestätigen (Logzeile `ammo he raw … mm, coeff …`)
- [ ] Ziehen mit der Maus in der Standalone-Fassung ohne TTaro testen
- [x] Deck von Nebraska, Delaware und Louisiana (vorher 6 mm): Hangar zählt jetzt (32/38/38 mm)
- [ ] Gegenprobe im Spiel: Panzerungsansicht Louisiana auf eine 6-mm-Fläche prüfen

## Veröffentlichung

- [ ] Lizenz festlegen
- [ ] Freigabe-Anfrage an Wargaming senden (Entwurf liegt vor)
- [ ] Anfrage an AndrewTaro (Nutzung von TTaroModUtils/ModForge)
- [ ] About-Bereich des Repos ausfüllen (Beschreibung, Website, Topics)
- [ ] Alten Branch `test/game-ammo-icons` auf GitHub löschen
