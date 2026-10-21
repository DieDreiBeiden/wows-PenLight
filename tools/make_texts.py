# -*- coding: utf-8 -*-
"""Erzeugt die Uebersetzungen fuer die Optionsseite (TTaro Mod Config).

    python3 -I tools/make_texts.py

Quelle: tools/data/texts.json {sprache: {IDS_...: text}}. Ausgabe wie bei TTaroModUtils:
mod/res_mods/texts/<sprache>/penlight.mo (GNU gettext). Sprachen ohne eigene Texte
erhalten die englischen. Die uebrigen Beschriftungen nutzen vorhandene IDS_TT_*-Texte
von TTaroModUtils.
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'tools', 'data', 'texts.json')
TARGET = os.path.join(ROOT, 'mod', 'res_mods', 'texts')
DOMAIN = 'penlight'
# Sprachordner wie in TTaroModUtils/texts, dazu pt und zh (PortInterface, AdditionalOptions)
LANGUAGES = ['cs', 'de', 'en', 'es', 'es_mx', 'fr', 'it', 'ja', 'ko', 'nl', 'pl', 'pt', 'pt_br',
             'ru', 'th', 'tr', 'uk', 'zh', 'zh_sg', 'zh_tw']


def mo_bytes(catalog):
    """GNU-.mo-Datei (little endian, ohne Hash-Tabelle) aus {id: text}."""
    header = 'Content-Type: text/plain; charset=UTF-8\n'
    entries = sorted([('', header)] + list(catalog.items()))
    ids = [k.encode('utf-8') for k, _ in entries]
    strs = [v.encode('utf-8') for _, v in entries]
    n = len(entries)
    ids_start = 7 * 4 + 16 * n
    offsets, data = [], b''
    for s in ids:
        offsets.append((len(s), ids_start + len(data)))
        data += s + b'\0'
    strs_start = ids_start + len(data)
    sdata = b''
    str_offsets = []
    for s in strs:
        str_offsets.append((len(s), strs_start + len(sdata)))
        sdata += s + b'\0'
    out = struct.pack('<7I', 0x950412de, 0, n, 28, 28 + 8 * n, 0, 0)
    out += b''.join(struct.pack('<2I', *o) for o in offsets)
    out += b''.join(struct.pack('<2I', *o) for o in str_offsets)
    return out + data + sdata


def main():
    with open(SOURCE, encoding='utf-8') as f:
        texts = json.load(f)
    for lang in LANGUAGES:
        catalog = dict(texts['en'])
        catalog.update(texts.get(lang, {}))
        folder = os.path.join(TARGET, lang)
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, DOMAIN + '.mo'), 'wb') as f:
            f.write(mo_bytes(catalog))
    print('%d Sprachen, %d Texte' % (len(LANGUAGES), len(texts['en'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
