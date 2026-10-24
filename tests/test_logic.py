# -*- coding: utf-8 -*-
# Schwellwerte aus dem WoWS-Wiki "Ship:Armor thresholds" (Stand 08/2024).
# Schiffsmasse hier sind Beispielwerte, keine verifizierten Spieldaten.
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from penlight.logic import (GREEN, RED, YELLOW, attack_color, defense_color,
                            detail_icons, evaluate, floor_mm, overmatch_limit, overmatches, pen_detail, pen_state,
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

    def test_floor_mm_always_rounds_down(self):
        self.assertEqual(floor_mm(37.5), 37)
        self.assertEqual(floor_mm(37.99), 37)
        self.assertEqual(floor_mm(40.0), 40)
        self.assertEqual(floor_mm(32 * 1.25), 40)
        self.assertEqual(floor_mm(39.9999999999), 40)   # Gleitkomma-Rest, kein echter Wert darunter

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

    def test_destroyer_is_hidden_with_ap(self):
        dd = self.ship('Destroyer', 130, 19, 19)
        ca = self.ship('Cruiser', 203, 25, 27)
        self.assertIsNone(evaluate(ca, dd))
        self.assertIsNone(evaluate(dd, ca))

    def test_he_rates_every_class(self):
        dd = self.ship('Destroyer', 130, 19, 19)
        ca = self.ship('Cruiser', 203, 25, 27)
        cv = self.ship('AirCarrier', None, 19, 19)
        ss = self.ship('Submarine', None, 19, 16)
        # Kreuzer-HE 30 mm gegen Zerstoerer/Traeger: ueberall durch, Schild ohne Bewertung
        for target in (dd, cv):
            r = evaluate(ca, target, 'he', 30)
            self.assertEqual((r['attack'], r['defense']), (GREEN, 'grey'))
            self.assertEqual(r['detail'][3:], [-1, -1, -1])
        # Zerstoerer-HE 21 mm gegen Kreuzer (25 / 27 mm): nirgends
        r = evaluate(dd, ca, 'sap', 26)
        self.assertEqual((r['attack'], r['defense']), ('bow', 'grey'))
        self.assertEqual(evaluate(dd, ca, 'he', 21)['attack'], RED)
        # U-Boote werden nicht bewertet, weder als Ziel noch als eigenes Schiff
        self.assertIsNone(evaluate(ca, ss, 'he', 30))
        self.assertIsNone(evaluate(ss, ca, 'he', 30))
        # Traeger nur als Ziel, nicht als eigenes Schiff
        self.assertIsNone(evaluate(cv, ca, 'he', 30))

    def test_cruiser_pair_keeps_shield_with_he(self):
        ca = self.ship('Cruiser', 203, 25, 27)
        bb = self.ship('Battleship', 406, 32, 57)
        self.assertEqual(evaluate(ca, bb, 'he', 30)['defense'], RED)  # 406 > 14.3 x 27

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



class Numbers(unittest.TestCase):
    def test_overmatch_limit(self):
        self.assertEqual(overmatch_limit(203), 14)    # 203 / 14.3 = 14.2
        self.assertEqual(overmatch_limit(460), 32)
        self.assertEqual(overmatch_limit(143), 9)     # genau 10 * 14.3: 10 mm wird nicht overmatcht
        self.assertEqual(overmatch_limit(None), -1)

    def test_numbers_for_he_and_unrated_shield(self):
        dd = {'class': 'Destroyer', 'caliber': 127.0, 'bow': 19.0, 'deck': 19.0}
        ca = {'class': 'Cruiser', 'caliber': 203.0, 'bow': 25.0, 'deck': 30.0, 'mid': 30.0}
        self.assertEqual(evaluate(ca, dd, 'he', 34)['numbers'], [19, -1, 19, 25, 30, 30, 34, -1, -1, -1])

if __name__ == '__main__':
    unittest.main()
