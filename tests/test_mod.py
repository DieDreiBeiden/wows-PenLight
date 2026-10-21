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
DEFAULTS = {'x': 30, 'y': 8, 'detailMode': 0, 'colorMode': 0, 'scale': 1.0}


class ModTest(unittest.TestCase):
    def run_mod(self, own_ship, enemies, data_version=VERSION, ttaro=False, ammo=1, he_coeff=1.0):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root)
        if ttaro:
            os.mkdir(os.path.join(root, 'TTaroModUtils'))
            open(os.path.join(root, 'TTaroModUtils', 'Main.py'), 'w').close()
        mod_dir = os.path.join(root, 'PenLight')
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
        self.flash_calls = []
        self.flash_callbacks = {}
        self.mod_dir = mod_dir

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
                          getAmmoParams=lambda ammo_id: AMMO[ammo_id],
                          getAmmoModifiers=lambda: Obj(GMPenetrationCoeffHE=he_coeff)),
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
                          onKeyEvent=lambda f: handlers.setdefault('key', f),
                          onArtilleryAmmoChanged=lambda f: handlers.setdefault('ammo', f)),
            'flash': Obj(call=lambda name, args: self.flash_calls.append((name, args)),
                         addExternalCallback=lambda name, f: self.flash_callbacks.setdefault(name, f)),
            'Keys': Obj(KEY_LEFTARROW=203, KEY_RIGHTARROW=205, KEY_UPARROW=200, KEY_DOWNARROW=208,
                        KEY_HOME=199, KEY_D=32, KEY_F=33, KEY_EQUALS=13, KEY_MINUS=12),
        }
        self.handlers = handlers
        self.env = env
        exec(compile(open(build_mod.build()).read(), 'Main.py', 'exec'), env)
        handlers['shown']()
        self.log = open(os.path.join(mod_dir, 'penlight_log.txt')).read()
        return open(os.path.join(mod_dir, 'penlight_last.txt')).read().splitlines()

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
        self.assertEqual(self.ui_data[0], ('modPenLight', {'byId': {}, 'byName': {},
                                                              'settings': DEFAULTS, 'ammo': 'ap',
                                                              'ifhe': False}))
        self.assertEqual(self.ui_data[-1], ('update', {
            'settings': DEFAULTS, 'ammo': 'ap', 'ifhe': False,
            # Detail: ich->Ziel [Bug, Mitte, Deck], Ziel->ich [Bug, Mitte, Deck]
            'byId': {'10': ['red', 'yellow', [0, 0, 0, 1, 1, 0], 'detail_target_r_r_r', 'detail_me_g_g_r']},
            'byName': {'bot10': ['red', 'yellow', [0, 0, 0, 1, 1, 0], 'detail_target_r_r_r', 'detail_me_g_g_r']},
        }))

    def key(self, code, ctrl=True, alt=True, shift=False):
        self.handlers['key'](Obj(key=code, isKeyDown=lambda: True, isCtrlDown=lambda: ctrl,
                                 isAltDown=lambda: alt, isShiftDown=lambda: shift))

    def saved(self):
        # ModPrefs existiert im Test nicht -> Rueckfall in den Mod-Ordner
        return json.load(open(os.path.join(self.mod_dir, 'diedreibeiden-penlight.json')))

    def test_position_keys_move_save_and_reset(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'])
        self.key(205)                 # rechts, 5 px
        self.key(208, shift=True)     # runter, 1 px
        settings = self.ui_data[-1][1]['settings']
        self.assertEqual((settings['x'], settings['y']), (35, 9))
        self.assertEqual((self.saved()['x'], self.saved()['y']), (35, 9))
        self.key(199)                 # Pos1 = zuruecksetzen
        self.assertEqual(self.ui_data[-1][1]['settings'], DEFAULTS)

    def test_option_keys(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'])
        self.key(32)                  # D: Detailansicht immer
        self.key(33)                  # F: Farbenblind
        for _ in range(20):
            self.key(13)              # +: Groesse, gedeckelt bei 2,0
        self.key(12)                  # -: 1,9
        expected = dict(DEFAULTS, detailMode=1, colorMode=1, scale=1.9)
        self.assertEqual(self.ui_data[-1][1]['settings'], expected)
        self.assertEqual(self.saved(), expected)

    def test_keys_without_ctrl_alt_are_ignored(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'])
        count = len(self.ui_data)
        self.key(205, alt=False)
        self.key(32, ctrl=False)
        self.assertEqual(len(self.ui_data), count)

    def test_saved_settings_are_checked(self):
        self.run_mod('PASC720_Hawaii', [])
        # kaputte bzw. unzulaessige Werte fallen auf den Standard zurueck, Groesse wird begrenzt
        raw = {'x': 50, 'y': 'oben', 'detailMode': 7, 'colorMode': 1, 'scale': 9}
        self.assertEqual(self.env['clean_settings'](raw), dict(DEFAULTS, x=50, colorMode=1, scale=2.0))

    def test_drag_moves_live_and_saves_on_release(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'])
        # Greifflaeche im Gefecht aktiv, an der Standardposition, Groesse der Symbole
        self.assertEqual(self.flash_calls[-1], ('omSetHandle', [30, 8, 62.0, 29.0, True]))
        self.flash_callbacks['omDragMove'](120.4, -50)
        self.assertEqual(self.ui_data[-1][1]['settings']['x'], 120)
        self.assertFalse(os.path.exists(os.path.join(self.mod_dir, 'diedreibeiden-penlight.json')))
        self.flash_callbacks['omDragEnd'](130, -40)
        self.assertEqual((self.saved()['x'], self.saved()['y']), (130, -40))

    def test_handle_follows_scale_and_battle_end(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'])
        self.key(13)                  # +: Groesse 1,1 -> Greifflaeche waechst mit
        name, args = self.flash_calls[-1]
        self.assertEqual((name, args[:2], args[4]), ('omSetHandle', [30, 8], True))
        self.assertAlmostEqual(args[2], 62 * 1.1)
        self.handlers['quit']()
        self.assertFalse(self.flash_calls[-1][1][4])

    def test_ttaro_takes_over_settings(self):
        self.run_mod('PASC720_Hawaii', ['PJSB018_Yamato_1944'], ttaro=True)
        self.assertIn('settings via TTaroModUtils', self.log)
        self.assertFalse(self.flash_calls[-1][1][4])   # Greifflaeche von Main.swf aus
        count = len(self.ui_data)
        self.key(205)                                   # Tastenkuerzel aus
        self.assertEqual(len(self.ui_data), count)

    def test_he_rates_destroyer(self):
        # Hawaii HE 21 mm gegen Gearing (19 mm): gruen; Schild grau, weil kein Kreuzer/Schlachtschiff
        lines = self.run_mod('PASC720_Hawaii', ['PASD013_Gearing'], ammo=2)
        self.assertEqual(lines, ['PASD013_Gearing attack=he:green defense=grey'])
        self.assertEqual(self.ui_data[-1][1]['byId']['10'][2][3:], [-1, -1, -1])

    def test_destroyer_with_he_rates_cruiser(self):
        lines = self.run_mod('PASD013_Gearing', ['PBSC110_Minotaur'], ammo=2)  # 21 mm gegen 16 mm
        self.assertEqual(lines, ['PBSC110_Minotaur attack=he:green defense=grey'])

    def test_loaded_he_rates_penetration(self):
        # Hawaii mit HE 21 mm gegen Minotaur (16 mm ueberall): Bug/Heck und Deck -> gruen
        lines = self.run_mod('PASC720_Hawaii', ['PBSC110_Minotaur', 'PJSB018_Yamato_1944'], ammo=2)
        self.assertEqual(lines, ['PBSC110_Minotaur attack=he:green defense=green',
                                 'PJSB018_Yamato_1944 attack=he:red defense=yellow'])
        payload = self.ui_data[-1][1]
        self.assertEqual(payload['ammo'], 'he')
        self.assertEqual(payload['byId']['10'][2][:3], [1, -1, 1])  # Ziel-Teil = Durchschlag (Mitte unbekannt)

    def test_ifhe_raises_he_penetration(self):
        # Hawaii HE 21 mm x 1.3 (IFHE) = 27.3 -> 27 mm: Alaska-Bug 27 mm ja (Gleichstand), Deck 36 nein
        lines = self.run_mod('PASC720_Hawaii', ['PASC510_Alaska'], ammo=2, he_coeff=1.3)
        self.assertEqual(lines, ['PASC510_Alaska attack=he:bow defense=green'])
        self.assertTrue(self.ui_data[-1][1]['ifhe'])

    def test_he_penetration_rounds_down(self):
        # 21 mm x 1.25 = 26.25 -> 26 mm < 27 mm Bug: rot, obwohl gerundet 26 nahe 27
        lines = self.run_mod('PASC720_Hawaii', ['PASC510_Alaska'], ammo=2, he_coeff=1.25)
        self.assertEqual(lines[0].split()[1], 'attack=he:red')

    def test_no_ifhe_without_modifier_or_for_sap(self):
        self.run_mod('PASC720_Hawaii', ['PASC510_Alaska'], ammo=2)
        self.assertFalse(self.ui_data[-1][1]['ifhe'])
        self.run_mod('PASC720_Hawaii', ['PASC510_Alaska'], ammo=3, he_coeff=1.25)  # SAP: kein Faktor
        self.assertFalse(self.ui_data[-1][1]['ifhe'])
        self.assertEqual(self.ui_data[-1][1]['ammo'], 'sap')

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
