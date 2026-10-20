# -*- coding: utf-8 -*-
"""Erzeugt die 8 Detail-Icons (ganzes Schiff je Farbkombination) aus dem Grund-Icon.

    python3 -I tools/make_detail_icons.py

Grund-Icon: assets/detail_ship_source.png. Weisse Flaechen = Sektionen, getrennt durch
den Umriss; Hintergrund und Umriss bleiben unveraendert. Zuordnung der weissen Bereiche
(4er-Nachbarschaft): der Bereich, der die oberste Zeile beruehrt, ist das Deck; der
Bereich mit dem Mittelpunkt naechst der Bildmitte ist die Mitte; die uebrigen sind Bug/Heck.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/detail_<bugheck>_<mitte>_<deck>.png, g/r,
geglaettet gerendert in SCALE-facher Groesse: jede Flaeche (Hintergrund, Umriss, Sektionen)
wird SUPERSAMPLE-fach vergroessert, die Treppenstufen per Weichzeichnen + Mehrheitsentscheid
abgerundet und das Ergebnis mit Kantenglaettung auf die Zielgroesse verkleinert.
"""
import itertools
import os
import sys

from PIL import Image, ImageChops, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'assets', 'detail_ship_source.png')
TARGET_DIR = os.path.join(ROOT, 'mod', 'res_mods', 'PnFMods', 'Overmatcher')

WHITE = (255, 255, 255)
COLORS = {'g': (0x3D, 0xDC, 0x5A), 'r': (0xE0, 0x00, 0x00)}  # wie Granate/Schild-Icons
SCALE = 2.5  # 50x30 -> 125x75, muss zu detailWidth/detailHeight in Overmatcher.unbound passen
SUPERSAMPLE = 10  # Arbeitsaufloesung beim Glaetten, relativ zum Grund-Icon
SMOOTH_RADIUS = 4  # Weichzeichner in Arbeitsaufloesung; groesser = rundere Kanten


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


def _labels(src, zones):
    """Flaechen des Grund-Icons: {name: Menge von (x, y)}; 'background' ist transparent."""
    px = src.load()
    w, h = src.size
    zone_pixels = set()
    for pixels in zones.values():
        zone_pixels.update(pixels)
    colors = {}
    for y in range(h):
        for x in range(w):
            if (x, y) in zone_pixels:
                continue
            colors.setdefault(px[x, y] if px[x, y][3] else None, set()).add((x, y))
    layers = dict(('zone:' + k, set(v)) for k, v in zones.items())
    for color, pixels in colors.items():
        layers['color:%s' % (color,)] = pixels
    return layers


def _smooth_masks(layers, size):
    """Je Flaeche eine geglaettete Maske in Arbeitsaufloesung; jede Stelle gehoert genau einer."""
    big = (size[0] * SUPERSAMPLE, size[1] * SUPERSAMPLE)
    soft = {}
    for name, pixels in layers.items():
        m = Image.new('L', size, 0)
        mp = m.load()
        for x, y in pixels:
            mp[x, y] = 255
        soft[name] = m.resize(big, Image.NEAREST).filter(ImageFilter.GaussianBlur(SMOOTH_RADIUS))
    # Mehrheitsentscheid: Stelle gehoert der Flaeche mit dem hoechsten geglaetteten Wert
    names = list(soft)
    best = soft[names[0]]
    for name in names[1:]:
        best = ImageChops.lighter(best, soft[name])
    masks = {}
    taken = Image.new('L', big, 0)
    for name in names:
        is_max = ImageChops.difference(soft[name], best).point(lambda v: 255 if v == 0 else 0)
        mask = ImageChops.subtract(is_max, taken)
        taken = ImageChops.lighter(taken, mask)
        masks[name] = mask
    return masks


def _render(masks, fills, size):
    big = masks[next(iter(masks))].size
    canvas = Image.new('RGBA', big, (0, 0, 0, 0))
    for name, mask in masks.items():
        fill = fills.get(name)
        if fill is None:
            continue
        canvas.paste(Image.new('RGBA', big, fill), (0, 0), mask)
    return canvas.resize(size, Image.LANCZOS)


def main():
    src = Image.open(SOURCE).convert('RGBA')
    zones = classify(white_regions(src), src.size)
    for zone, pixels in sorted(zones.items()):
        print('%-8s %3d Pixel' % (zone, len(pixels)))
    layers = _labels(src, zones)
    masks = _smooth_masks(layers, src.size)
    size = (int(round(src.size[0] * SCALE)), int(round(src.size[1] * SCALE)))
    base_fills = {}
    for name in layers:
        if name.startswith('color:') and name != 'color:None':
            base_fills[name] = src.load()[next(iter(layers[name]))]
    written = []
    for combo in itertools.product('gr', repeat=3):
        fills = dict(base_fills)
        for zone, letter in zip(('bowstern', 'mid', 'deck'), combo):
            fills['zone:' + zone] = COLORS[letter] + (255,)
        name = 'detail_%s.png' % '_'.join(combo)
        _render(masks, fills, size).save(os.path.join(TARGET_DIR, name))
        written.append(name)
    print('%d Dateien, %dx%d: %s' % (len(written), size[0], size[1], ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
