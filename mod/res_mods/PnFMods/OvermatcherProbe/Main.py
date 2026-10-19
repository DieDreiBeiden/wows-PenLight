# -*- coding: utf-8 -*-
# Probe-Mod: schreibt die im Gefecht verfuegbaren Spieler-/Schiffsdaten in
# probe_dump.txt im Mod-Ordner (und ins python.log). Zeigt nichts an, aendert nichts.
API_VERSION = 'API_v1.0'
MOD_NAME = 'OvermatcherProbe'

_dumped = [False]


def _public_attrs(obj):
    out = {}
    for name in dir(obj):
        if name.startswith('_'):
            continue
        try:
            value = getattr(obj, name)
        except Exception as e:
            value = '<error %r>' % (e,)
        if callable(value):
            continue
        out[name] = repr(value)
    return out


def _dump():
    lines = []

    def section(title, value):
        lines.append('===== %s =====' % title)
        lines.append(repr(value))

    try:
        section('gameVersion', utils.getGameVersion())
        players = battle.getPlayersInfo()
        section('getPlayersInfo', players)
        for player_id in players:
            try:
                ship_info = battle.getPlayerShipInfo(player_id)
                section('getPlayerShipInfo(%s)' % player_id, ship_info)
                section('getPlayerShipInfo(%s) attrs' % player_id, _public_attrs(ship_info))
            except Exception as e:
                section('getPlayerShipInfo(%s) ERROR' % player_id, e)
        own = battle.getSelfPlayerShip()
        section('getSelfPlayerShip attrs', _public_attrs(own))
        for ship in battle.getAllShips():
            section('getAllShips item', _public_attrs(ship))
    except Exception as e:
        section('ERROR', e)

    text = '\n'.join(lines)
    print('[%s]\n%s' % (MOD_NAME, text))
    try:
        with open(utils.getModDir() + '/probe_dump.txt', 'w') as f:
            f.write(text)
    except Exception as e:
        print('[%s] could not write file: %r' % (MOD_NAME, e))


def onBattleShown(*args, **kwargs):
    if not _dumped[0]:
        _dumped[0] = True
        _dump()


def onBattleQuit(*args, **kwargs):
    _dumped[0] = False


events.onBattleShown(onBattleShown)
events.onBattleQuit(onBattleQuit)
