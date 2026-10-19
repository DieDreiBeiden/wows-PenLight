# -*- coding: utf-8 -*-
# GENERIERT von tools/build_mod.py - nicht direkt bearbeiten.
# Quellen: src/overmatcher/logic.py, src/overmatcher/mod_main.py
API_VERSION = 'API_v1.0'


# ---- src/overmatcher/logic.py ----
"""Overmatch-Ampel. Muss unter Python 2.7 (Spielclient) und 3.x (Tests) laufen."""

OVERMATCH_RATIO = 14.3

GREEN = 'green'
YELLOW = 'yellow'
RED = 'red'

# Werte von Ship.subtype bzw. GameParams 'species'; per Probe-Mod zu bestaetigen.
RELEVANT_CLASSES = frozenset(['Cruiser', 'Battleship'])

# Bug ueberwunden, Deck nicht: von der Ampel-Definition nicht abgedeckt.
# Annahme: gilt als "teilweise" -> Gelb.
BOW_ONLY_COLOR = YELLOW


def overmatches(caliber_mm, armor_mm):
    return caliber_mm > armor_mm * OVERMATCH_RATIO


def _zones(caliber_mm, bow_mm, deck_mm):
    return overmatches(caliber_mm, bow_mm), overmatches(caliber_mm, deck_mm)


def attack_color(my_caliber_mm, target_bow_mm, target_deck_mm):
    """Granate: kann ich das Ziel overmatchen?"""
    bow, deck = _zones(my_caliber_mm, target_bow_mm, target_deck_mm)
    if bow and deck:
        return GREEN
    if deck:
        return YELLOW
    if bow:
        return BOW_ONLY_COLOR
    return RED


def defense_color(enemy_caliber_mm, my_bow_mm, my_deck_mm):
    """Schild: kann der Gegner mich overmatchen?"""
    bow, deck = _zones(enemy_caliber_mm, my_bow_mm, my_deck_mm)
    if bow and deck:
        return RED
    if deck:
        return YELLOW
    if bow:
        return BOW_ONLY_COLOR
    return GREEN


def is_relevant(my_class, enemy_class):
    return my_class in RELEVANT_CLASSES and enemy_class in RELEVANT_CLASSES


def evaluate(me, enemy):
    """me/enemy: dict mit 'class', 'caliber', 'bow', 'deck' (mm).

    Liefert None, wenn die Paarung nicht angezeigt werden soll.
    """
    if not is_relevant(me['class'], enemy['class']):
        return None
    return {
        'attack': attack_color(me['caliber'], enemy['bow'], enemy['deck']),
        'defense': defense_color(enemy['caliber'], me['bow'], me['deck']),
    }


# ---- src/overmatcher/mod_main.py ----
# Spiel-Anbindung. Wird von tools/build_mod.py hinter logic.py in Main.py kopiert;
# battle, utils, events stellt der Client als Globals bereit (ModsAPI v1.0).
MOD_NAME = 'Overmatcher'
DATA_FILE = 'ships.json'
RESULT_FILE = 'overmatcher_last.txt'
LOG_FILE = 'overmatcher_log.txt'

_state = {'data': None, 'disabled': False, 'results': None}


def _log(message):
    # print() erscheint nicht im python.log (Probe-Befund), utils.logInfo schon.
    line = '[%s] %s' % (MOD_NAME, message)
    try:
        utils.logInfo(line)
    except Exception:
        pass
    try:
        with open(utils.getModDir() + '/' + LOG_FILE, 'a') as f:
            f.write(line + '\n')
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
        with open(utils.getModDir() + '/' + DATA_FILE) as f:
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
    return name, {'class': row[0], 'bow': row[1], 'deck': row[2], 'caliber': row[3]}


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
        verdict = evaluate(me, enemy)
        if verdict is not None:
            verdict['ship'] = name
            results[pid] = verdict
    return results


def _report(results):
    lines = ['%s attack=%s defense=%s' % (r['ship'], r['attack'], r['defense'])
             for r in sorted(results.values(), key=lambda r: r['ship'])]
    if not lines:
        lines = ['(keine relevanten Gegner oder Mod inaktiv, siehe %s)' % LOG_FILE]
    _log('result:\n' + '\n'.join(lines))
    try:
        with open(utils.getModDir() + '/' + RESULT_FILE, 'w') as f:
            f.write('\n'.join(lines))
    except Exception as e:
        _log('could not write %s: %r' % (RESULT_FILE, e))


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


def _on_battle_quit(*args, **kwargs):
    _state['results'] = None


_log('Main.py loaded, game version %s' % (utils.getGameVersion(),))
events.onBattleShown(_refresh)
events.onPlayersListUpdated(_refresh)
events.onBattleQuit(_on_battle_quit)
