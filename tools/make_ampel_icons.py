# -*- coding: utf-8 -*-
"""Zeichnet die Ampel-Icons Granate/Schild im Stil des WoWS-HUD.

    python3 -I tools/make_ampel_icons.py

Granate = AP-Granate wie im Bewaffnungs-Fenster (grau-metallisch, schraeg nach unten rechts),
Ampelfarbe auf Spitze und Ring (wo im Original Rot ist).
Schild  = Wappenschild mit drei Sparren, Rand metallisch grau wie die Granate,
          Sparren in Ampelfarbe auf Hellgrau.
Gezeichnet mit SUPERSAMPLE-facher Aufloesung und per Mittelwert auf SIZE verkleinert.
Die frueheren 19x19-Vorlagen in assets/icons_19/ werden nicht mehr verwendet.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/{shell,shield}_{green,yellow,red,grey}.png
(grey = kein Ziel aufgeschaltet bzw. Ziel ohne Bewertung)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET_DIR = os.path.join(ROOT, 'mod', 'res_mods', 'PnFMods', 'Overmatcher')

SIZE = 29  # muss zu iconSize in Overmatcher.unbound passen
SUPERSAMPLE = 16
W = SIZE * SUPERSAMPLE

# Gruen wie die Detail-Schiffe, Orange; beides bewusst abgesetzt vom tuerkisen/gelben HUD
AMPEL = {'green': (0x3D, 0xDC, 0x5A), 'yellow': (0xFF, 0x8C, 0x00), 'red': (232, 72, 52)}
# ohne aufgeschaltetes Ziel (oder ohne Bewertung): neutrales Grau statt Ampelfarbe
NEUTRAL = {'grey': (128, 132, 136)}
OUTLINE = (24, 26, 28)
METAL = (168, 172, 176)
GUIDE_RING = (92, 94, 98)
LIGHT = (212, 214, 216)
SHELL_SCALE = 1.28
SHELL_SHIFT = 0.03  # Granate liegt sonst etwas links oben (Heck kuerzer als Spitze)


def _grid():
    y, x = np.mgrid[0:W, 0:W].astype(np.float32)
    return x / W, y / W


def _compose(layers):
    """layers: [(maske 0/1, farbe HxWx3)] von hinten nach vorn."""
    rgb = np.zeros((W, W, 3), np.float32)
    alpha = np.zeros((W, W), np.float32)
    for mask, col in layers:
        m = mask[..., None]
        rgb = rgb * (1 - m) + col * m
        alpha = np.maximum(alpha, mask)
    return rgb, alpha


def _outlined(rgb, alpha, px=1.1):
    """Dunkle Kontur und weicher Schatten wie bei den Spiel-Icons."""
    a = Image.fromarray((alpha * 255).astype(np.uint8))
    grown = np.asarray(a.filter(ImageFilter.MaxFilter(int(px * SUPERSAMPLE) | 1)), np.float32) / 255
    shadow = np.asarray(a.filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 1.2)), np.float32) / 255 * 0.55
    m = alpha[..., None]
    out = np.array(OUTLINE, np.float32) * (1 - m) + rgb * m
    out_a = np.maximum(np.maximum(grown, shadow), alpha)
    arr = np.dstack([np.clip(out, 0, 255), out_a[..., None] * 255]).astype(np.uint8)
    return Image.fromarray(arr, 'RGBA')


def shell(color):
    x, y = _grid()
    # SHELL_SCALE: gleiche Hoehe wie der Schild (sichtbar ~28 von 29 px)
    u = ((x - 0.5 - SHELL_SHIFT) + (y - 0.5 - SHELL_SHIFT)) / np.sqrt(2) / SHELL_SCALE    # entlang der Achse, Spitze bei +u
    v = (-(x - 0.5 - SHELL_SHIFT) + (y - 0.5 - SHELL_SHIFT)) / np.sqrt(2) / SHELL_SCALE   # quer zur Achse
    r, tail, ogive, tip = 0.15, -0.40, 0.12, 0.43
    t = np.clip((u - ogive) / (tip - ogive), 0, 1)
    radius = np.where(u < ogive, r, r * np.sqrt(np.clip(1 - t ** 1.6, 0, 1)))
    body = (u > tail) & (u < tip) & (np.abs(v) < radius)
    corner = 0.03  # abgerundetes Heck
    body &= ~((u < tail + corner) & (np.abs(v) > r - corner) &
              ((u - (tail + corner)) ** 2 + (np.abs(v) - (r - corner)) ** 2 > corner ** 2))
    body = body.astype(np.float32)
    s = np.clip(v / r, -1, 1)
    shade = (0.62 + 0.38 * np.cos((s + 0.35) * 1.5) - 0.18 * np.clip(s, 0, 1))[..., None]
    rgb, alpha = _compose([
        (body, np.array(METAL, np.float32) * shade),
        (body * ((u > -0.30) & (u < -0.24)), np.array(GUIDE_RING, np.float32) * shade),
        (body * ((u > -0.04) & (u < 0.03)), np.array(color, np.float32) * shade),
        (body * (u > ogive + 0.06), np.array(color, np.float32) * np.clip(shade + 0.1, 0, 1.2)),
    ])
    return _outlined(rgb, alpha)


def _shield_mask(x, y, inset=0.0):
    """Spitz zulaufender Wappenschild; inset verkleinert ihn fuer die Innenflaeche."""
    top, bottom, half = 0.04 + inset, 0.97 - inset * 2.2, 0.34 - inset
    top_y = top + 0.025 * (1 - ((x - 0.5) / 0.34) ** 2)
    t = np.clip((y - 0.30) / (bottom - 0.30), 0, 1)
    w = half * np.where(y < 0.30, 1.0, np.clip(1 - t ** 1.5, 0, 1) ** 0.75)
    return ((y > top_y) & (y < bottom) & (np.abs(x - 0.5) < w)).astype(np.float32)


def shield(color):
    x, y = _grid()
    outer = _shield_mask(x, y)
    inner = _shield_mask(x, y, inset=0.065)
    # Rand metallisch wie der Granatenkoerper (gleiches Grau, Licht von rechts)
    s = np.clip((x - 0.5) / 0.34, -1, 1)
    rim_shade = (0.62 + 0.38 * np.cos((s - 0.35) * 1.5) - 0.18 * np.clip(-s, 0, 1))[..., None]
    # Sparren mit Spitze nach oben, unten in Ampelfarbe auslaufend
    k = (y - 0.85 * np.abs(x - 0.5) - 0.03) / 0.15
    chevron = (((np.floor(k) % 2 == 0) & (k > 0)) | (k > 4.0))[..., None]
    face = np.where(chevron, np.array(color, np.float32), np.array(LIGHT, np.float32))
    face_shade = (1.0 + 0.10 * (x - 0.5) / 0.34 - 0.08 * y)[..., None]
    rgb, alpha = _compose([
        (outer, np.array(METAL, np.float32) * rim_shade),
        (_shield_mask(x, y, inset=0.055), np.array(GUIDE_RING, np.float32)),  # Fuge wie Fuehrungsring
        (inner, face * face_shade),
    ])
    return _outlined(rgb, alpha)


def main():
    written = []
    for kind, draw in (('shell', shell), ('shield', shield)):
        for state, color in list(AMPEL.items()) + list(NEUTRAL.items()):
            name = '%s_%s.png' % (kind, state)
            draw(color).reduce(SUPERSAMPLE).save(os.path.join(TARGET_DIR, name))
            written.append(name)
    print('%d Icons, %dx%d: %s' % (len(written), SIZE, SIZE, ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
