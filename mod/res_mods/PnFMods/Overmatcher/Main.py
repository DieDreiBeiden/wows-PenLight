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

# Ampel nach Spieler-Definition (docs/KONZEPT.md, Variante B). Bug/Heck ist die
# Grundvoraussetzung; Gruen erst, wenn auch Mitte und Deck overmatcht werden.
# Farben der normalen Ansicht = gut / schlecht fuer mich (Granate: ich -> Ziel, Schild: Ziel -> ich).
#   Bug/Heck  Mitte+Deck   Granate                    Schild
#   ja        beide ja     gruen (ich komme durch)    rot   (Ziel kommt ueberall durch)
#   ja        nicht beide  gelb                       gelb
#   nein      egal         rot                        gruen (Ziel kommt nicht durch)
# Die Alt-Detailansicht faerbt dagegen fuer Target und Me gleich: gruen = Overmatch (detail_icons).
# Fehlt der Mitte-Wert, entscheiden Bug/Heck und Deck allein.


def overmatches(caliber_mm, armor_mm):
    return caliber_mm > armor_mm * OVERMATCH_RATIO


LEVEL_COLORS = (RED, YELLOW, GREEN)


def _level(caliber_mm, ship):
    """2 = alle Zonen, 1 = nur Bug/Heck (plus ggf. weitere), 0 = Bug/Heck nicht."""
    if not overmatches(caliber_mm, ship['bow']):
        return 0
    rest = [ship['deck']] + ([ship['mid']] if ship.get('mid') is not None else [])
    return 2 if all(overmatches(caliber_mm, mm) for mm in rest) else 1


def attack_color(my_caliber_mm, target):
    """Granate: kann ich das Ziel overmatchen? target: dict mit 'bow', 'deck', optional 'mid'."""
    return LEVEL_COLORS[_level(my_caliber_mm, target)]


def defense_color(enemy_caliber_mm, me):
    """Schild: kann der Gegner mich overmatchen? Farbe = gut fuer mich: rot = ja, ueberall."""
    return DEFENSE_COLORS[_level(enemy_caliber_mm, me)]


DEFENSE_COLORS = (GREEN, YELLOW, RED)


def is_relevant(my_class, enemy_class):
    return my_class in RELEVANT_CLASSES and enemy_class in RELEVANT_CLASSES


def zone_detail(caliber_mm, ship):
    """Detailansicht: [bug, mitte, deck] je 1 (overmatch), 0 (nein), -1 (keine Daten)."""
    out = []
    for zone in ('bow', 'mid', 'deck'):
        mm = ship.get(zone)
        out.append(-1 if mm is None else int(overmatches(caliber_mm, mm)))
    return out


def detail_icons(detail):
    """Bildnamen der Detailansicht (ohne .png) fuer [ich->ziel..., ziel->ich...].

    Farbe wie die Ampel: g = Overmatch, r = kein Overmatch (Target und Me gleich).
    Fehlt eine Zone (-1), wird fuer diese Zeile kein Bild angezeigt ('').
    """
    def name(prefix, values):
        if -1 in values:
            return ''
        return prefix + '_'.join('g' if v else 'r' for v in values)
    # Granate = Ziel ("Target"), Schild = eigenes Schiff ("Me"); Bilder sind beschriftet
    return name('detail_target_', detail[:3]), name('detail_me_', detail[3:])


def evaluate(me, enemy):
    """me/enemy: dict mit 'class', 'caliber', 'bow', 'deck', optional 'mid' (mm).

    Liefert None, wenn die Paarung nicht angezeigt werden soll.
    """
    if not is_relevant(me['class'], enemy['class']):
        return None
    return {
        'attack': attack_color(me['caliber'], enemy),
        'defense': defense_color(enemy['caliber'], me),
        'detail': zone_detail(me['caliber'], enemy) + zone_detail(enemy['caliber'], me),
    }


# ---- src/overmatcher/mod_main.py ----
# Spiel-Anbindung. Wird von tools/build_mod.py hinter logic.py in Main.py kopiert;
# battle, utils, events stellt der Client als Globals bereit (ModsAPI v1.0);
# der Import ist eine Absicherung wie in PenetrationCalculator.
try:
    import events, ui, utils, battle
except Exception:
    pass

MOD_NAME = 'Overmatcher'
# Datenkomponente fuer Overmatcher.unbound (CC.mods_DataComponent mit dieser ID)
UI_COMPONENT_ID = 'modOvermatcher'
DATA_FILE = 'ships.json'
RESULT_FILE = 'overmatcher_last.txt'
LOG_FILE = 'overmatcher_log.txt'

LOG_KEEP = 300

_state = {'data': None, 'disabled': False, 'results': None, 'log': [], 'ui_id': None}

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
        verdict = evaluate(me, enemy)
        if verdict is not None:
            verdict['ship'] = name
            verdict['player'] = _get(players[pid], 'name')
            results[pid] = verdict
    return results


def _report(results):
    lines = ['%s attack=%s defense=%s' % (r['ship'], r['attack'], r['defense'])
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
    """Daten fuer Overmatcher.unbound: Schluessel = Avatar-ID (als Text) bzw. Spielername.

    Wert: [granate, schild, [ich->ziel bug, mitte, deck, ziel->ich bug, mitte, deck],
           bild_granate, bild_schild]  (Bildnamen ohne .png, '' = keine Daten)
    """
    by_id, by_name = {}, {}
    for pid, r in results.items():
        pair = [r['attack'], r['defense'], r['detail']] + list(detail_icons(r['detail']))
        by_id[str(pid)] = pair
        if r.get('player'):
            by_name[r['player']] = pair
    return {'byId': by_id, 'byName': by_name}


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


def _on_battle_quit(*args, **kwargs):
    _state['results'] = None
    _remove_ui()


_log('Main.py loaded, game version %s, getModDir %s -> %s'
     % (utils.getGameVersion(), utils.getModDir(), _mod_dir()))
events.onBattleShown(_refresh)
events.onPlayersListUpdated(_refresh)
events.onBattleQuit(_on_battle_quit)
