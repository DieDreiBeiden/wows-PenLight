# -*- coding: utf-8 -*-
"""Erzeugt die Ampel-Icons (Granate/Schild) in Anzeigegroesse aus den 19x19-Originalen.

    python3 -I tools/make_ampel_icons.py

Quelle: assets/icons_19/{shell,shield}_{green,yellow,red}.png. Geglaettet wie die
Detail-Schiffe (make_detail_icons): Flaechen je Farbe vergroessern, Stufen abrunden,
mit Kantenglaettung auf SIZE verkleinern.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/ (gleiche Dateinamen).
"""
import glob
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_detail_icons as detail  # noqa: E402

ROOT = detail.ROOT
SOURCE_DIR = os.path.join(ROOT, 'assets', 'icons_19')
SIZE = 29  # 1,5 x 19 (gerundet), muss zu iconSize in Overmatcher.unbound passen


def color_layers(src):
    px = src.load()
    w, h = src.size
    layers = {}
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            layers.setdefault(p if p[3] else None, set()).add((x, y))
    return layers


def main():
    written = []
    for path in sorted(glob.glob(os.path.join(SOURCE_DIR, '*.png'))):
        src = Image.open(path).convert('RGBA')
        layers = color_layers(src)
        masks = detail._smooth_masks(layers, src.size)
        fills = dict((k, k) for k in layers if k is not None)
        out = detail._render(masks, fills, (SIZE, SIZE))
        name = os.path.basename(path)
        out.save(os.path.join(detail.TARGET_DIR, name))
        written.append(name)
    print('%d Icons, %dx%d: %s' % (len(written), SIZE, SIZE, ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
