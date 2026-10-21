# -*- coding: utf-8 -*-
# Synthetische GameParams-Datei im Originalformat (Pickle -> zlib -> reversed).
# Die Feldstruktur ist nachgebaut, nicht aus einer echten Datei entnommen.
import os
import pickle
import sys
import tempfile
import types
import unittest
import zlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import gameparams

_mod = types.ModuleType('GameParams')
sys.modules['GameParams'] = _mod


class GPData(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


GPData.__module__ = 'GameParams'
_mod.GPData = GPData


def armor(bow, deck, inner_deck=None, mid=None):
    """armor-Dict im GameParams-Format: (lage << 16) | material_id -> mm."""
    mat = gameparams.MATERIAL_NAMES.index
    out = {(1 << 16) | mat('Bow_ConstrSide'): bow, (1 << 16) | mat('Cas_Deck'): deck,
           (1 << 16) | mat('Bow_Trans'): 0.0}
    if mid is not None:
        out[(1 << 16) | mat('Cas_Belt')] = mid
        out[(1 << 16) | mat('SSC_ConstrSide')] = mid + 10
    if inner_deck is not None:
        out[(2 << 16) | mat('Cas_Deck')] = inner_deck
    return out


def ship(index, species, hulls, arts, upgrades):
    kw = dict(index=index, id=hash(index) & 0xffffffff, level=10,
              typeinfo=GPData(type='Ship', species=species), ShipUpgradeInfo=GPData(**upgrades))
    kw.update(hulls)
    kw.update(arts)
    return GPData(**kw)


def write_gameparams(path, entries):
    params = dict((e.index, e) for e in entries)
    raw = pickle.dumps({'': params, 'EU': params}, protocol=2)
    with open(path, 'wb') as f:
        f.write(zlib.compress(raw)[::-1])


class GameParamsTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), 'GameParams.data')
        yamato = ship(
            'PJSB018_Yamato_1944', 'Battleship',
            {'A_Hull': GPData(armourExtremities=[-1, -1], armourDeck=[-1, -1], armor=armor(32.0, 57.0, inner_deck=200.0, mid=32.0))},
            {'A_Artillery': GPData(HP_JGM_1=GPData(barrelDiameter=0.46, numBarrels=3), maxDist=26000)},
            {'H1': GPData(ucType='_Hull', prev='', components={'hull': ['A_Hull']}),
             'A1': GPData(ucType='_Artillery', prev='', components={'artillery': ['A_Artillery']})})
        upgradeable = ship(
            'PXSC001_Test', 'Cruiser',
            {'A_Hull': GPData(armor=armor(13.0, 13.0)),
             'B_Hull': GPData(armor=armor(16.0, 16.0))},
            {'A_Artillery': GPData(HP_1=GPData(barrelDiameter=0.152))},
            {'H1': GPData(ucType='_Hull', prev='', components={'hull': ['A_Hull']}),
             'H2': GPData(ucType='_Hull', prev='H1', components={'hull': ['B_Hull']})})
        destroyer = ship('PXSD001_Test', 'Destroyer', {}, {}, {})
        write_gameparams(self.path, [yamato, upgradeable, destroyer])

    def test_extract(self):
        ships = gameparams.extract(gameparams.load(self.path))
        # alle Klassen werden gelesen; Schiffe ohne Panzerungsdaten fallen erst in mod_table weg
        self.assertEqual(sorted(ships), ['PJSB018_Yamato_1944', 'PXSC001_Test', 'PXSD001_Test'])
        self.assertIsNone(ships['PXSD001_Test']['bow'])
        y = ships['PJSB018_Yamato_1944']
        self.assertEqual((y['class'], y['bow'], y['deck'], y['caliber'], y['mid']),
                         ('Battleship', 32.0, 57.0, 460.0, 32.0))

    def test_mod_table_classes(self):
        def row(cls, bow, deck, caliber):
            return {'class': cls, 'bow': bow, 'deck': deck, 'caliber': caliber, 'mid': None}
        table = gameparams.mod_table({
            'PASD013_Gearing_1945': row('Destroyer', 19.0, 19.0, 127.0),
            'PJSA718_Akagi': row('AirCarrier', 19.0, 19.0, None),       # Traeger: nur HE/SAP-Ziel
            'PASC000_NoGuns': row('Cruiser', 25.0, 30.0, None),         # Kreuzer braucht Kaliber
            'PASD000_NoArmor': row('Destroyer', None, 19.0, 127.0),
        }, '15,9,0,1')['ships']
        self.assertEqual(sorted(table), ['PASD013_Gearing_1945', 'PJSA718_Akagi'])

    def test_final_hull_is_used(self):
        ships = gameparams.extract(gameparams.load(self.path))
        self.assertEqual(ships['PXSC001_Test']['hull'], 'B_Hull')
        self.assertEqual(ships['PXSC001_Test']['bow'], 16.0)


if __name__ == '__main__':
    unittest.main()
