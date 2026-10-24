# -*- coding: utf-8 -*-
# Spiel-Anbindung. Wird von tools/build_mod.py hinter logic.py in Main.py kopiert;
# battle, utils, events stellt der Client als Globals bereit (ModsAPI v1.0);
# der Import ist eine Absicherung wie in PenetrationCalculator.
try:
    import events, ui, utils, battle
except Exception:
    pass
# Client-Sandbox: die Builtin-Funktion globals fehlt dort (python.log: NameError: name 'globals' is not
# defined). Darum erst den vom Client gesetzten Namen pruefen, dann importieren, sonst None.
try:
    flash
except NameError:
    try:
        import flash
    except Exception:
        flash = None
try:
    Keys
except NameError:
    try:
        import Keys
    except Exception:
        Keys = None
try:
    constants
except NameError:
    try:
        import constants
    except Exception:
        constants = None

MOD_NAME = 'PenLight'
# Datenkomponente fuer PenLight.unbound (CC.mods_DataComponent mit dieser ID)
UI_COMPONENT_ID = 'modPenLight'
DATA_FILE = 'ships.json'
RESULT_FILE = 'penlight_last.txt'
LOG_FILE = 'penlight_log.txt'

LOG_KEEP = 300

# Standalone-Einstellungen (ohne TTaroModUtils). Bedienung im Gefecht mit Strg+Alt+Taste:
#   Pfeiltasten   Anzeige verschieben (5 px, mit Umschalt 1 px)
#   Pos1          Position zuruecksetzen
#   D             Detailansicht: mit Alt <-> immer
#   F             Farben: Standard <-> Farbenblind
#   S             Darstellung: Klassisch -> Modern -> Nur Text
#   + / -         Groesse in 0,1-Schritten (0,5 - 2,0)
# Zusaetzlich mit der Maus ziehen (Mauszeiger z. B. per Strg): Main.swf legt eine unsichtbare
# Greifflaeche ueber Granate | Schild (FlashAPI, Kanaele omSetHandle / omDragMove / omDragEnd).
# Gespeichert im Spielverzeichnis unter ModPrefs/ (ueberlebt Patches), sonst im Mod-Ordner.
# Ist TTaroModUtils installiert, gilt dessen Optionsseite (ModForge haengt dann die TTaro-Huelle
# ein); Tastenkuerzel und Greifflaeche von Main.swf sind dann aus, damit nichts doppelt greift.
DEFAULT_SETTINGS = {'x': 30, 'y': 8, 'detailMode': 0, 'colorMode': 0, 'scale': 1.0, 'style': 1}
# Darstellung (wie defaultStyle in PenLight.unbound): 0 Klassisch, 1 Modern, 2 Nur Text
STYLES = 3
POSITION_STEP = 5
SCALE_STEP = 0.1
SCALE_RANGE = (0.5, 2.0)
SETTINGS_NAME = 'diedreibeiden-penlight.json'
# Vom Mod-Ordner res_mods/PnFMods/PenLight aus: PnFMods, res_mods, <Build>, bin, Spielverzeichnis.
SETTINGS_DIRS = ('/../../../../../ModPrefs', '')

# Groesse der Greifflaeche bei Skalierung 1 je Darstellung (wie PENLIGHT_SETTINGS in PenLight.unbound):
# Klassisch Granate | Schild (2 x 29 px + 4 px Abstand), Modern zwei Kapseln (72 x 18, 4 px Abstand),
# Nur Text zwei Zeilen (textWidth x 2 x textLineHeight); dazu ein Rand (links, oben, rechts, unten)
# wie dragPad*
HANDLE_SIZES = {0: (62, 29), 1: (72, 40), 2: (180, 42)}
HANDLE_PAD = (4, 12, 12, 10)

_state = {'data': None, 'disabled': False, 'results': None, 'log': [], 'ui_id': None,
          'settings': None, 'in_battle': False, 'ttaro': None,
          'ammo': ('ap', None, False)}

