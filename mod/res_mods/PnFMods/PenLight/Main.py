# -*- coding: utf-8 -*-
# GENERIERT von tools/build_mod.py - nicht direkt bearbeiten.
# Quellen: src/penlight/logic.py, src/penlight/mod_main.py
API_VERSION = 'API_v1.0'


# ---- src/penlight/logic.py ----
"""Overmatch-Ampel. Muss unter Python 2.7 (Spielclient) und 3.x (Tests) laufen."""

OVERMATCH_RATIO = 14.3

GREEN = 'green'
YELLOW = 'yellow'
RED = 'red'

# Werte von Ship.subtype bzw. GameParams 'species'; per Probe-Mod zu bestaetigen.
RELEVANT_CLASSES = frozenset(['Cruiser', 'Battleship'])
# HE/SAP-Durchschlag wird gegen jede Klasse mit Daten bewertet (eigenes Schiff: jede Klasse mit
# geladener HE/SAP); AP-Overmatch und Schild bleiben bei Kreuzern und Schlachtschiffen.
PEN_CLASSES = frozenset(['Destroyer', 'Cruiser', 'Battleship', 'AirCarrier', 'Submarine'])
GREY = 'grey'

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


# HE/SAP: Durchschlag je Granate (alphaPiercingHE x IFHE-Faktor / alphaPiercingCS), abgerundet (floor_mm).
# Gleichstand zaehlt als Durchschlag (Nutzervorgabe). Ampel nur fuer das Ziel, Zonen Bug/Heck und Deck:
#   Bug/Heck  Deck   Zustand
#   ja        ja     green  (dazu Stern wie bei AP)
#   ja        nein   bow    (orange, Spitze gefuellt)
#   nein      ja     deck   (orange, Band + Ring gefuellt)
#   nein      nein   red    (Schraegstrich)
PEN_AMMO = ('he', 'sap')


def floor_mm(value):
    """Durchschlag in ganzen mm, immer abgerundet; die Toleranz faengt Gleitkomma-Reste (39.99999).
    Ohne math-Modul (Import in der Client-Sandbox ungeprueft); Werte sind nie negativ."""
    return int(value + 1e-6)


def penetrates(pen_mm, armor_mm):
    return pen_mm >= armor_mm


def pen_detail(pen_mm, ship):
    """Wie zone_detail, aber fuer HE/SAP-Durchschlag: [bug, mitte, deck] je 1/0/-1."""
    return [-1 if ship.get(z) is None else int(penetrates(pen_mm, ship[z])) for z in ('bow', 'mid', 'deck')]


def pen_state(pen_mm, ship):
    bow, deck = penetrates(pen_mm, ship['bow']), penetrates(pen_mm, ship['deck'])
    if bow and deck:
        return GREEN
    if bow:
        return 'bow'
    return 'deck' if deck else RED


def evaluate(me, enemy, ammo='ap', pen_mm=None):
    """me/enemy: dict mit 'class', 'caliber', 'bow', 'deck', optional 'mid' (mm).

    ammo/pen_mm: geladene Munition ('ap', 'he', 'sap') und ihr Durchschlag (mm, nur HE/SAP).
    Bei HE/SAP bewerten 'attack' und der Target-Teil von 'detail' den Durchschlag statt des
    Overmatch; Schild und Me-Teil bleiben AP-Overmatch des Gegners.
    HE/SAP wird auch fuer Zerstoerer, Traeger und U-Boote bewertet; Schild und Me-Teil gibt es
    nur bei Kreuzer/Schlachtschiff-Paarungen, sonst grau bzw. unbekannt (-1).
    Liefert None, wenn die Paarung nicht angezeigt werden soll.
    """
    he = ammo in PEN_AMMO and pen_mm is not None
    ap_rated = is_relevant(me['class'], enemy['class'])
    if not ap_rated and not (he and enemy['class'] in PEN_CLASSES):
        return None
    return {
        'ammo': ammo if he else 'ap',
        'attack': pen_state(pen_mm, enemy) if he else attack_color(me['caliber'], enemy),
        'defense': defense_color(enemy['caliber'], me) if ap_rated else GREY,
        'detail': (pen_detail(pen_mm, enemy) if he else zone_detail(me['caliber'], enemy))
        + (zone_detail(enemy['caliber'], me) if ap_rated else [-1, -1, -1]),
    }


# ---- src/penlight/mod_main.py ----
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
          'in_battle': False, 'ammo': ('ap', None, False)}

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
    return {'byId': by_id, 'byName': by_name, 'ammo': _state['ammo'][0], 'ifhe': _state['ammo'][2]}


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
    _selected_ammo()
    _refresh()


def _on_battle_quit(*args, **kwargs):
    _state['results'] = None
    _state['in_battle'] = False
    _state['ammo'] = ('ap', None, False)
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
