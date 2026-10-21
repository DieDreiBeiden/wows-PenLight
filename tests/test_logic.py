# -*- coding: utf-8 -*-
# Schwellwerte aus dem WoWS-Wiki "Ship:Armor thresholds" (Stand 08/2024).
# Schiffsmasse hier sind Beispielwerte, keine verifizierten Spieldaten.
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from overmatcher.logic import (GREEN, RED, YELLOW, attack_color, defense_color,
                               detail_icons, evaluate, overmatches, pen_detail, pen_state,
                               zone_detail)


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
    # Zonen in mm; Werte aus ships.json 15.9
    HAWAII = {'bow': 27.0, 'mid': 28.0, 'deck': 36.0}
    THUNDERER = {'bow': 32.0, 'mid': 32.0, 'deck': 32.0}
    NEW_ORLEANS_LIKE = {'bow': 25.0, 'mid': 25.0, 'deck': 25.0}

    def test_attack(self):
        self.assertEqual(attack_color(460, self.THUNDERER), GREEN)          # alles
        self.assertEqual(attack_color(460, self.HAWAII), YELLOW)            # Bug+Mitte, Deck nicht
        self.assertEqual(attack_color(400, self.HAWAII), YELLOW)            # nur Bug
        self.assertEqual(attack_color(457, self.THUNDERER), RED)            # Bug nicht
        self.assertEqual(attack_color(406, self.NEW_ORLEANS_LIKE), GREEN)

    def test_defense(self):
        # Farbe = gut fuer mich: Rot = Gegner overmatcht mich ueberall
        self.assertEqual(defense_color(460, self.THUNDERER), RED)
        self.assertEqual(defense_color(460, self.HAWAII), YELLOW)
        self.assertEqual(defense_color(457, self.THUNDERER), GREEN)

    def test_deck_only_counts_as_nothing(self):
        ship = {'bow': 32.0, 'mid': 32.0, 'deck': 30.0}
        self.assertEqual(attack_color(457, ship), RED)
        self.assertEqual(defense_color(457, ship), GREEN)

    def test_missing_mid_uses_bow_and_deck(self):
        self.assertEqual(attack_color(460, {'bow': 32.0, 'mid': None, 'deck': 32.0}), GREEN)
        self.assertEqual(attack_color(460, {'bow': 32.0, 'deck': 38.0}), YELLOW)


class Penetration(unittest.TestCase):
    YAMATO = {'bow': 32.0, 'mid': 32.0, 'deck': 57.0}

    def test_tie_penetrates(self):
        self.assertEqual(pen_state(32, {'bow': 32.0, 'deck': 32.0}), GREEN)

    def test_states(self):
        self.assertEqual(pen_state(36, self.YAMATO), 'bow')
        self.assertEqual(pen_state(57, self.YAMATO), GREEN)
        self.assertEqual(pen_state(30, self.YAMATO), RED)
        self.assertEqual(pen_state(40, {'bow': 50.0, 'deck': 38.0}), 'deck')

    def test_detail(self):
        self.assertEqual(pen_detail(36, self.YAMATO), [1, 1, 0])

    def test_evaluate_with_he_keeps_shield_on_ap(self):
        me = {'class': 'Cruiser', 'caliber': 203, 'bow': 27, 'deck': 30, 'mid': 27}
        r = evaluate(me, dict(self.YAMATO, **{'class': 'Battleship', 'caliber': 460}), 'he', 51)
        self.assertEqual((r['ammo'], r['attack'], r['defense']), ('he', 'bow', RED))
        self.assertEqual(r['detail'], [1, 1, 0, 1, 1, 1])


class Detail(unittest.TestCase):
    def test_zones(self):
        hawaii = {'bow': 27.0, 'mid': 28.0, 'deck': 36.0}
        self.assertEqual(zone_detail(460, hawaii), [1, 1, 0])
        self.assertEqual(zone_detail(400, hawaii), [1, 0, 0])  # 400/14,3 = 27,97 mm

    def test_icons(self):
        # ich overmatche Bug, nicht Mitte/Deck; Gegner overmatcht Bug+Mitte bei mir
        self.assertEqual(detail_icons([1, 0, 0, 1, 1, 0]), ('detail_target_g_r_r', 'detail_me_g_g_r'))
        self.assertEqual(detail_icons([0, -1, 0, 0, 0, 0]), ('', 'detail_me_r_r_r'))

    def test_unknown_zone(self):
        self.assertEqual(zone_detail(460, {'bow': 27.0, 'mid': None, 'deck': 36.0}), [1, -1, 0])


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
        self.assertEqual(evaluate(large, light)['attack'], GREEN)
        self.assertEqual(evaluate(large, light)['defense'], GREEN)
        self.assertEqual(evaluate(light, large)['attack'], RED)
        self.assertEqual(evaluate(light, large)['defense'], RED)

    def test_battleship_vs_battleship_shown(self):
        bb = self.ship('Battleship', 460, 32, 32)
        self.assertIsNotNone(evaluate(bb, bb))


if __name__ == '__main__':
    unittest.main()
