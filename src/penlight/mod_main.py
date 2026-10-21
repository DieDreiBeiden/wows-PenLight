# -*- coding: utf-8 -*-
# Spiel-Anbindung. Wird von tools/build_mod.py hinter logic.py in Main.py kopiert;
# battle, utils, events stellt der Client als Globals bereit (ModsAPI v1.0);
# der Import ist eine Absicherung wie in PenetrationCalculator.
try:
    import events, ui, utils, battle
except Exception:
    pass
try:
    import constants
except Exception:
    constants = globals().get('constants')

MOD_NAME = 'PenLight'
# Datenkomponente fuer PenLight.unbound (CC.mods_DataComponent mit dieser ID)
UI_COMPONENT_ID = 'modPenLight'
DATA_FILE = 'ships.json'
RESULT_FILE = 'penlight_last.txt'
LOG_FILE = 'penlight_log.txt'

LOG_KEEP = 300

_state = {'data': None, 'disabled': False, 'results': None, 'log': [], 'ui_id': None,
          'in_battle': False, 'ammo': ('ap', None)}

# Geladene Munition (ModsAPI: battle.getSelectedAmmoId, battle.getAmmoParams,
# events.onArtilleryAmmoChanged; wie PenetrationCalculator). ammoType -> Kurzname und Feld
# mit dem festen Durchschlag (mm); IFHE wird bewusst nicht beruecksichtigt.
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
        ammo, pen = _state['ammo']
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


def ui_payload(results):
    """Daten fuer PenLight.unbound: Schluessel = Avatar-ID (als Text) bzw. Spielername.

    Wert: [granate, schild, [ich->ziel bug, mitte, deck, ziel->ich bug, mitte, deck],
           bild_granate, bild_schild]  (Bildnamen ohne .png, '' = keine Daten)
    Granate und Ziel-Teil gelten fuer die geladene Munition ('ammo': ap / he / sap); bei HE/SAP
    ist die Granate green / bow / deck / red und der Ziel-Teil der Durchschlag statt Overmatch.
    """
    by_id, by_name = {}, {}
    for pid, r in results.items():
        pair = [r['attack'], r['defense'], r['detail']] + list(detail_icons(r['detail']))
        by_id[str(pid)] = pair
        if r.get('player'):
            by_name[r['player']] = pair
    return {'byId': by_id, 'byName': by_name, 'ammo': _state['ammo'][0]}


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


def _read_ammo(ammo_id):
    """(kurzname, durchschlag_mm) zur Granaten-ID; unbekannt -> AP-Bewertung."""
    params = battle.getAmmoParams(ammo_id)
    name, field = AMMO_TYPES.get(str(_get(params, 'ammoType')), ('ap', None))
    pen = float(_get(params, field)) if field else None
    return (name, pen) if name == 'ap' or pen else ('ap', None)


def on_ammo_changed(ammo_id=None, *args):
    try:
        ammo = _read_ammo(ammo_id)
    except Exception as e:
        _log('ammo %r not readable: %r' % (ammo_id, e))
        ammo = ('ap', None)
    if ammo != _state['ammo']:
        _state['ammo'] = ammo
        _log('ammo %s, penetration %s mm' % ammo)
        if _state['in_battle']:
            _refresh()


def _selected_ammo():
    try:
        on_ammo_changed(battle.getSelectedAmmoId(constants.WeaponType.ARTILLERY))
    except Exception as e:
        _log('selected ammo not readable: %r' % (e,))


def _on_battle_shown(*args, **kwargs):
    _state['in_battle'] = True
    _selected_ammo()
    _refresh()


def _on_battle_quit(*args, **kwargs):
    _state['results'] = None
    _state['in_battle'] = False
    _state['ammo'] = ('ap', None)
    _remove_ui()


_log('Main.py loaded, game version %s, getModDir %s -> %s'
     % (utils.getGameVersion(), utils.getModDir(), _mod_dir()))
events.onBattleShown(_on_battle_shown)
events.onPlayersListUpdated(_refresh)
events.onBattleQuit(_on_battle_quit)
try:
    events.onArtilleryAmmoChanged(on_ammo_changed)
except Exception as e:
    _log('ammo events unavailable: %r' % (e,))
