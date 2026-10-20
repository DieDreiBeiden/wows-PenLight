# -*- coding: utf-8 -*-
"""Overmatch-Ampel. Muss unter Python 2.7 (Spielclient) und 3.x (Tests) laufen."""

OVERMATCH_RATIO = 14.3

GREEN = 'green'
YELLOW = 'yellow'
RED = 'red'

# Werte von Ship.subtype bzw. GameParams 'species'; per Probe-Mod zu bestaetigen.
RELEVANT_CLASSES = frozenset(['Cruiser', 'Battleship'])

# Ampel nach Spieler-Definition (docs/KONZEPT.md). Bug/Heck ist die taktische
# Kategorie, das Deck zaehlt nur zusammen mit dem Bug ("Kirsche obendrauf").
#   (bug, deck)     Granate  Schild
#   (ja, ja)        gruen    rot      ueberall durch / aktiv ausweichen
#   (ja, nein)      gelb     gelb     auf Bug/Heck zielen / Bug/Heck schuetzen
#   (nein, *)       rot      gruen    nur Breitseite / aggressiv anwinkeln
ATTACK_COLORS = {(True, True): GREEN, (True, False): YELLOW, (False, True): RED, (False, False): RED}
DEFENSE_COLORS = {(True, True): RED, (True, False): YELLOW, (False, True): GREEN, (False, False): GREEN}


def overmatches(caliber_mm, armor_mm):
    return caliber_mm > armor_mm * OVERMATCH_RATIO


def _zones(caliber_mm, bow_mm, deck_mm):
    return overmatches(caliber_mm, bow_mm), overmatches(caliber_mm, deck_mm)


def attack_color(my_caliber_mm, target_bow_mm, target_deck_mm):
    """Granate: kann ich das Ziel overmatchen?"""
    return ATTACK_COLORS[_zones(my_caliber_mm, target_bow_mm, target_deck_mm)]


def defense_color(enemy_caliber_mm, my_bow_mm, my_deck_mm):
    """Schild: kann der Gegner mich overmatchen?"""
    return DEFENSE_COLORS[_zones(enemy_caliber_mm, my_bow_mm, my_deck_mm)]


def is_relevant(my_class, enemy_class):
    return my_class in RELEVANT_CLASSES and enemy_class in RELEVANT_CLASSES


def evaluate(me, enemy):
    """me/enemy: dict mit 'class', 'caliber', 'bow', 'deck' (mm).

    Liefert None, wenn die Paarung nicht angezeigt werden soll.
    """
    if not is_relevant(me['class'], enemy['class']):
        return None
    return {
        'attack': attack_color(me['caliber'], enemy['bow'], enemy['deck']),
        'defense': defense_color(enemy['caliber'], me['bow'], me['deck']),
    }
