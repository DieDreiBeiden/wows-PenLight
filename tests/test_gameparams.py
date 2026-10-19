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


def ship(index, species, hulls, arts, upgrades):
    kw = dict(index=index, id=hash(index) & 0xffffffff, level=10,
              typeinfo=GPData(type='Ship', species=species), ShipUpgradeInfo=GPData(**upgrades))
    kw.update(hulls)
    kw.update(arts)
    return GPData(**kw)


def write_gameparams(path, entries):
    raw = pickle.dumps([dict((e.index, e) for e in entries)], protocol=2)
    with open(path, 'wb') as f:
        f.write(zlib.compress(raw)[::-1])


class GameParamsTest(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), 'GameParams.data')
        yamato = ship(
            'PJSB018_Yamato_1944', 'Battleship',
            {'A_Hull': GPData(armourExtremities=32.0, armourDeck=57.0)},
            {'A_Artillery': GPData(HP_JGM_1=GPData(barrelDiameter=0.46, numBarrels=3), maxDist=26000)},
            {'H1': GPData(ucType='_Hull', prev='', components={'hull': ['A_Hull']}),
             'A1': GPData(ucType='_Artillery', prev='', components={'artillery': ['A_Artillery']})})
        upgradeable = ship(
            'PXSC001_Test', 'Cruiser',
            {'A_Hull': GPData(armourExtremities=13.0, armourDeck=13.0),
             'B_Hull': GPData(armourExtremities=16.0, armourDeck=16.0)},
            {'A_Artillery': GPData(HP_1=GPData(barrelDiameter=0.152))},
            {'H1': GPData(ucType='_Hull', prev='', components={'hull': ['A_Hull']}),
             'H2': GPData(ucType='_Hull', prev='H1', components={'hull': ['B_Hull']})})
        destroyer = ship('PXSD001_Test', 'Destroyer', {}, {}, {})
        write_gameparams(self.path, [yamato, upgradeable, destroyer])

    def test_extract(self):
        ships = gameparams.extract(gameparams.load(self.path))
        self.assertEqual(sorted(ships), ['PJSB018_Yamato_1944', 'PXSC001_Test'])
        y = ships['PJSB018_Yamato_1944']
        self.assertEqual((y['class'], y['bow'], y['deck'], y['caliber']), ('Battleship', 32.0, 57.0, 460.0))

    def test_final_hull_is_used(self):
        ships = gameparams.extract(gameparams.load(self.path))
        self.assertEqual(ships['PXSC001_Test']['hull'], 'B_Hull')
        self.assertEqual(ships['PXSC001_Test']['bow'], 16.0)


if __name__ == '__main__':
    unittest.main()