# Geladene Munition (ModsAPI: battle.getSelectedAmmoId, battle.getAmmoParams,
# events.onArtilleryAmmoChanged; wie PenetrationCalculator). ammoType -> Kurzname und Feld
# mit dem festen Durchschlag (mm). HE wird mit battle.getAmmoModifiers().GMPenetrationCoeffHE
# multipliziert (IFHE und andere Modifikatoren des eigenen Schiffs), SAP nicht; immer abgerundet.
AMMO_TYPES = {'AP': ('ap', None), 'HE': ('he', 'alphaPiercingHE'), 'CS': ('sap', 'alphaPiercingCS')}

# Client-Eigenheiten (python.log 15.9.0.13357625):
# - open() verlangt immer (pfad, modus); Modus 'a' nur fuer bereits vorhandene Dateien.
# - utils.getModDir() lieferte den Ordner einer anderen Mod (OvermatcherProbe).
# - print() erscheint nicht im python.log, utils.logInfo schon.


def _mod_dir():
    path = str(utils.getModDir()).replace('\\', '/').rstrip('/')
    parent, _, name = path.rpartition('/')
    if name != MOD_NAME:
        path = parent + '/' + MOD_NAME
    return path


def _mod_file(name):
    return _mod_dir() + '/' + name


def _log(message):
    line = '[%s] %s' % (MOD_NAME, message)
    try:
        utils.logInfo(line)
    except Exception:
        pass
    _state['log'] = (_state['log'] + [line])[-LOG_KEEP:]
    try:
        with open(_mod_file(LOG_FILE), 'w') as f:
            f.write('\n'.join(_state['log']) + '\n')
    except Exception:
        pass


def _get(obj, key):
    try:
        return obj[key]
    except Exception:
        return getattr(obj, key, None)


def _decode_json(text):
    for name in ('jsonDncode', 'jsonDecode'):
        decoder = getattr(utils, name, None)
        if decoder is not None:
            return decoder(text)
    raise RuntimeError('utils has no JSON decoder')


def _load_data():
    if _state['data'] is not None or _state['disabled']:
        return _state['data']
    try:
        with open(_mod_file(DATA_FILE), 'r') as f:
            data = _decode_json(f.read())
    except Exception as e:
        _log('could not load %s: %r' % (DATA_FILE, e))
        _state['disabled'] = True
        return None
    game_version = str(utils.getGameVersion())
    if str(data.get('gameVersion')) != game_version:
        # Veraltete Daten wuerden falsche Farben liefern -> lieber nichts anzeigen.
        _log('data version %s != game version %s, disabled; regenerate ships.json'
             % (data.get('gameVersion'), game_version))
        _state['disabled'] = True
        return None
    _state['data'] = data['ships']
    _log('loaded %d ships for %s' % (len(_state['data']), game_version))
    return _state['data']


def _ship_record(ships, player_id):
    name = _get(battle.getPlayerShipInfo(player_id), 'name')
    row = ships.get(name)
    if row is None:
        return name, None
    mid = row[4] if len(row) > 4 else None
    return name, {'class': row[0], 'bow': row[1], 'deck': row[2], 'caliber': row[3], 'mid': mid}


def _self_player_id(players):
    try:
        own_id = _get(battle.getSelfPlayerInfo(), 'id')
        if own_id in players:
            return own_id
    except Exception:
        pass
    own_name = _get(battle.getSelfPlayerShip(), 'playerName') or ''
    for pid in players:
        name = _get(players[pid], 'name')
        if name and own_name.endswith(name):
            return pid
    return None


def compute():
    """{player_id: {'ship': name, 'attack': color, 'defense': color}} fuer relevante Gegner."""
    ships = _load_data()
    if not ships:
        return {}
    players = battle.getPlayersInfo()
    own_id = _self_player_id(players)
    _log('%d players, own id %s' % (len(players), own_id))
    if own_id is None:
        _log('own player not found')
        return {}
    own_team = _get(players[own_id], 'teamId')
    own_name, me = _ship_record(ships, own_id)
    _log('own ship %s, team %s' % (own_name, own_team))
    if me is None:
        _log('no data for own ship %s' % own_name)
        return {}
    results = {}
    for pid in players:
        if _get(players[pid], 'teamId') == own_team:
            continue
        name, enemy = _ship_record(ships, pid)
        if enemy is None:
            _log('no data for enemy ship %s' % name)
            continue
        ammo, pen = _state['ammo'][:2]
        verdict = evaluate(me, enemy, ammo, pen)
        if verdict is not None:
            verdict['ship'] = name
            verdict['player'] = _get(players[pid], 'name')
            results[pid] = verdict
    return results


