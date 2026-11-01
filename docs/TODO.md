# PenLight – To-Do

Stand: 2026-11-01. Probe-Builds entstehen im Branch `Test`, übernommen wird erst nach Freigabe.

## Neue Funktionen

- [x] **HE-Luftschlag gegen das Deck** – im Spiel getestet (Utrecht), in 0.5.0 übernommen (2026-11-01).
  Erkennung über `events.onWeaponTypeChanged` (`WeaponType.AIR_SUPPORT = 12`), Bombe aus
  `battle.getSelectedAmmoId(12)`, Rückfall auf `ships.json`.
  - Offen: Modifikatoren (Kapitänsfertigkeiten) auf den Bomben-Durchschlag; derzeit ohne Faktor.
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
- [x] README-Bilder für Modern und Nur Text (`styles.png`, seit 0.5.0 im Munitionsleisten-Design)
- [ ] Standard-Darstellung für Bestandsnutzer festlegen (derzeit Modern)

## Munitionsleisten-Design (seit 0.5.0)

- [x] Alle Darstellungen (Klassisch, Modern, Nur Text, Alt-Ansicht) im Stil der Munitionsleiste, Schild
      `planes_ap_damage`, Spiel-Symbole als Kopien in `PnFMods/PenLight/ammobar/game/` – im Spiel getestet,
      in 0.5.0 übernommen (2026-11-01); README, Fair Play und Quellenangabe angepasst.
- [ ] In der Freigabe-Anfrage an Wargaming die mitgelieferten Spiel-Symbole nennen
- [ ] Optional IFHE-Plakette: Fertigkeitssymbol `he_penetration` (IFHE) statt eigener Plakette
- [ ] Alte Symbole (Granate / Schild, Status-Kapseln) entfernen, falls der Schalter `ammoBarDesign`
      nicht mehr gebraucht wird

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
