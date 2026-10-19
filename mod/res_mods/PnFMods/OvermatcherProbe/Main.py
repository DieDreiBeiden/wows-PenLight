# -*- coding: utf-8 -*-
# Probe-Mod v2.1: liest pro Spieler Klasse, Panzerungs- und Artilleriewerte aus
# shipInfo.params (GameParams im Client) und die ausgeruesteten Module.
# Schreibt probe_dump2.txt in den Mod-Ordner. Zeigt nichts an, aendert nichts.
API_VERSION = 'API_v1.0'
MOD_NAME = 'OvermatcherProbe'

MAX_DEPTH = 4
MAX_ITEMS = 200

_dumped = [False]


def _keys(obj):
    try:
        return list(obj.keys())
    except Exception:
        pass
    try:
        return [k for k in vars(obj) if not k.startswith('_')]
    except Exception:
        pass
    return [k for k in dir(obj) if not k.startswith('_')]


def _get(obj, key):
    try:
        return obj[key]
    except Exception:
        pass
    try:
        return getattr(obj, key)
    except Exception as e:
        return '<error %r>' % (e,)


def _is_scalar(value):
    return value is None or isinstance(value, (bool, int, long, float, basestring))


def _ser(value, depth=0):
    if _is_scalar(value):
        return repr(value)
    if depth >= MAX_DEPTH:
        return '<%s ...>' % type(value).__name__
    if isinstance(value, (list, tuple)):
        items = [_ser(v, depth + 1) for v in value[:MAX_ITEMS]]
        if len(value) > MAX_ITEMS:
            items.append('... (%d total)' % len(value))
        return '[' + ', '.join(items) + ']'
    keys = _keys(value)
    parts = []
    for k in sorted(keys, key=str)[:MAX_ITEMS]:
        v = _get(value, k)
        if callable(v):
            continue
        parts.append('%r: %s' % (k, _ser(v, depth + 1)))
    if len(keys) > MAX_ITEMS:
        parts.append('... (%d keys total)' % len(keys))
    return '{' + ', '.join(parts) + '}'


def _module_keys(params, suffix):
    return [k for k in _keys(params) if str(k).endswith(suffix)]


def _hull_summary(hull):
    out = {}
    for k in _keys(hull):
        ks = str(k)
        if ks.startswith('armour') or ks.startswith('armor') or ks in ('health', 'Bow', 'Cit', 'Cas', 'SG', 'Hull'):
            out[ks] = _get(hull, k)
    return out


def _artillery_summary(art):
    out = {}
    for k in _keys(art):
        v = _get(art, k)
        if _is_scalar(v):
            continue
        sub = _keys(v)
        if 'barrelDiameter' in sub or 'ammoList' in sub:
            out[str(k)] = dict((f, _get(v, f)) for f in ('barrelDiameter', 'ammoList', 'numBarrels', 'typeinfo') if f in sub)
    return out


def _dump():
    lines = []

    def section(title, value):
        lines.append('===== %s =====' % title)
        lines.append(_ser(value) if not isinstance(value, basestring) else value)

    try:
        section('gameVersion', repr(utils.getGameVersion()))
        players = battle.getPlayersInfo()
        for pid in players:
            p = players[pid]
            # shipInfo aus getPlayersInfo() ist nur ein leeres Geruest (v2-Befund),
            # die gefuellte Variante kommt aus getPlayerShipInfo().
            info = battle.getPlayerShipInfo(pid)
            params = _get(info, 'params')
            hull = _get(params, 'A_Hull')
            section('%s | access check' % pid, {
                'info.type': type(info).__name__,
                'params.type': type(params).__name__,
                'A_Hull.type': type(hull).__name__,
                'A_Hull.armourDeck': _get(hull, 'armourDeck'),
                'A_Hull.armourExtremities': _get(hull, 'armourExtremities'),
                'params.keys': sorted(str(k) for k in _keys(params)),
            })
            tag = '%s %s team=%s' % (pid, _get(info, 'name'), _get(p, 'teamId'))
            section(tag + ' | basics', {
                'shipParamsId': _get(p, 'shipParamsId'),
                'shipId': _get(p, 'shipId'),
                'subtype': _get(info, 'subtype'),
                'subtypeIDS': _get(info, 'subtypeIDS'),
                'level': _get(info, 'level'),
                'typeinfo': _get(params, 'typeinfo'),
            })
            section(tag + ' | shipComponents', _get(p, 'shipComponents'))
            section(tag + ' | ShipUpgradeInfo', _get(params, 'ShipUpgradeInfo'))
            for hk in _module_keys(params, '_Hull'):
                section(tag + ' | ' + hk, _hull_summary(_get(params, hk)))
            for ak in _module_keys(params, '_Artillery'):
                section(tag + ' | ' + ak, _artillery_summary(_get(params, ak)))
    except Exception as e:
        section('ERROR', repr(e))

    text = '\n'.join(lines)
    print('[%s] dump written (%d chars)' % (MOD_NAME, len(text)))
    try:
        with open(utils.getModDir() + '/probe_dump2.txt', 'w') as f:
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