def _report(results):
    lines = ['%s attack=%s defense=%s' % (r['ship'], r['attack'] if r.get('ammo', 'ap') == 'ap'
                                          else '%s:%s' % (r['ammo'], r['attack']), r['defense'])
             for r in sorted(results.values(), key=lambda r: r['ship'])]
    if not lines:
        lines = ['(keine relevanten Gegner oder Mod inaktiv, siehe %s)' % LOG_FILE]
    _log('result:\n' + '\n'.join(lines))
    try:
        with open(_mod_file(RESULT_FILE), 'w') as f:
            f.write('\n'.join(lines))
    except Exception as e:
        _log('could not write %s: %r' % (RESULT_FILE, e))


def ttaro_installed():
    """TTaroModUtils liegt neben uns in PnFMods/ (gleiche Bedingung wie im ModForge-Manifest)."""
    if _state['ttaro'] is None:
        try:
            with open(_mod_dir() + '/../TTaroModUtils/Main.py', 'r'):
                _state['ttaro'] = True
        except Exception:
            _state['ttaro'] = False
    return _state['ttaro']


def _settings_paths():
    return [_mod_dir() + d + '/' + SETTINGS_NAME for d in SETTINGS_DIRS]


def clean_settings(raw):
    """Gelesene Werte pruefen; Unbekanntes oder Kaputtes faellt auf den Standard zurueck."""
    out = dict(DEFAULT_SETTINGS)
    for key in ('x', 'y', 'detailMode', 'colorMode', 'style'):
        try:
            out[key] = int(raw[key])
        except Exception:
            pass
    out['detailMode'] = 1 if out['detailMode'] == 1 else 0
    out['colorMode'] = 1 if out['colorMode'] == 1 else 0
    if out['style'] not in range(STYLES):
        out['style'] = DEFAULT_SETTINGS['style']
    try:
        out['scale'] = min(max(round(float(raw['scale']), 2), SCALE_RANGE[0]), SCALE_RANGE[1])
    except Exception:
        pass
    return out


def load_settings():
    for path in _settings_paths():
        try:
            with open(path, 'r') as f:
                return clean_settings(_decode_json(f.read()))
        except Exception:
            continue
    return dict(DEFAULT_SETTINGS)


def save_settings(settings):
    text = '{%s}' % ', '.join('"%s": %s' % (k, repr(settings[k])) for k in sorted(settings))
    for path in _settings_paths():
        try:
            with open(path, 'w') as f:
                f.write(text)
            return path
        except Exception:
            continue
    _log('could not save settings')
    return None


def _settings():
    if _state['settings'] is None:
        _state['settings'] = load_settings()
    return _state['settings']


def _key(*names):
    for name in names:
        value = getattr(Keys, name, None) if Keys is not None else None
        if value is not None:
            return value
    return None


def _key_actions():
    """Tastencode -> Aktion; Tasten, die der Client nicht kennt, fehlen."""
    table = [
        (('KEY_LEFTARROW',), ('move', -1, 0)), (('KEY_RIGHTARROW',), ('move', 1, 0)),
        (('KEY_UPARROW',), ('move', 0, -1)), (('KEY_DOWNARROW',), ('move', 0, 1)),
        (('KEY_HOME',), ('reset',)),
        (('KEY_D',), ('toggle', 'detailMode')), (('KEY_F',), ('toggle', 'colorMode')),
        (('KEY_S',), ('cycle', 'style', STYLES)),
        (('KEY_EQUALS',), ('scale', 1)), (('KEY_ADD', 'KEY_NUMPADPLUS'), ('scale', 1)),
        (('KEY_MINUS',), ('scale', -1)), (('KEY_NUMPADMINUS', 'KEY_SUBTRACT'), ('scale', -1)),
    ]
    out = {}
    for names, action in table:
        code = _key(*names)
        if code is not None:
            out[code] = action
    return out


