# -*- coding: utf-8 -*-
"""Erzeugt die 8 Detail-Icons (ganzes Schiff je Farbkombination) aus dem Grund-Icon.

    python3 -I tools/make_detail_icons.py

Grund-Icon: assets/detail_ship_source.png. Weisse Flaechen = Sektionen, getrennt durch
den Umriss; Hintergrund und Umriss bleiben unveraendert. Zuordnung der weissen Bereiche
(4er-Nachbarschaft): der Bereich, der die oberste Zeile beruehrt, ist das Deck; der
Bereich mit dem Mittelpunkt naechst der Bildmitte ist die Mitte; die uebrigen sind Bug/Heck.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/detail_<bugheck>_<mitte>_<deck>.png, g/r,
skaliert um SCALE mit Nearest-Neighbor (scharfe Kanten statt Weichzeichnen im Spiel).
"""
import itertools
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'assets', 'detail_ship_source.png')
TARGET_DIR = os.path.join(ROOT, 'mod', 'res_mods', 'PnFMods', 'Overmatcher')

WHITE = (255, 255, 255)
COLORS = {'g': (0x3D, 0xDC, 0x5A), 'r': (0xE0, 0x00, 0x00)}  # wie Granate/Schild-Icons
SCALE = 2.5  # 50x30 -> 125x75, muss zu detailWidth/detailHeight in Overmatcher.unbound passen


def white_regions(im):
    w, h = im.size
    px = im.load()
    seen, regions = set(), []
    for y in range(h):
        for x in range(w):
            if (x, y) in seen or px[x, y][:3] != WHITE or px[x, y][3] == 0:
                continue
            stack, region = [(x, y)], []
            seen.add((x, y))
            while stack:
                cx, cy = stack.pop()
                region.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in seen \
                            and px[nx, ny][:3] == WHITE and px[nx, ny][3] > 0:
                        seen.add((nx, ny))
                        stack.append((nx, ny))
            regions.append(region)
    return regions


def classify(regions, size):
    if len(regions) != 4:
        raise SystemExit('erwartet 4 weisse Bereiche, gefunden: %d' % len(regions))
    top = min(min(y for _, y in r) for r in regions)
    deck = [r for r in regions if min(y for _, y in r) == top]
    if len(deck) != 1:
        raise SystemExit('Deck nicht eindeutig')
    hull = [r for r in regions if r is not deck[0]]
    cx = size[0] / 2.0
    hull.sort(key=lambda r: abs(sum(x for x, _ in r) / float(len(r)) - cx))
    return {'bowstern': hull[1] + hull[2], 'mid': hull[0], 'deck': deck[0]}


def main():
    src = Image.open(SOURCE).convert('RGBA')
    zones = classify(white_regions(src), src.size)
    for zone, pixels in sorted(zones.items()):
        print('%-8s %3d Pixel' % (zone, len(pixels)))
    written = []
    for combo in itertools.product('gr', repeat=3):
        im = src.copy()
        px = im.load()
        for zone, letter in zip(('bowstern', 'mid', 'deck'), combo):
            for x, y in zones[zone]:
                px[x, y] = COLORS[letter] + (px[x, y][3],)
        name = 'detail_%s.png' % '_'.join(combo)
        size = (int(round(src.size[0] * SCALE)), int(round(src.size[1] * SCALE)))
        im.resize(size, Image.NEAREST).save(os.path.join(TARGET_DIR, name))
        written.append(name)
    print('%d Dateien, %dx%d: %s' % (len(written), int(round(src.size[0] * SCALE)),
                                     int(round(src.size[1] * SCALE)), ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
