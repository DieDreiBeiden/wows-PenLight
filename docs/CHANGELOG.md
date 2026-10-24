# Changelog

Player-facing changes per release, in English. New entries go under "Unreleased"; the Release
workflow uses them as "What's new" and then moves them under the new version.

## Unreleased

- The edition without TTaroModUtils (standalone) is no longer released; releases contain one zip, `PenLight-<version>.zip`, which needs ModForge and TTaroModUtils. If you used the standalone edition, delete `gui/unbound2/PnFMods/PenLightTTaro.unbound` and `PnFMods/PenLight/Main.swf`.

## 0.4.0 – 2026-10-24

- New: display style option in TTaro Mod Config – **Classic** (shell / shield), **Modern** (status capsules, new default) and **Text only**.
- New: Modern detail view (Alt) with the plate thickness per zone and your shot (penetration, or calibre and overmatch limit).
- New: texts of Modern and Text only follow the client language (20 languages; needs LocalizationLoader, otherwise English).
- The standalone edition does not have the new display styles yet; it keeps the classic display.

## 0.3.2 – 2026-10-23

- Fixed: Nebraska, Delaware and Louisiana now use their hangar deck (32 / 38 / 38 mm) instead of a wrong 6 mm value.

## 0.3.1 – 2026-10-21

- PenLight is now shown only in the **aiming view** (binoculars / scope). In the normal third-person view it is hidden, including the gear button and the drag area.
- Both editions report version 0.3.1 to ModForge.

## 0.3.0 – 2026-10-21

- First public pre-release.
