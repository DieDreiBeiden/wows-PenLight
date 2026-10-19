# -*- coding: utf-8 -*-
"""Liest content/GameParams.data und erzeugt die Overmatch-Datentabelle.

GameParams.data = bytereversiertes, zlib-komprimiertes Python-2-Pickle.

    python3 -I tools/gameparams.py GameParams.data ships_full.json \
        mod/res_mods/PnFMods/Overmatcher/ships.json 15,9,0,13357625

Spielversion so, wie utils.getGameVersion() sie liefert (python.log / Probe-Dump).

Panzerung: Hull-Modul 'armor' = {(lage << 16) | material_id: mm}, Lage 1 = aussen.
Material-Namen: tools/data/collision_materials.json.
- Bug/Heck = Seitenbeplankung Bug ('Bow_ConstrSide'), Fallback Heck.
- Deck     = duennste Mittschiffs-Deckplatte ('Cas_Deck', 'SSC_Deck').
Die Felder 'armourDeck'/'armourExtremities' sind in Build 15.9 nur Platzhalter [-1, -1].
- Hauptkaliber = 'barrelDiameter' (m) der Geschuetze im Artillerie-Modul.
- Voll ausgebaut = jeweils letztes Modul in ShipUpgradeInfo.
"""
import io
import json
import os
import pickle
import sys
import zlib

RELEVANT_SPECIES = ('Cruiser', 'Battleship')

BOW_MATERIALS = ('Bow_ConstrSide', 'St_ConstrSide')
DECK_MATERIALS = ('Cas_Deck', 'SSC_Deck')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'collision_materials.json')) as _f:
    MATERIAL_NAMES = json.load(_f)


def outer_plates(armor):
    """{material_name: mm} der aeussersten Lage, ohne 0-mm-Eintraege."""
    out = {}
    for key, mm in armor.items():
        layer, material = key >> 16, key & 0xFFFF
        if layer != 1 or not mm or material >= len(MATERIAL_NAMES):
            continue
        out[MATERIAL_NAMES[material]] = mm
    return out


def bow_mm(plates):
    for name in BOW_MATERIALS:
        if name in plates:
            return plates[name]
    return None


def deck_mm(plates):
    values = [plates[n] for n in DECK_MATERIALS if n in plates]
    return min(values) if values else None


class GPObject(dict):
    def __setstate__(self, state):
        if isinstance(state, tuple):
            state = state[-1] if state and isinstance(state[-1], dict) else {}
        if isinstance(state, dict):
            self.update(state)


def _reconstructor(cls, base, state):
    obj = cls()
    if state is not None:
        obj.__setstate__(state)
    return obj


class _Unpickler(pickle.Unpickler):
    _classes = {}

    def find_class(self, module, name):
        if module in ('copy_reg', 'copyreg') and name == '_reconstructor':
            return _reconstructor
        if module in ('__builtin__', 'builtins'):
            return super().find_class('builtins', name)
        key = (module, name)
        if key not in self._classes:
            self._classes[key] = type(str(name), (GPObject,), {})
        return self._classes[key]


def load(path, region='EU'):
    with open(path, 'rb') as f:
        raw = f.read()
    data = zlib.decompress(raw[::-1])
    root = _Unpickler(io.BytesIO(data), encoding='latin1').load()
    # Build 15.9: {region: {name: entry}} mit Regionen '', 'EU', 'NA', ...
    # Aeltere Builds: [ {name: entry} ]
    if isinstance(root, (list, tuple)):
        root = root[0]
    for key in (region, ''):
        if key in root and isinstance(root[key], dict):
            return root[key]
    return root


def _typeinfo(entry):
    ti = entry.get('typeinfo') or {}
    return ti.get('type'), ti.get('species')


def _final_modules(entry, uc_type):
    """Komponentennamen des letzten Upgrades vom Typ uc_type (z. B. '_Hull')."""
    upgrades = entry.get('ShipUpgradeInfo') or {}
    candidates = {}
    for name, up in upgrades.items():
        if isinstance(up, dict) and up.get('ucType') == uc_type:
            candidates[name] = up
    referenced = set(up.get('prev') for up in candidates.values())
    finals = [n for n in candidates if n not in referenced]
    if not finals:
        return None
    components = candidates[sorted(finals)[-1]].get('components') or {}
    return components


def _module_names(entry, suffix):
    return sorted(k for k in entry if isinstance(k, str) and k.endswith(suffix))


def _pick(entry, suffix, comp_key, uc_type):
    comps = _final_modules(entry, uc_type)
    if comps and comps.get(comp_key):
        name = comps[comp_key][0]
        if name in entry:
            return name
    names = _module_names(entry, suffix)
    return names[-1] if names else None


def _main_caliber_mm(artillery):
    calibers = [v.get('barrelDiameter') for v in artillery.values()
                if isinstance(v, dict) and v.get('barrelDiameter')]
    return round(max(calibers) * 1000, 1) if calibers else None


def extract(params):
    ships = {}
    for index, entry in params.items():
        if not isinstance(entry, dict):
            continue
        typ, species = _typeinfo(entry)
        if typ != 'Ship' or species not in RELEVANT_SPECIES:
            continue
        hull_name = _pick(entry, '_Hull', 'hull', '_Hull')
        art_name = _pick(entry, '_Artillery', 'artillery', '_Artillery')
        hull = entry.get(hull_name) or {}
        art = entry.get(art_name) or {}
        # Schluessel = voller Name wie shipInfo.name im Client (z. B. PJSB018_Yamato_1944)
        ships[index] = {
            'id': entry.get('id'),
            'index': entry.get('index'),
            'class': species,
            'level': entry.get('level'),
            'hull': hull_name,
            'artillery': art_name,
            'bow': bow_mm(outer_plates(hull.get('armor') or {})),
            'deck': deck_mm(outer_plates(hull.get('armor') or {})),
            'caliber': _main_caliber_mm(art),
        }
    return ships


def mod_table(ships, game_version):
    """Kompakte Tabelle fuer die Mod: {name: [klasse, bug, deck, kaliber]}."""
    table = {}
    for name, s in ships.items():
        if name.startswith('PX') or None in (s['bow'], s['deck'], s['caliber']):
            continue  # Event-/Operationsschiffe bzw. unvollstaendige Daten
        table[name] = [s['class'], s['bow'], s['deck'], s['caliber']]
    return {'gameVersion': game_version, 'ships': table}


def main(argv):
    """gameparams.py GameParams.data ships_full.json [mod_ships.json SPIELVERSION]"""
    if len(argv) not in (3, 5):
        sys.stderr.write(__doc__)
        return 2
    ships = extract(load(argv[1]))
    with open(argv[2], 'w', encoding='utf-8') as f:
        json.dump(ships, f, indent=1, sort_keys=True)
    missing = [k for k, s in ships.items() if None in (s['bow'], s['deck'], s['caliber'])]
    print('%d Schiffe, %d mit fehlenden Werten' % (len(ships), len(missing)))
    if len(argv) == 5:
        table = mod_table(ships, argv[4])
        with open(argv[3], 'w', encoding='utf-8') as f:
            json.dump(table, f, separators=(',', ':'), sort_keys=True)
        print('Mod-Tabelle: %d Schiffe, Version %s' % (len(table['ships']), argv[4]))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
