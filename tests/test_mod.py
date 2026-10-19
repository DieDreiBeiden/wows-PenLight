# -*- coding: utf-8 -*-
# Fuehrt die gebaute Main.py mit nachgebauten Client-Objekten aus.
# Die Objektstruktur folgt den Probe-Dumps (Build 15.9.0.13357625).
import builtins
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import build_mod

builtins.long = int
builtins.basestring = str


class Obj(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


SHIPS = {
    'PASC720_Hawaii': ['Cruiser', 27.0, 36.0, 127.0],
    'PJSB018_Yamato_1944': ['Battleship', 32.0, 57.0, 460.0],
    'PBSC110_Minotaur': ['Cruiser', 16.0, 16.0, 152.0],
    'PASC510_Alaska': ['Cruiser', 27.0, 36.0, 305.0],
    'PASD013_Gearing': ['Destroyer', 19.0, 19.0, 127.0],
}
VERSION = '15,9,0,13357625'


class ModTest(unittest.TestCase):
    def run_mod(self, own_ship, enemies, data_version=VERSION):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        mod_dir = os.path.join(root, 'Overmatcher')
        wrong_dir = os.path.join(root, 'OvermatcherProbe')  # getModDir-Befund im Client
        os.mkdir(mod_dir)
        os.mkdir(wrong_dir)
        with open(os.path.join(mod_dir, 'ships.json'), 'w') as f:
            json.dump({'gameVersion': data_version, 'ships': SHIPS}, f)
        players = {1: {'teamId': 0, 'name': 'me'}}
        ship_names = {1: own_ship}
        for i, ship in enumerate(enemies, start=10):
            players[i] = {'teamId': 1, 'name': 'bot%d' % i}
            ship_names[i] = ship
        handlers = {}
        self.ui_data = []

        def client_open(path, mode):
            # wie im Client: Modus Pflicht, 'a' nur fuer vorhandene Dateien
            if 'a' in mode and not os.path.exists(path):
                raise IOError('Path %r does not exists' % path)
            return open(path, mode)
        env = {
            '__name__': 'Main',
            'battle': Obj(getPlayersInfo=lambda: players,
                          getPlayerShipInfo=lambda pid: Obj(name=ship_names[pid]),
                          getSelfPlayerInfo=lambda: {'id': 1}),
            'open': client_open,
            'ui': Obj(createUiElement=lambda: 7,
                      addDataComponentWithId=lambda uid, cid, data: self.ui_data.append((cid, data)),
                      updateUiElementData=lambda uid, data: self.ui_data.append(('update', data)),
                      deleteUiElement=lambda uid: None),
            'utils': Obj(getModDir=lambda: wrong_dir, getGameVersion=lambda: VERSION,
                         jsonDncode=json.loads, logInfo=lambda *a, **k: None),
            'events': Obj(onBattleShown=lambda f: handlers.setdefault('shown', f),
                          onPlayersListUpdated=lambda f: handlers.setdefault('players', f),
                          onBattleQuit=lambda f: handlers.setdefault('quit', f)),
        }
        exec(compile(open(build_mod.build()).read(), 'Main.py', 'exec'), env)
        handlers['shown']()
        self.log = open(os.path.join(mod_dir, 'overmatcher_log.txt')).read()
        return open(os.path.join(mod_dir, 'overmatcher_last.txt')).read().splitlines()

    def test_cruiser_vs_mixed_enemies(self):
        lines = self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944', 'PBSC110_Minotaur', 'PASD013_Gearing'])
        self.assertEqual(lines, [
            'PBSC110_Minotaur attack=red defense=green',
            'PJSB018_Yamato_1944 attack=red defense=yellow',  # 460 > 27 Bug, < 36 Deck
        ])

    def test_large_cruiser_overmatches_minotaur(self):
        lines = self.run_mod('PASC510_Alaska', ['PBSC110_Minotaur'])
        self.assertEqual(lines, ['PBSC110_Minotaur attack=green defense=green'])

    def test_ui_payload_for_unbound(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944', 'PASD013_Gearing'])
        self.assertEqual(self.ui_data[0], ('modOvermatcher', {'byId': {}, 'byName': {}}))
        self.assertEqual(self.ui_data[-1], ('update', {
            'byId': {'10': ['red', 'yellow']},
            'byName': {'bot10': ['red', 'yellow']},
        }))

    def test_version_mismatch_disables(self):
        lines = self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'], data_version='15,8,0,1')
        self.assertTrue(lines[0].startswith('(keine relevanten Gegner'))
        self.assertIn('data version 15,8,0,1 != game version', self.log)

    def test_only_irrelevant_enemies_still_reports(self):
        lines = self.run_mod('PASC720_Hawaii', ['PASD013_Gearing'])
        self.assertTrue(lines[0].startswith('(keine relevanten Gegner'))
        self.assertIn('Main.py loaded', self.log)

    def test_unknown_enemy_is_logged(self):
        self.run_mod('PASC720_Hawaii', ['PZZZ999_Unknown'])
        self.assertIn('no data for enemy ship PZZZ999_Unknown', self.log)


if __name__ == '__main__':
    unittest.main()
