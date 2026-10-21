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
    'PASC720_Hawaii': ['Cruiser', 27.0, 36.0, 127.0, 28.0],
    'PJSB018_Yamato_1944': ['Battleship', 32.0, 57.0, 460.0, 32.0],
    'PBSC110_Minotaur': ['Cruiser', 16.0, 16.0, 152.0],
    'PASC510_Alaska': ['Cruiser', 27.0, 36.0, 305.0],
    'PASD013_Gearing': ['Destroyer', 19.0, 19.0, 127.0],
}
VERSION = '15,9,0,13357625'
# Granaten wie battle.getAmmoParams: 1 = AP, 2 = HE (Hawaii 127 mm: 21 mm), 3 = SAP 30 mm, 4 = HE 36 mm
AMMO = {1: Obj(ammoType='AP', alphaPiercingHE=0.0, alphaPiercingCS=0),
        2: Obj(ammoType='HE', alphaPiercingHE=21.0, alphaPiercingCS=0),
        3: Obj(ammoType='CS', alphaPiercingHE=0.0, alphaPiercingCS=30),
        4: Obj(ammoType='HE', alphaPiercingHE=36.0, alphaPiercingCS=0)}


class ModTest(unittest.TestCase):
    def run_mod(self, own_ship, enemies, data_version=VERSION, ammo=1):
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
                          getSelfPlayerInfo=lambda: {'id': 1},
                          getSelectedAmmoId=lambda weapon: ammo,
                          getAmmoParams=lambda ammo_id: AMMO[ammo_id]),
            'constants': Obj(WeaponType=Obj(ARTILLERY=0)),
            'open': client_open,
            'ui': Obj(createUiElement=lambda: 7,
                      addDataComponentWithId=lambda uid, cid, data: self.ui_data.append((cid, data)),
                      updateUiElementData=lambda uid, data: self.ui_data.append(('update', data)),
                      deleteUiElement=lambda uid: None),
            'utils': Obj(getModDir=lambda: wrong_dir, getGameVersion=lambda: VERSION,
                         jsonDncode=json.loads, logInfo=lambda *a, **k: None),
            'events': Obj(onBattleShown=lambda f: handlers.setdefault('shown', f),
                          onPlayersListUpdated=lambda f: handlers.setdefault('players', f),
                          onBattleQuit=lambda f: handlers.setdefault('quit', f),
                          onArtilleryAmmoChanged=lambda f: handlers.setdefault('ammo', f)),
        }
        self.handlers = handlers
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
        self.assertEqual(self.ui_data[0], ('modOvermatcher', {'byId': {}, 'byName': {}, 'ammo': 'ap'}))
        self.assertEqual(self.ui_data[-1], ('update', {
            'ammo': 'ap',
            # Detail: ich->Ziel [Bug, Mitte, Deck], Ziel->ich [Bug, Mitte, Deck]
            'byId': {'10': ['red', 'yellow', [0, 0, 0, 1, 1, 0], 'detail_target_r_r_r', 'detail_me_g_g_r']},
            'byName': {'bot10': ['red', 'yellow', [0, 0, 0, 1, 1, 0], 'detail_target_r_r_r', 'detail_me_g_g_r']},
        }))

    def test_loaded_he_rates_penetration(self):
        # Hawaii mit HE 21 mm gegen Minotaur (16 mm ueberall): Bug/Heck und Deck -> gruen
        lines = self.run_mod('PASC720_Hawaii', ['PBSC110_Minotaur', 'PJSB018_Yamato_1944'], ammo=2)
        self.assertEqual(lines, ['PBSC110_Minotaur attack=he:green defense=green',
                                 'PJSB018_Yamato_1944 attack=he:red defense=yellow'])
        payload = self.ui_data[-1][1]
        self.assertEqual(payload['ammo'], 'he')
        self.assertEqual(payload['byId']['10'][2][:3], [1, -1, 1])  # Ziel-Teil = Durchschlag (Mitte unbekannt)

    def test_ammo_switch_refreshes(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'])       # AP geladen
        self.handlers['ammo'](3)                                       # SAP 30 mm
        entry = self.ui_data[-1][1]
        self.assertEqual(entry['ammo'], 'sap')
        self.assertEqual(entry['byId']['10'][0], 'red')                # 30 mm < 32 mm Bug, < 57 mm Deck
        self.handlers['ammo'](4)                                       # HE 36 mm: Bug 32 ja, Deck 57 nein
        self.assertEqual(self.ui_data[-1][1]['byId']['10'][0], 'bow')
        self.handlers['ammo'](1)
        self.assertEqual(self.ui_data[-1][1]['ammo'], 'ap')

    def test_missing_mid_is_unknown(self):
        self.run_mod('PASC720_Hawaii', ['PBSC110_Minotaur'])  # Minotaur ohne Mitte-Wert
        entry = self.ui_data[-1][1]['byId']['10']
        self.assertEqual(entry[2], [0, -1, 0, 0, 0, 0])
        self.assertEqual(entry[3:], ['', 'detail_me_r_r_r'])  # Granate ohne Bild, Schild: nirgends Overmatch

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
