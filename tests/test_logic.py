# -*- coding: utf-8 -*-
# Schwellwerte aus dem WoWS-Wiki "Ship:Armor thresholds" (Stand 08/2024).
# Schiffsmasse hier sind Beispielwerte, keine verifizierten Spieldaten.
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from overmatcher.logic import (GREEN, RED, YELLOW, attack_color, defense_color,
                               evaluate, overmatches)


class OvermatchRule(unittest.TestCase):
    def test_wiki_thresholds(self):
        self.assertTrue(overmatches(460, 32))
        self.assertFalse(overmatches(457, 32))
        self.assertTrue(overmatches(457, 30))
        self.assertTrue(overmatches(406, 27))
        self.assertFalse(overmatches(381, 27))
        self.assertTrue(overmatches(381, 26))
        self.assertTrue(overmatches(234, 16))
        self.assertFalse(overmatches(220, 16))

    def test_exactly_at_threshold_is_no_overmatch(self):
        self.assertFalse(overmatches(14.3 * 25, 25))


class Colors(unittest.TestCase):
    def test_attack(self):
        self.assertEqual(attack_color(460, 32, 32), GREEN)
        self.assertEqual(attack_color(457, 32, 30), YELLOW)
        self.assertEqual(attack_color(305, 25, 30), RED)

    def test_defense(self):
        self.assertEqual(defense_color(460, 32, 32), RED)
        self.assertEqual(defense_color(457, 32, 30), YELLOW)
        self.assertEqual(defense_color(203, 25, 27), GREEN)

    def test_bow_only_is_yellow(self):
        # 460 mm gegen 32 mm Bug / 38 mm Deck (US-BB-Muster)
        self.assertEqual(attack_color(460, 32, 38), YELLOW)
        self.assertEqual(defense_color(460, 32, 38), YELLOW)


class Filter(unittest.TestCase):
    def ship(self, cls, caliber, bow, deck):
        return {'class': cls, 'caliber': caliber, 'bow': bow, 'deck': deck}

    def test_destroyer_is_hidden(self):
        dd = self.ship('Destroyer', 130, 19, 19)
        ca = self.ship('Cruiser', 203, 25, 27)
        self.assertIsNone(evaluate(ca, dd))
        self.assertIsNone(evaluate(dd, ca))

    def test_cruiser_vs_cruiser(self):
        # grosser Kreuzer 305 mm gegen leichten Kreuzer mit 16 mm Huelle
        large = self.ship('Cruiser', 305, 27, 30)
        light = self.ship('Cruiser', 152, 16, 16)
        self.assertEqual(evaluate(large, light), {'attack': GREEN, 'defense': GREEN})
        self.assertEqual(evaluate(light, large), {'attack': RED, 'defense': RED})

    def test_battleship_vs_battleship_shown(self):
        bb = self.ship('Battleship', 460, 32, 32)
        self.assertIsNotNone(evaluate(bb, bb))


if __name__ == '__main__':
    unittest.main()