def apply_action(settings, action, fine=False):
    kind = action[0]
    if kind == 'move':
        step = 1 if fine else POSITION_STEP
        settings['x'] += action[1] * step
        settings['y'] += action[2] * step
    elif kind == 'reset':
        settings['x'], settings['y'] = DEFAULT_SETTINGS['x'], DEFAULT_SETTINGS['y']
    elif kind == 'toggle':
        settings[action[1]] = 1 - settings[action[1]]
    elif kind == 'cycle':
        settings[action[1]] = (settings[action[1]] + 1) % action[2]
    elif kind == 'scale':
        value = round(settings['scale'] + action[1] * SCALE_STEP, 2)
        settings['scale'] = min(max(value, SCALE_RANGE[0]), SCALE_RANGE[1])
    return settings


def on_key(event):
    """Strg+Alt+Taste aendert eine Einstellung (Tabelle oben)."""
    try:
        if ttaro_installed() or not (event.isKeyDown() and event.isCtrlDown() and event.isAltDown()):
            return
        action = _key_actions().get(event.key)
        if action is None:
            return
        settings = apply_action(_settings(), action, fine=event.isShiftDown())
        path = save_settings(settings)
        _log('settings %r saved to %s' % (settings, path))
        _publish(_state['results'] or {})
        _update_handle()
    except Exception as e:
        _log('key handling failed: %r' % (e,))


def _update_handle():
    """Greifflaeche in Main.swf an Position und Groesse der Anzeige anpassen."""
    if flash is None:
        return
    s = _settings()
    left, top, right, bottom = HANDLE_PAD
    width, height = HANDLE_SIZES.get(s['style'], HANDLE_SIZES[DEFAULT_SETTINGS['style']])
    try:
        flash.call('omSetHandle', [s['x'] - left * s['scale'], s['y'] - top * s['scale'],
                                   (width + left + right) * s['scale'],
                                   (height + top + bottom) * s['scale'],
                                   bool(_state['in_battle']) and not ttaro_installed()])
    except Exception as e:
        _log('flash handle update failed: %r' % (e,))


def _dragged(args):
    settings = _settings()
    # Flash meldet die linke obere Ecke der Greifflaeche; die Anzeige liegt um den Rand versetzt
    x = float(args[0]) + HANDLE_PAD[0] * settings['scale']
    y = float(args[1]) + HANDLE_PAD[1] * settings['scale']
    settings['x'], settings['y'] = int(round(x)), int(round(y))
    _publish(_state['results'] or {})
    return settings


def on_drag_move(*args):
    """Waehrend des Ziehens: Anzeige mitfuehren, noch nicht speichern."""
    try:
        _dragged(args)
    except Exception as e:
        _log('drag move failed: %r' % (e,))


def on_drag_end(*args):
    try:
        settings = _dragged(args)
        _log('settings %r saved to %s (drag)' % (settings, save_settings(settings)))
    except Exception as e:
        _log('drag end failed: %r' % (e,))


def ui_payload(results):
    """Daten fuer PenLight.unbound: Schluessel = Avatar-ID (als Text) bzw. Spielername.

    Wert: [granate, schild, [ich->ziel bug, mitte, deck, ziel->ich bug, mitte, deck],
           bild_granate, bild_schild, werte]  (Bildnamen ohne .png, '' = keine Daten;
           werte = logic.numbers, mm fuer die Alt-Ansicht der Darstellungen Modern und Nur Text)
    Granate und Ziel-Teil gelten fuer die geladene Munition ('ammo': ap / he / sap); bei HE/SAP
    ist die Granate green / bow / deck / red und der Ziel-Teil der Durchschlag statt Overmatch.
    """
    by_id, by_name = {}, {}
    for pid, r in results.items():
        pair = [r['attack'], r['defense'], r['detail']] + list(detail_icons(r['detail'])) + [r['numbers']]
        by_id[str(pid)] = pair
        if r.get('player'):
            by_name[r['player']] = pair
    return {'byId': by_id, 'byName': by_name, 'settings': dict(_settings()), 'ammo': _state['ammo'][0],
            'ifhe': _state['ammo'][2]}


