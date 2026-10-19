# -*- coding: utf-8 -*-
"""Liest content/GameParams.data und erzeugt die Overmatch-Datentabelle.

GameParams.data = bytereversiertes, zlib-komprimiertes Python-2-Pickle.

    python3 -I tools/gameparams.py GameParams.data data/ships.json

Annahmen (an bekannten Schiffen zu verifizieren, siehe docs/KONZEPT.md):
- Hull-Felder 'armourExtremities' (Bug/Heck) und 'armourDeck' (Deck) in mm.
- Hauptkaliber = 'barrelDiameter' (m) der Geschuetze im Artillerie-Modul.
- Voll ausgebaut = jeweils letztes Modul in ShipUpgradeInfo.
"""
import io
import json
import pickle
import sys
import zlib

RELEVANT_SPECIES = ('Cruiser', 'Battleship')


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


def load(path):
    with open(path, 'rb') as f:
        raw = f.read()
    data = zlib.decompress(raw[::-1])
    root = _Unpickler(io.BytesIO(data), encoding='latin1').load()
    # Struktur: [ {name: entry, ...} ] oder [ {'': {name: entry}} ] je nach Build
    if isinstance(root, (list, tuple)):
        root = root[0]
    if len(root) == 1 and '' in root:
        root = root['']
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
        ships[entry.get('index') or index] = {
            'id': entry.get('id'),
            'class': species,
            'level': entry.get('level'),
            'hull': hull_name,
            'artillery': art_name,
            'bow': hull.get('armourExtremities'),
            'deck': hull.get('armourDeck'),
            'caliber': _main_caliber_mm(art),
        }
    return ships


def main(argv):
    if len(argv) != 3:
        sys.stderr.write(__doc__)
        return 2
    ships = extract(load(argv[1]))
    with open(argv[2], 'w', encoding='utf-8') as f:
        json.dump(ships, f, indent=1, sort_keys=True)
    missing = [k for k, s in ships.items() if None in (s['bow'], s['deck'], s['caliber'])]
    print('%d Schiffe, %d mit fehlenden Werten' % (len(ships), len(missing)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
