# -*- coding: utf-8 -*-
"""Overmatch-Ampel. Muss unter Python 2.7 (Spielclient) und 3.x (Tests) laufen."""

OVERMATCH_RATIO = 14.3

GREEN = 'green'
YELLOW = 'yellow'
RED = 'red'

# Werte von Ship.subtype bzw. GameParams 'species'; per Probe-Mod zu bestaetigen.
RELEVANT_CLASSES = frozenset(['Cruiser', 'Battleship'])

# Ampel nach Spieler-Definition (docs/KONZEPT.md, Variante B). Bug/Heck ist die
# Grundvoraussetzung; Gruen erst, wenn auch Mitte und Deck overmatcht werden.
# Farben der normalen Ansicht = gut / schlecht fuer mich (Granate: ich -> Ziel, Schild: Ziel -> ich).
#   Bug/Heck  Mitte+Deck   Granate                    Schild
#   ja        beide ja     gruen (ich komme durch)    rot   (Ziel kommt ueberall durch)
#   ja        nicht beide  gelb                       gelb
#   nein      egal         rot                        gruen (Ziel kommt nicht durch)
# Die Alt-Detailansicht faerbt dagegen fuer Target und Me gleich: gruen = Overmatch (detail_icons).
# Fehlt der Mitte-Wert, entscheiden Bug/Heck und Deck allein.


def overmatches(caliber_mm, armor_mm):
    return caliber_mm > armor_mm * OVERMATCH_RATIO


LEVEL_COLORS = (RED, YELLOW, GREEN)


def _level(caliber_mm, ship):
    """2 = alle Zonen, 1 = nur Bug/Heck (plus ggf. weitere), 0 = Bug/Heck nicht."""
    if not overmatches(caliber_mm, ship['bow']):
        return 0
    rest = [ship['deck']] + ([ship['mid']] if ship.get('mid') is not None else [])
    return 2 if all(overmatches(caliber_mm, mm) for mm in rest) else 1


def attack_color(my_caliber_mm, target):
    """Granate: kann ich das Ziel overmatchen? target: dict mit 'bow', 'deck', optional 'mid'."""
    return LEVEL_COLORS[_level(my_caliber_mm, target)]


def defense_color(enemy_caliber_mm, me):
    """Schild: kann der Gegner mich overmatchen? Farbe = gut fuer mich: rot = ja, ueberall."""
    return DEFENSE_COLORS[_level(enemy_caliber_mm, me)]


DEFENSE_COLORS = (GREEN, YELLOW, RED)


def is_relevant(my_class, enemy_class):
    return my_class in RELEVANT_CLASSES and enemy_class in RELEVANT_CLASSES


def zone_detail(caliber_mm, ship):
    """Detailansicht: [bug, mitte, deck] je 1 (overmatch), 0 (nein), -1 (keine Daten)."""
    out = []
    for zone in ('bow', 'mid', 'deck'):
        mm = ship.get(zone)
        out.append(-1 if mm is None else int(overmatches(caliber_mm, mm)))
    return out


def detail_icons(detail):
    """Bildnamen der Detailansicht (ohne .png) fuer [ich->ziel..., ziel->ich...].

    Farbe wie die Ampel: g = Overmatch, r = kein Overmatch (Target und Me gleich).
    Fehlt eine Zone (-1), wird fuer diese Zeile kein Bild angezeigt ('').
    """
    def name(prefix, values):
        if -1 in values:
            return ''
        return prefix + '_'.join('g' if v else 'r' for v in values)
    # Granate = Ziel ("Target"), Schild = eigenes Schiff ("Me"); Bilder sind beschriftet
    return name('detail_target_', detail[:3]), name('detail_me_', detail[3:])


def evaluate(me, enemy):
    """me/enemy: dict mit 'class', 'caliber', 'bow', 'deck', optional 'mid' (mm).

    Liefert None, wenn die Paarung nicht angezeigt werden soll.
    """
    if not is_relevant(me['class'], enemy['class']):
        return None
    return {
        'attack': attack_color(me['caliber'], enemy),
        'defense': defense_color(enemy['caliber'], me),
        'detail': zone_detail(me['caliber'], enemy) + zone_detail(enemy['caliber'], me),
    }
