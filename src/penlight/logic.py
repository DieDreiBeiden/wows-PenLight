# -*- coding: utf-8 -*-
"""Overmatch-Ampel. Muss unter Python 2.7 (Spielclient) und 3.x (Tests) laufen."""

OVERMATCH_RATIO = 14.3

GREEN = 'green'
YELLOW = 'yellow'
RED = 'red'

# Werte von Ship.subtype bzw. GameParams 'species'; per Probe-Mod zu bestaetigen.
RELEVANT_CLASSES = frozenset(['Cruiser', 'Battleship'])
# HE/SAP-Durchschlag wird gegen jede Klasse mit Daten bewertet (eigenes Schiff: jede Klasse mit
# geladener HE/SAP); AP-Overmatch und Schild bleiben bei Kreuzern und Schlachtschiffen.
PEN_CLASSES = frozenset(['Destroyer', 'Cruiser', 'Battleship', 'AirCarrier', 'Submarine'])
GREY = 'grey'

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


# HE/SAP: Durchschlag je Granate (alphaPiercingHE x IFHE-Faktor / alphaPiercingCS), abgerundet (floor_mm).
# Gleichstand zaehlt als Durchschlag (Nutzervorgabe). Ampel nur fuer das Ziel, Zonen Bug/Heck und Deck:
#   Bug/Heck  Deck   Zustand
#   ja        ja     green  (dazu Stern wie bei AP)
#   ja        nein   bow    (orange, Spitze gefuellt)
#   nein      ja     deck   (orange, Band + Ring gefuellt)
#   nein      nein   red    (Schraegstrich)
PEN_AMMO = ('he', 'sap')


def floor_mm(value):
    """Durchschlag in ganzen mm, immer abgerundet; die Toleranz faengt Gleitkomma-Reste (39.99999).
    Ohne math-Modul (Import in der Client-Sandbox ungeprueft); Werte sind nie negativ."""
    return int(value + 1e-6)


def penetrates(pen_mm, armor_mm):
    return pen_mm >= armor_mm


def pen_detail(pen_mm, ship):
    """Wie zone_detail, aber fuer HE/SAP-Durchschlag: [bug, mitte, deck] je 1/0/-1."""
    return [-1 if ship.get(z) is None else int(penetrates(pen_mm, ship[z])) for z in ('bow', 'mid', 'deck')]


def pen_state(pen_mm, ship):
    bow, deck = penetrates(pen_mm, ship['bow']), penetrates(pen_mm, ship['deck'])
    if bow and deck:
        return GREEN
    if bow:
        return 'bow'
    return 'deck' if deck else RED


def evaluate(me, enemy, ammo='ap', pen_mm=None):
    """me/enemy: dict mit 'class', 'caliber', 'bow', 'deck', optional 'mid' (mm).

    ammo/pen_mm: geladene Munition ('ap', 'he', 'sap') und ihr Durchschlag (mm, nur HE/SAP).
    Bei HE/SAP bewerten 'attack' und der Target-Teil von 'detail' den Durchschlag statt des
    Overmatch; Schild und Me-Teil bleiben AP-Overmatch des Gegners.
    HE/SAP wird auch fuer Zerstoerer, Traeger und U-Boote bewertet; Schild und Me-Teil gibt es
    nur bei Kreuzer/Schlachtschiff-Paarungen, sonst grau bzw. unbekannt (-1).
    Liefert None, wenn die Paarung nicht angezeigt werden soll.
    """
    he = ammo in PEN_AMMO and pen_mm is not None
    ap_rated = is_relevant(me['class'], enemy['class'])
    if not ap_rated and not (he and enemy['class'] in PEN_CLASSES):
        return None
    return {
        'ammo': ammo if he else 'ap',
        'attack': pen_state(pen_mm, enemy) if he else attack_color(me['caliber'], enemy),
        'defense': defense_color(enemy['caliber'], me) if ap_rated else GREY,
        'detail': (pen_detail(pen_mm, enemy) if he else zone_detail(me['caliber'], enemy))
        + (zone_detail(enemy['caliber'], me) if ap_rated else [-1, -1, -1]),
    }
