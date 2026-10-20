# -*- coding: utf-8 -*-
"""Zeichnet die Ampel-Icons Granate/Schild im Stil des WoWS-HUD.

    python3 -I tools/make_ampel_icons.py

Granate = AP-Granate wie im Bewaffnungs-Fenster (grau-metallisch, schraeg nach unten rechts),
Ampelfarbe auf Spitze und Ring (wo im Original Rot ist).
Schild  = Signalflaggen Hotel Yankee in Grau, Ampelfarbe auf der rechten Haelfte der H-Flagge.
Gezeichnet mit SUPERSAMPLE-facher Aufloesung und per Mittelwert auf SIZE verkleinert.
Die frueheren 19x19-Vorlagen in assets/icons_19/ werden nicht mehr verwendet.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/{shell,shield}_{green,yellow,red}.png
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_detail_icons as detail  # noqa: E402

SIZE = 29  # muss zu iconSize in Overmatcher.unbound passen
SUPERSAMPLE = 16
W = SIZE * SUPERSAMPLE

# an die HUD-Farben angelehnt
AMPEL = {'green': (76, 226, 160), 'yellow': (240, 190, 60), 'red': (232, 72, 52)}
OUTLINE = (24, 26, 28)
METAL = (168, 172, 176)
GUIDE_RING = (92, 94, 98)
LIGHT, MID, DARK = (205, 208, 210), (128, 132, 136), (88, 92, 96)


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
    u = ((x - 0.5) + (y - 0.5)) / np.sqrt(2)    # entlang der Achse, Spitze bei +u
    v = (-(x - 0.5) + (y - 0.5)) / np.sqrt(2)   # quer zur Achse
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


def flag(color):
    x, y = _grid()
    wave = 0.018 * np.sin(x * 2 * np.pi * 1.2)
    fold = (0.88 + 0.12 * np.cos(x * 2 * np.pi * 1.2 + 0.6))[..., None]  # Faltenwurf
    left, right = 0.10, 0.90
    h_mask = ((x > left) & (x < right) & (y > 0.12 + wave) & (y < 0.48 + wave)).astype(np.float32)
    y_mask = ((x > left + 0.04) & (x < right - 0.04) &
              (y > 0.50 + wave) & (y < 0.88 + wave * 1.4)).astype(np.float32)
    h_col = np.where((x < 0.5)[..., None], np.array(LIGHT, np.float32), np.array(color, np.float32))
    stripes = (np.floor((x + y) / 0.11) % 2 == 0)[..., None]
    y_col = np.where(stripes, np.array(MID, np.float32), np.array(DARK, np.float32))
    rgb, alpha = _compose([(h_mask, h_col * fold), (y_mask, y_col * fold)])
    return _outlined(rgb, alpha)


def main():
    written = []
    for kind, draw in (('shell', shell), ('shield', flag)):
        for state, color in AMPEL.items():
            name = '%s_%s.png' % (kind, state)
            draw(color).reduce(SUPERSAMPLE).save(os.path.join(detail.TARGET_DIR, name))
            written.append(name)
    print('%d Icons, %dx%d: %s' % (len(written), SIZE, SIZE, ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
