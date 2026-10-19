# -*- coding: utf-8 -*-
"""Overmatch-Ampel. Muss unter Python 2.7 (Spielclient) und 3.x (Tests) laufen."""

OVERMATCH_RATIO = 14.3

GREEN = 'green'
YELLOW = 'yellow'
RED = 'red'

# Werte von Ship.subtype bzw. GameParams 'species'; per Probe-Mod zu bestaetigen.
RELEVANT_CLASSES = frozenset(['Cruiser', 'Battleship'])

# Bug ueberwunden, Deck nicht: von der Ampel-Definition nicht abgedeckt.
# Annahme: gilt als "teilweise" -> Gelb.
BOW_ONLY_COLOR = YELLOW


def overmatches(caliber_mm, armor_mm):
    return caliber_mm > armor_mm * OVERMATCH_RATIO


def _zones(caliber_mm, bow_mm, deck_mm):
    return overmatches(caliber_mm, bow_mm), overmatches(caliber_mm, deck_mm)


def attack_color(my_caliber_mm, target_bow_mm, target_deck_mm):
    """Granate: kann ich das Ziel overmatchen?"""
    bow, deck = _zones(my_caliber_mm, target_bow_mm, target_deck_mm)
    if bow and deck:
        return GREEN
    if deck:
        return YELLOW
    if bow:
        return BOW_ONLY_COLOR
    return RED


def defense_color(enemy_caliber_mm, my_bow_mm, my_deck_mm):
    """Schild: kann der Gegner mich overmatchen?"""
    bow, deck = _zones(enemy_caliber_mm, my_bow_mm, my_deck_mm)
    if bow and deck:
        return RED
    if deck:
        return YELLOW
    if bow:
        return BOW_ONLY_COLOR
    return GREEN


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
