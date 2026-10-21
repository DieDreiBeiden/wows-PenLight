# -*- coding: utf-8 -*-
"""Baut mod/res_mods/PnFMods/PenLight/Main.py aus src/penlight/.

Der Client laedt pro Mod eine Main.py; ob eigene Module importiert werden
duerfen, ist nicht dokumentiert. Deshalb wird alles in eine Datei kopiert.

    python3 -I tools/build_mod.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES = ['src/penlight/logic.py', 'src/penlight/mod_main.py']
TARGET = 'mod/res_mods/PnFMods/PenLight/Main.py'

HEADER = """# -*- coding: utf-8 -*-
# GENERIERT von tools/build_mod.py - nicht direkt bearbeiten.
# Quellen: %s
API_VERSION = 'API_v1.0'
"""


def _body(path):
    lines = open(os.path.join(ROOT, path), encoding='utf-8').read().splitlines()
    if lines and lines[0].startswith('# -*- coding'):
        lines = lines[1:]
    return '\n'.join(lines).strip('\n')


def build():
    parts = [HEADER % ', '.join(SOURCES)]
    for src in SOURCES:
        parts.append('\n# ---- %s ----\n%s\n' % (src, _body(src)))
    target = os.path.join(ROOT, TARGET)
    with open(target, 'w', encoding='utf-8') as f:
        f.write('\n'.join(parts))
    return target


if __name__ == '__main__':
    print(build())
