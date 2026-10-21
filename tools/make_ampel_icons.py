# -*- coding: utf-8 -*-
"""Zeichnet die Ampel-Icons Granate/Schild im Stil des WoWS-HUD.

    python3 -I tools/make_ampel_icons.py

Granate = AP-Granate wie im Bewaffnungs-Fenster (grau-metallisch, schraeg nach unten rechts).
Schild  = Wappenschild mit Sparren, Rand metallisch grau wie die Granate.
Barrierearm (Pruefung nach WCAG 2.1, Variante A2): der Zustand ist auch ohne Farbe erkennbar.
Je Icon drei Segmente auf dunklem Grund mit dunklen Trennlinien, gefuellt nach Zustand:
  green  = Overmatch ueberall   -> alle Segmente in Farbe
  yellow = nur Bug/Heck         -> Granate: Spitze, Schild: Fuss + unterer Sparren
  red    = kein Overmatch       -> Schraegstrich in Farbe, leere Segmente dunkel in Farbe getoent
  grey   = kein Ziel / keine Bewertung -> alle Segmente leer
Granate: Spitze, Band, Heckring. Schild: Fuss, unterer Sparren, oberer Sparren.
Gezeichnet mit SUPERSAMPLE-facher Aufloesung und per Mittelwert auf SIZE verkleinert.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/{shell,shield}_[cb_]{green,yellow,red,grey}.png
(cb_ = Farbenblind-Schema AMPEL_CB)
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
# Farbenblind-Schema (Okabe-Ito, unterscheidbar bei Rot-Gruen-Schwaeche): Blau = Overmatch,
# Gelb = nur Bug/Heck, Orange = kein Overmatch. Dateien mit Praefix 'cb_'.
# Blau kraeftiger als Okabe-Ito-Himmelblau, damit es sich vom Grau 'kein Ziel' abhebt.
AMPEL_CB = {'green': (0x2B, 0x8C, 0xE8), 'yellow': (0xF0, 0xE4, 0x42), 'red': (0xD5, 0x5E, 0x00)}
# Praefix im Dateinamen -> Farben (Zustandsnamen bleiben green/yellow/red/grey)
PALETTES = {'': dict(AMPEL, **NEUTRAL), 'cb_': dict(AMPEL_CB, **NEUTRAL)}
OUTLINE = (24, 26, 28)
METAL = (168, 172, 176)
GUIDE_RING = (92, 94, 98)
SEGMENT_GROUND = (46, 50, 54)   # dunkler Grund fuer die Farbsegmente (Helligkeitskontrast)
SEGMENT_EMPTY = (92, 96, 100)   # leeres Segment, Form bleibt sichtbar
SEPARATOR = (22, 24, 26)        # Trennlinie zwischen Farbe und Metall
RED_TINT = 0.45                 # 'kein Overmatch': leere Segmente so weit in Zustandsfarbe
# gefuellte Segmente je Zustand (Granate, Schild)
FILL = {'green': (3, 3), 'yellow': (1, 2), 'red': (0, 0), 'grey': (0, 0)}
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


def _mix(a, b, t):
    return tuple(p * (1 - t) + q * t for p, q in zip(a, b))


def _empty_color(state, color):
    return _mix(SEGMENT_GROUND, color, RED_TINT) if state == 'red' else SEGMENT_EMPTY


def _slash(x, y, color):
    """Schraegstrich rechts oben -> links unten mit dunklem Rand ('kein Overmatch')."""
    d = np.abs((x - 0.5) + (y - 0.5)) / np.sqrt(2)
    along = np.abs((x - 0.5) - (y - 0.5)) / np.sqrt(2)
    core = ((d < 0.055) & (along < 0.40)).astype(np.float32)
    rim = ((d < 0.095) & (along < 0.44)).astype(np.float32)
    return [(rim, np.array(SEPARATOR, np.float32)), (core, np.array(color, np.float32))]


def shell(state, palette=None):
    palette = palette or PALETTES['']
    color = palette[state]
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
    lit = np.clip(shade + 0.1, 0, 1.2)
    edge = 0.012
    # Segmente: Spitze, Band, Heckring (jeweils mit dunklen Trennlinien)
    segments = [
        (body * (u > ogive + 0.06), body * (np.abs(u - (ogive + 0.06)) < edge)),
        (body * ((u > -0.06) & (u < 0.04)), body * ((np.abs(u + 0.06) < edge) | (np.abs(u - 0.04) < edge))),
        (body * ((u > -0.31) & (u < -0.22)), body * ((np.abs(u + 0.31) < edge) | (np.abs(u + 0.22) < edge))),
    ]
    layers = [(body, np.array(METAL, np.float32) * shade)]
    filled = FILL[state][0]
    for i, (segment, separator) in enumerate(segments):
        fill = color if i < filled else _empty_color(state, color)
        layers.append((segment, np.array(fill, np.float32) * lit))
        layers.append((separator, np.array(SEPARATOR, np.float32)))
    if state == 'red':
        layers += _slash(x, y, color)
    return _outlined(*_compose(layers))


def _shield_mask(x, y, inset=0.0):
    """Spitz zulaufender Wappenschild; inset verkleinert ihn fuer die Innenflaeche."""
    top, bottom, half = 0.04 + inset, 0.97 - inset * 2.2, 0.34 - inset
    top_y = top + 0.025 * (1 - ((x - 0.5) / 0.34) ** 2)
    t = np.clip((y - 0.30) / (bottom - 0.30), 0, 1)
    w = half * np.where(y < 0.30, 1.0, np.clip(1 - t ** 1.5, 0, 1) ** 0.75)
    return ((y > top_y) & (y < bottom) & (np.abs(x - 0.5) < w)).astype(np.float32)


def shield(state, palette=None):
    palette = palette or PALETTES['']
    color = palette[state]
    x, y = _grid()
    outer = _shield_mask(x, y)
    inner = _shield_mask(x, y, inset=0.065)
    # Rand metallisch wie der Granatenkoerper (gleiches Grau, Licht von rechts)
    s = np.clip((x - 0.5) / 0.34, -1, 1)
    rim_shade = (0.62 + 0.38 * np.cos((s - 0.35) * 1.5) - 0.18 * np.clip(-s, 0, 1))[..., None]
    # Sparren mit Spitze nach oben; Segmente von unten: Fuss, unterer, oberer Sparren
    k = (y - 0.85 * np.abs(x - 0.5) - 0.03) / 0.15
    segments = [inner * (k > 4.15), inner * ((k > 2.15) & (k < 2.85)), inner * ((k > 0.15) & (k < 0.85))]
    layers = [
        (outer, np.array(METAL, np.float32) * rim_shade),
        (_shield_mask(x, y, inset=0.055), np.array(GUIDE_RING, np.float32)),  # Fuge wie Fuehrungsring
        (inner, np.array(SEGMENT_GROUND, np.float32)),
    ]
    filled = FILL[state][1]
    for i, segment in enumerate(segments):
        layers.append((segment, np.array(color if i < filled else _empty_color(state, color), np.float32)))
    if state == 'red':
        layers += _slash(x, y, color)
    return _outlined(*_compose(layers))


def main():
    written = []
    for kind, draw in (('shell', shell), ('shield', shield)):
        for prefix, palette in sorted(PALETTES.items()):
            for state in palette:
                name = '%s_%s%s.png' % (kind, prefix, state)
                draw(state, palette).reduce(SUPERSAMPLE).save(os.path.join(TARGET_DIR, name))
                written.append(name)
    print('%d Icons, %dx%d: %s' % (len(written), SIZE, SIZE, ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