def _publish(results):
    try:
        if _state['ui_id'] is None:
            _state['ui_id'] = ui.createUiElement()
            ui.addDataComponentWithId(_state['ui_id'], UI_COMPONENT_ID, ui_payload({}))
        ui.updateUiElementData(_state['ui_id'], ui_payload(results))
    except Exception as e:
        _log('ui publish failed: %r' % (e,))


def _remove_ui():
    if _state['ui_id'] is None:
        return
    try:
        ui.deleteUiElement(_state['ui_id'])
    except Exception as e:
        _log('ui delete failed: %r' % (e,))
    _state['ui_id'] = None


def _refresh(*args, **kwargs):
    _log('refresh (battle shown / players updated)')
    try:
        results = compute()
    except Exception as e:
        _log('compute failed: %r' % (e,))
        return
    if results != _state['results']:
        _state['results'] = results
        _report(results)
        _publish(results)


def _he_coeff():
    """Faktor auf den HE-Durchschlag der Hauptbatterie (IFHE); nicht lesbar -> 1.0."""
    try:
        coeff = float(_get(battle.getAmmoModifiers(), 'GMPenetrationCoeffHE'))
    except Exception as e:
        _log('ammo modifiers not readable: %r' % (e,))
        return 1.0
    return coeff if coeff > 0 else 1.0


def _read_ammo(ammo_id):
    """(kurzname, durchschlag_mm, ifhe) zur Granaten-ID; unbekannt -> AP-Bewertung."""
    params = battle.getAmmoParams(ammo_id)
    name, field = AMMO_TYPES.get(str(_get(params, 'ammoType')), ('ap', None))
    if not field:
        return ('ap', None, False)
    raw = float(_get(params, field))
    coeff = _he_coeff() if name == 'he' else 1.0
    pen = floor_mm(raw * coeff)
    if not pen:
        return ('ap', None, False)
    if coeff != 1.0:
        _log('ammo %s raw %s mm, coeff %s' % (name, raw, coeff))
    return (name, pen, coeff > 1.0 + 1e-6)


def on_ammo_changed(ammo_id=None, *args):
    try:
        ammo = _read_ammo(ammo_id)
    except Exception as e:
        _log('ammo %r not readable: %r' % (ammo_id, e))
        ammo = ('ap', None, False)
    if ammo != _state['ammo']:
        _state['ammo'] = ammo
        _log('ammo %s, penetration %s mm, ifhe %s' % ammo)
        if _state['in_battle']:
            _refresh()


def _selected_ammo():
    try:
        on_ammo_changed(battle.getSelectedAmmoId(constants.WeaponType.ARTILLERY))
    except Exception as e:
        _log('selected ammo not readable: %r' % (e,))


def _on_battle_shown(*args, **kwargs):
    _state['in_battle'] = True
    _update_handle()
    _selected_ammo()
    _refresh()


def _on_battle_quit(*args, **kwargs):
    _state['results'] = None
    _state['ammo'] = ('ap', None, False)
    _state['in_battle'] = False
    _update_handle()
    _remove_ui()


def _register_flash():
    if flash is None:
        return 'missing'
    try:
        flash.addExternalCallback('omDragMove', on_drag_move)
        flash.addExternalCallback('omDragEnd', on_drag_end)
        return 'ok'
    except Exception as e:
        return 'failed: %r' % (e,)


_log('Main.py loaded, game version %s, getModDir %s -> %s, keys %d/12, flash %s, settings via %s'
     % (utils.getGameVersion(), utils.getModDir(), _mod_dir(), len(_key_actions()), _register_flash(),
        'TTaroModUtils' if ttaro_installed() else 'keys/Main.swf'))
events.onBattleShown(_on_battle_shown)
events.onPlayersListUpdated(_refresh)
events.onBattleQuit(_on_battle_quit)
events.onKeyEvent(on_key)
try:
    events.onArtilleryAmmoChanged(on_ammo_changed)
except Exception as e:
    _log('ammo events unavailable: %r' % (e,))
