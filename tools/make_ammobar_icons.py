# -*- coding: utf-8 -*-
"""Zeichnet die eigenen Teile des Munitionsleisten-Designs (seit 0.5.0).

    python3 -I tools/make_ammobar_icons.py

Die Symbole selbst (geladene Munition, Luftschlag, Schild der Kapitaensfertigkeit) sind Kopien aus den
Spieldateien (Wargaming) in ammobar/game/; per img:// sind sie aus Mods nicht erreichbar. Hier entstehen nur
Rahmen, Zonen-Balken, Kapseln mit Punkten, Farbstreifen und Leuchtringe; die Ampelfarbe sitzt ausschliesslich
in diesen Teilen.

Ausgabe: mod/res_mods/PnFMods/PenLight/ammobar/
  slot_<pal><state>.png, slot_ext_<pal><green|red>.png, slot_grey.png     Slot 46 x 46 (Klassisch)
  glow_slot_<pal><green|red>.png                                           Leuchtring 56 x 56
  seg_<pal><state>_<bits>.png, seg_grey.png                                drei Balken 46 x 5
  cap_<pal><state>_<bits>.png, cap_grey.png                                Kapsel 72 x 22 (Modern)
  glow_cap_<pal><green|red>.png                                            Leuchtring 82 x 32
  stripe_<pal><state>.png, stripe_grey.png                                 Farbstreifen 3 x 19 (Nur Text)
<pal> = '' oder 'cb_', <state> = green / yellow / red, <bits> = Bug/Heck, Mitte, Deck (1 = durch).
"""
import itertools
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_ampel_icons import AMPEL, AMPEL_CB, ROOT  # noqa: E402

TARGET_DIR = os.path.join(ROOT, 'mod', 'res_mods', 'PnFMods', 'PenLight', 'ammobar')
SS = 4
PANEL = (14, 16, 18, 215)
SLOT_FILL = (24, 27, 30, 235)
RIM = (70, 74, 78, 255)
OFF = (60, 64, 68, 255)
GREY = (120, 124, 128)
PALETTES = {'': AMPEL, 'cb_': AMPEL_CB}
STATES = ('green', 'yellow', 'red')
SLOT = 46
SEG_W, SEG_H = 46, 5
CAP_W, CAP_H = 72, 22
GLOW_PAD = 5


def _rgba(color):
    return tuple(color) + (255,)


def slot(color, width=1.0):
    im = Image.new('RGBA', (SLOT * SS, SLOT * SS), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle([0, 0, SLOT * SS - 1, SLOT * SS - 1], radius=4 * SS, fill=PANEL,
                                         outline=color, width=int(width * SS))
    return im.reduce(SS)


def segments(bits, color):
    im = Image.new('RGBA', (SEG_W * SS, SEG_H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, on in enumerate(bits):
        x0 = (i * SEG_W / 3.0 + (0 if i == 0 else 1)) * SS
        x1 = ((i + 1) * SEG_W / 3.0 - (0 if i == 2 else 1)) * SS - 1
        d.rounded_rectangle([x0, 0.5 * SS, x1, (SEG_H - 1) * SS], radius=1.5 * SS, fill=_rgba(color) if on else OFF)
    return im.reduce(SS)


def capsule(bits, color, nowhere_ring):
    """Kapsel mit Symbol-Slot links (Spiel-Symbol liegt zur Laufzeit darueber) und drei Punkten."""
    im = Image.new('RGBA', (CAP_W * SS, CAP_H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, CAP_W * SS - 1, CAP_H * SS - 1], radius=CAP_H * SS // 2, fill=PANEL,
                        outline=_rgba(color), width=int(0.9 * SS))
    d.rounded_rectangle([2 * SS, 2 * SS, 24 * SS, (CAP_H - 2) * SS], radius=3 * SS, fill=SLOT_FILL)
    for i, on in enumerate(bits):
        cx, cy, r = 40 + i * 10.5, CAP_H / 2.0, 3.6
        box = [(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS]
        if on:
            d.ellipse(box, fill=_rgba(color))
        else:
            d.ellipse(box, outline=_rgba(color if nowhere_ring else GREY), width=int(1.2 * SS))
    return im.reduce(SS)


def glow(size, radius, color):
    w, h = size
    W2, H2 = (w + 2 * GLOW_PAD) * SS, (h + 2 * GLOW_PAD) * SS
    mask = Image.new('L', (W2, H2), 0)
    p = GLOW_PAD * SS
    ImageDraw.Draw(mask).rounded_rectangle([p - 1.5 * SS, p - 1.5 * SS, W2 - p + 1.5 * SS, H2 - p + 1.5 * SS],
                                           radius=(radius + 1.5) * SS, outline=255, width=int(2.2 * SS))
    mask = mask.filter(ImageFilter.GaussianBlur(1.6 * SS))
    im = Image.new('RGBA', (W2, H2), tuple(color) + (0,))
    im.putalpha(mask.point(lambda v: min(255, int(v * 1.6))))
    return im.reduce(SS)


def stripe(color):
    return Image.new('RGBA', (3, 19), _rgba(color))


def icon_set():
    out = {'slot_grey.png': slot(RIM), 'seg_grey.png': segments((0, 0, 0), GREY),
           'cap_grey.png': capsule((0, 0, 0), GREY, False), 'stripe_grey.png': stripe(GREY)}
    combos = list(itertools.product((0, 1), repeat=3))
    for pal, palette in sorted(PALETTES.items()):
        for state in STATES:
            color = palette[state]
            out['slot_%s%s.png' % (pal, state)] = slot(_rgba(color))
            out['stripe_%s%s.png' % (pal, state)] = stripe(color)
            for bits in combos:
                key = ''.join(map(str, bits))
                out['seg_%s%s_%s.png' % (pal, state, key)] = segments(bits, color)
                out['cap_%s%s_%s.png' % (pal, state, key)] = capsule(bits, color, not any(bits))
        for state in ('green', 'red'):
            color = palette[state]
            out['slot_ext_%s%s.png' % (pal, state)] = slot(_rgba(color), 1.6)
            out['glow_slot_%s%s.png' % (pal, state)] = glow((SLOT, SLOT), 4, color)
            out['glow_cap_%s%s.png' % (pal, state)] = glow((CAP_W, CAP_H), CAP_H / 2.0, color)
    return out


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    icons = icon_set()
    for name, im in sorted(icons.items()):
        im.save(os.path.join(TARGET_DIR, name))
    print('%d Teile in %s' % (len(icons), TARGET_DIR))
    return 0


if __name__ == '__main__':
    sys.exit(main())
