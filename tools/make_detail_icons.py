# -*- coding: utf-8 -*-
"""Zeichnet die 16 Detail-Bilder (Alt-Ansicht) im Stil der Granate/Schild-Icons.

    python3 -I tools/make_detail_icons.py

Freistehendes Schiff (Seitenansicht, Bug rechts) ohne Hintergrund: Rumpf und Aufbauten
metallisch grau wie die Granate, dunkle Kontur und weicher Schatten. Sektionen
Bug/Heck, Mitte (unten mittig) und Deck (oberer Rumpfstreifen) in Gruen/Rot
(= gut/schlecht fuer mich, Farben wie make_ampel_icons.AMPEL). Oben links die graue
Mini-Granate (Target) bzw. der Mini-Schild (Me) mit Beschriftung "TARGET"/"ME".
Gezeichnet mit SUPERSAMPLE-facher Aufloesung und per Mittelwert auf SIZE verkleinert.
Das fruehere Grund-Icon assets/detail_ship_source.png wird nicht mehr verwendet.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/detail_<me|target>_<bugheck>_<mitte>_<deck>.png (g/r)
"""
import itertools
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ampel_icons as icons  # noqa: E402

TARGET_DIR = icons.TARGET_DIR
SIZE = (125, 75)  # muss zu detailWidth/detailHeight in Overmatcher.unbound passen
SUPERSAMPLE = 8
W, H = SIZE[0] * SUPERSAMPLE, SIZE[1] * SUPERSAMPLE
SHIP_DY = 6  # Schiff nach unten versetzt, oben ist Platz fuer die Beschriftung

COLORS = {'g': icons.AMPEL['green'], 'r': icons.AMPEL['red']}
LABELS = {'me': ('ME', 'shield'), 'target': ('TARGET', 'shell')}
LABEL_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'  # DejaVu-Lizenz, frei
LABEL_SIZE = 8.5
LABEL_POS = (19, 8.5)  # linke Kante, vertikale Mitte
LABEL_COLOR = (236, 238, 240)
MINI_ICON = 15  # Kantenlaenge der Mini-Icons, linke obere Ecke bei (2, 1)

# Seitenansicht im 125x75-Raster
HULL = [(6, 38), (60, 38), (119, 35), (110, 61), (22, 61), (9, 50)]
SUPERSTRUCTURE = [
    [(46, 38), (47, 29), (52, 29), (53, 24), (60, 24), (61, 29), (72, 29), (73, 38)],  # Bruecke
    [(63, 29), (64, 22), (69, 22), (70, 29)],                                          # Schornstein
    [(55.5, 24), (56.5, 16), (57.5, 16), (58.5, 24)],                                  # Mast
    [(80, 38), (81, 34), (90, 34), (91, 38)], [(89, 35), (101, 34.2), (101, 35.6), (89, 36.6)],  # Turm vorn
    [(30, 38), (31, 34), (40, 34), (41, 38)], [(31, 35), (19, 34.2), (19, 35.6), (31, 36.6)],    # Turm achtern
]
RIM = 2.2        # grauer Rand zwischen Rumpfkante und Sektionen
GAP = 1.1        # graue Fuge zwischen den Sektionen
DECK_BOTTOM = 44.5
STERN_END, BOW_START = 38, 86


def _mask(polys):
    im = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(im)
    for poly in polys:
        d.polygon([(x * SUPERSAMPLE, (y + SHIP_DY) * SUPERSAMPLE) for x, y in poly], fill=255)
    return np.asarray(im, np.float32) / 255


def _filtered(mask, flt):
    return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(flt), np.float32) / 255


def _vshade(top, bottom):
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    return top + (bottom - top) * y


def _ship(bowstern, mid, deck):
    hull = _mask([HULL])
    sup = _mask(SUPERSTRUCTURE) * (1 - hull)
    inner = _filtered(hull, ImageFilter.MinFilter(int(RIM * SUPERSAMPLE) | 1))
    x = np.linspace(0, SIZE[0], W, dtype=np.float32)[None, :]
    y = np.linspace(0, SIZE[1], H, dtype=np.float32)[:, None] - SHIP_DY
    low = inner * (y > DECK_BOTTOM + GAP * 1.6)
    zones = [(inner * (y < DECK_BOTTOM), deck),
             (low * (x < STERN_END), bowstern),
             (low * (x > BOW_START + GAP * 2), bowstern),
             (low * (x > STERN_END + GAP * 2) * (x < BOW_START), mid)]
    metal = np.array(icons.METAL, np.float32)
    shade = _vshade(1.12, 0.78)
    rgb = np.zeros((H, W, 3), np.float32)
    alpha = np.zeros((H, W), np.float32)
    for m, col in [(sup, metal * _vshade(1.15, 0.8)), (hull, metal * shade * 0.92)] + \
            [(m, np.array(c, np.float32) * shade) for m, c in zones]:
        rgb = rgb * (1 - m[..., None]) + col * m[..., None]
        alpha = np.maximum(alpha, m)
    # dunkle Kontur und Schatten wie bei den Icons
    shape = np.maximum(hull, sup)
    grown = _filtered(shape, ImageFilter.MaxFilter(int(1.1 * SUPERSAMPLE) | 1))
    shadow = _filtered(shape, ImageFilter.GaussianBlur(SUPERSAMPLE * 1.4)) * 0.6
    a = alpha[..., None]
    rgb = np.array(icons.OUTLINE, np.float32) * (1 - a) + rgb * a
    alpha = np.maximum(alpha, np.maximum(grown, shadow))
    arr = np.dstack([np.clip(rgb, 0, 255), alpha[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def _label(text):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    font = ImageFont.truetype(LABEL_FONT, int(LABEL_SIZE * SUPERSAMPLE))
    x, y = LABEL_POS[0] * SUPERSAMPLE, LABEL_POS[1] * SUPERSAMPLE
    off = 0.6 * SUPERSAMPLE
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).text((x + off, y + off), text, font=font, fill=(10, 12, 14, 230), anchor='lm')
    im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(off)))
    ImageDraw.Draw(im).text((x, y), text, font=font, fill=LABEL_COLOR + (255,), anchor='lm')
    return im


def _mini_icon(kind):
    draw = icons.shell if kind == 'shell' else icons.shield
    px = MINI_ICON * SUPERSAMPLE
    return draw(icons.NEUTRAL['grey']).resize((px, px), Image.LANCZOS)


def render(key, combo):
    text, kind = LABELS[key]
    img = _ship(*(COLORS[c] for c in combo))
    img.alpha_composite(_mini_icon(kind), (2 * SUPERSAMPLE, 1 * SUPERSAMPLE))
    img.alpha_composite(_label(text))
    return img.reduce(SUPERSAMPLE)


def main():
    written = []
    for key in sorted(LABELS):
        for combo in itertools.product('gr', repeat=3):
            name = 'detail_%s_%s.png' % (key, '_'.join(combo))
            render(key, combo).save(os.path.join(TARGET_DIR, name))
            written.append(name)
    print('%d Dateien, %dx%d: %s' % (len(written), SIZE[0], SIZE[1], ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
