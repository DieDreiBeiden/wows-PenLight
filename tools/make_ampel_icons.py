# -*- coding: utf-8 -*-
"""Zeichnet die Ampel-Icons Granate/Schild im Stil des WoWS-HUD.

    python3 -I tools/make_ampel_icons.py

Granate = AP-Granate wie im Bewaffnungs-Fenster (grau-metallisch, schraeg nach unten rechts).
Schild  = Wappenschild mit Sparren, Rand metallisch grau wie die Granate.
Barrierearm (Pruefung nach WCAG 2.1, Variante A2): der Zustand ist auch ohne Farbe erkennbar.
Je Icon drei Segmente auf dunklem Grund mit dunklen Trennlinien; Farbe = gut/schlecht fuer mich.
Granate (ich -> Ziel), Form = Overmatch-Umfang:
  gruen  ueberall       -> alle Segmente (Spitze, Band, Heckring)
  gelb   nur Bug/Heck   -> nur die Spitze
  rot    kein Overmatch -> Schraegstrich, leere Segmente dunkel in Farbe getoent
Schild (Ziel -> ich), Form = Schutz:
  gruen  Ziel kommt nicht durch  -> voll, heil
  gelb   nur Bug/Heck            -> Fuss + unterer Sparren
  rot    Ziel kommt ueberall durch -> voll, aber gebrochen (Spalt)
grey (kein Ziel / keine Bewertung) -> alle Segmente leer
Dazu mark_star.png / mark_warning.png fuer die Extremfaelle (P3).
Geladene HE/SAP: eigene Granaten he_*.png / sap_*.png (Zustaende green, bow, deck, red, grey;
Spitze = Bug/Heck, Band + Ring = Deck) und Plaketten tag_ap/he/sap.png.
Granate: Spitze, Band, Heckring. Schild: Fuss, unterer Sparren, oberer Sparren.
Gezeichnet mit SUPERSAMPLE-facher Aufloesung und per Mittelwert auf SIZE verkleinert.
Ausgabe: mod/res_mods/PnFMods/Overmatcher/{shell,shield}_[cb_]{green,yellow,red,grey}.png
(cb_ = Farbenblind-Schema AMPEL_CB)
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
SLASH_TINT = 0.45               # 'kein Overmatch': leere Segmente so weit in Zustandsfarbe
# Granate: Form = Overmatch-Umfang (Stufe 2 = ueberall, 1 = nur Bug/Heck, 0 = keiner).
LEVEL = {'shell': {'green': 2, 'yellow': 1, 'red': 0}}
# gefuellte Segmente je Stufe (Granate: Spitze/Band/Heckring, Schild: Fuss/Sparren unten/oben)
FILL = {'shell': {2: 3, 1: 1, 0: 0}}
# Schild (Schutz): gefuellte Segmente je Farbe; rot zusaetzlich gebrochen (Zickzack-Spalt)
SHIELD_FILL = {'green': 3, 'yellow': 2, 'red': 3, 'grey': 0}
SHIELD_CRACK = [(0.70, 0.10), (0.56, 0.30), (0.64, 0.42), (0.46, 0.60), (0.53, 0.70), (0.38, 0.92)]
SHIELD_CRACK_WIDTH = 0.11
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


def _empty_color(level, color):
    return _mix(SEGMENT_GROUND, color, SLASH_TINT) if level == 0 else SEGMENT_EMPTY


def _level(kind, state):
    """Overmatch-Stufe zum Farbzustand; None = kein Ziel (grau, alles leer, kein Strich)."""
    return LEVEL[kind].get(state)


def _slash(x, y, color):
    """Schraegstrich rechts oben -> links unten mit dunklem Rand ('kein Overmatch')."""
    d = np.abs((x - 0.5) + (y - 0.5)) / np.sqrt(2)
    along = np.abs((x - 0.5) - (y - 0.5)) / np.sqrt(2)
    core = ((d < 0.055) & (along < 0.40)).astype(np.float32)
    rim = ((d < 0.095) & (along < 0.44)).astype(np.float32)
    return [(rim, np.array(SEPARATOR, np.float32)), (core, np.array(color, np.float32))]


# Granatenformen (Koordinaten entlang der Achse u, quer v; Spitze bei +u):
#   ap  = spitze Ogive (wie das AP-Symbol im Bewaffnungsfenster)
#   he  = kurz und dick, runde Nase mit Zuenderkappe und Explosionsstrahlen davor
#   sap = schlank, abgeflachte Nase mit weisser Kappe
SHELL_FORMS = {
    'ap': dict(scale=SHELL_SCALE, shift=SHELL_SHIFT, r=0.15, tail=-0.40, ogive=0.12, tip=0.43, exp=1.6, flat=None),
    'he': dict(scale=1.12, shift=-0.035, r=0.175, tail=-0.40, ogive=0.10, tip=0.31, exp=3.0, flat=None),
    'sap': dict(scale=SHELL_SCALE, shift=SHELL_SHIFT, r=0.125, tail=-0.42, ogive=0.10, tip=0.43, exp=1.4, flat=0.33),
}
# gefuellte Segmente je Zustand. AP: Overmatch-Umfang. HE/SAP: Spitze = Bug/Heck, Band + Ring = Deck.
SHELL_FILL = {
    'ap': {'green': ('tip', 'band', 'ring'), 'yellow': ('tip',), 'red': (), 'grey': ()},
    'he': {'green': ('tip', 'band', 'ring'), 'bow': ('tip',), 'deck': ('band', 'ring'), 'red': (), 'grey': ()},
}
SHELL_FILL['sap'] = SHELL_FILL['he']
# HE/SAP-Zustaende 'bow'/'deck' nutzen die Ampelfarbe 'yellow'
STATE_COLOR = {'bow': 'yellow', 'deck': 'yellow'}


def shell(state, palette=None, ammo='ap'):
    palette = palette or PALETTES['']
    color = palette[STATE_COLOR.get(state, state)]
    g = SHELL_FORMS[ammo]
    x, y = _grid()
    # scale: sichtbare Hoehe wie der Schild (~28 von 29 px); shift: Granate mittig
    u = ((x - 0.5 - g['shift']) + (y - 0.5 - g['shift'])) / np.sqrt(2) / g['scale']
    v = (-(x - 0.5 - g['shift']) + (y - 0.5 - g['shift'])) / np.sqrt(2) / g['scale']
    r, tail, ogive, tip = g['r'], g['tail'], g['ogive'], g['tip']
    t = np.clip((u - ogive) / (tip - ogive), 0, 1)
    radius = np.where(u < ogive, r, r * np.sqrt(np.clip(1 - t ** g['exp'], 0, 1)))
    nose = tip if g['flat'] is None else g['flat']
    body = (u > tail) & (u < nose) & (np.abs(v) < radius)
    corner = 0.03  # abgerundetes Heck
    body &= ~((u < tail + corner) & (np.abs(v) > r - corner) &
              ((u - (tail + corner)) ** 2 + (np.abs(v) - (r - corner)) ** 2 > corner ** 2))
    body = body.astype(np.float32)
    s = np.clip(v / r, -1, 1)
    shade = (0.62 + 0.38 * np.cos((s + 0.35) * 1.5) - 0.18 * np.clip(s, 0, 1))[..., None]
    lit = np.clip(shade + 0.1, 0, 1.2)
    edge = 0.012
    tip_from = ogive + 0.06
    tip_to = nose - (0.06 if ammo == 'sap' else 0.0)
    # Segmente: Spitze, Band, Heckring (jeweils mit dunklen Trennlinien)
    segments = {
        'tip': (body * (u > tip_from) * (u < tip_to), body * (np.abs(u - tip_from) < edge)),
        'band': (body * ((u > -0.06) & (u < 0.04)), body * ((np.abs(u + 0.06) < edge) | (np.abs(u - 0.04) < edge))),
        'ring': (body * ((u > -0.31) & (u < -0.22)), body * ((np.abs(u + 0.31) < edge) | (np.abs(u + 0.22) < edge))),
    }
    layers = [(body, np.array(METAL, np.float32) * shade)]
    filled = SHELL_FILL[ammo].get(state, ())
    empty = SEGMENT_EMPTY if filled or state == 'grey' else _mix(SEGMENT_GROUND, color, SLASH_TINT)
    for name, (segment, separator) in segments.items():
        layers.append((segment, np.array(color if name in filled else empty, np.float32) * lit))
        layers.append((separator, np.array(SEPARATOR, np.float32)))
    if ammo == 'sap':      # weisse Kappe an der flachen Nase
        layers.append((body * (u > nose - 0.05), np.array((240, 242, 244), np.float32) * lit))
        layers.append((body * (np.abs(u - (nose - 0.05)) < edge), np.array(SEPARATOR, np.float32)))
    if ammo == 'he':       # Zuenderkappe vorn
        layers.append((body * (u > tip - 0.045), np.array((240, 242, 244), np.float32) * lit))
    if state == 'red':
        layers += _slash(x, y, color)
    im = _outlined(*_compose(layers))
    if ammo == 'he':
        _he_burst(im, g)
    return im


def _he_burst(im, g):
    """Explosionsstrahlen vor der HE-Nase (weiss mit dunklem Rand)."""
    d = ImageDraw.Draw(im)
    c = 0.5 + g['shift'] + (g['tip'] + 0.02) * g['scale'] / np.sqrt(2)
    for ang in (-60, 0, 60):
        a = np.radians(45 + ang)
        p0 = ((c + 0.045 * np.cos(a)) * W, (c + 0.045 * np.sin(a)) * W)
        p1 = ((c + 0.16 * np.cos(a)) * W, (c + 0.16 * np.sin(a)) * W)
        d.line([p0, p1], fill=OUTLINE + (255,), width=int(0.12 * W))
        d.line([p0, p1], fill=(250, 250, 250, 255), width=int(0.06 * W))


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
    # Schild = Schutz: gruen voll und heil, gelb Fuss + unterer Sparren, rot voll aber gebrochen
    filled = SHIELD_FILL.get(state, 0)
    for i, segment in enumerate(segments):
        layers.append((segment, np.array(color if i < filled else SEGMENT_EMPTY, np.float32)))
    if state == 'red':
        # Bruch: dunkle Kante, darin ein durchsichtiger Spalt quer durch den Schild
        layers.append((_line_mask(SHIELD_CRACK, SHIELD_CRACK_WIDTH + 0.05) * outer, np.array(SEPARATOR, np.float32)))
        rgb, alpha = _compose(layers)
        return _outlined(rgb, alpha * (1 - _line_mask(SHIELD_CRACK, SHIELD_CRACK_WIDTH) * outer))
    return _outlined(*_compose(layers))


def _line_mask(points, width):
    im = Image.new('L', (W, W), 0)
    ImageDraw.Draw(im).line([(px * W, py * W) for px, py in points], fill=255, width=int(width * W), joint='curve')
    return np.asarray(im, np.float32) / 255


# Hervorhebung der Extremfaelle (Variante P3), als eigene Bilder rechts oben am Symbol:
# Stern = ich komme ueberall durch (Granate gruen), Warndreieck = Ziel kommt ueberall durch
# (Schild rot). Weiss mit dunklem Rand, also unabhaengig von Farbschema und Farbsehen.
MARK_SIZE = 16
MARK_DARK = (16, 18, 20, 255)
MARK_LIGHT = (250, 250, 250, 255)


def mark_star():
    S = MARK_SIZE * SUPERSAMPLE
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = S / 2, S * 0.36
    pts = []
    for i in range(8):
        ang = np.pi / 4 * i - np.pi / 2
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((c + rr * np.cos(ang), c + rr * np.sin(ang)))
    d.polygon([(c + (x - c) * 1.35, c + (y - c) * 1.35) for x, y in pts], fill=MARK_DARK)
    d.polygon(pts, fill=MARK_LIGHT)
    return im.reduce(SUPERSAMPLE)


def mark_warning():
    S = MARK_SIZE * SUPERSAMPLE
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, top, size, rim = S / 2, S * 0.10, S * 0.80, S * 0.07
    d.polygon([(cx, top - rim * 1.4), (cx + size / 2 + rim * 1.3, top + size * 0.87 + rim * 0.75),
               (cx - size / 2 - rim * 1.3, top + size * 0.87 + rim * 0.75)], fill=MARK_DARK)
    d.polygon([(cx, top), (cx + size / 2, top + size * 0.87), (cx - size / 2, top + size * 0.87)], fill=MARK_LIGHT)
    w = size * 0.15
    d.rounded_rectangle([cx - w / 2, top + size * 0.30, cx + w / 2, top + size * 0.62], radius=w / 2, fill=MARK_DARK)
    d.ellipse([cx - w / 2, top + size * 0.68, cx + w / 2, top + size * 0.68 + w], fill=MARK_DARK)
    return im.reduce(SUPERSAMPLE)


# Plakette wie die Munitions-Slots im HUD: weisse Versalien auf dunklem Grund, in Zielgroesse
# gezeichnet (scharf). Sitzt in Overmatcher.unbound links oben an der Granate.
TAG_FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'  # DejaVu-Lizenz, frei
TAG_SIZE = 8
TAG_HEIGHT = 10


def tag(text):
    font = ImageFont.truetype(TAG_FONT, TAG_SIZE)
    width = int(ImageDraw.Draw(Image.new('L', (1, 1))).textlength(text, font=font)) + 5
    im = Image.new('RGBA', (width, TAG_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, width - 1, TAG_HEIGHT - 1], radius=2, fill=(16, 18, 20, 230))
    d.text((2, 0), text, font=font, fill=(245, 245, 245, 255))
    return im


AMMO_STATES = {'he': ('green', 'bow', 'deck', 'red', 'grey'), 'sap': ('green', 'bow', 'deck', 'red', 'grey')}


def main():
    written = []
    for ammo, states in sorted(AMMO_STATES.items()):
        for prefix, palette in sorted(PALETTES.items()):
            for state in states:
                name = '%s_%s%s.png' % (ammo, prefix, state)
                shell(state, palette, ammo).reduce(SUPERSAMPLE).save(os.path.join(TARGET_DIR, name))
                written.append(name)
    for ammo in ('ap', 'he', 'sap'):
        tag(ammo.upper()).save(os.path.join(TARGET_DIR, 'tag_%s.png' % ammo))
        written.append('tag_%s.png' % ammo)
    for kind, draw in (('shell', shell), ('shield', shield)):
        for prefix, palette in sorted(PALETTES.items()):
            for state in palette:
                name = '%s_%s%s.png' % (kind, prefix, state)
                draw(state, palette).reduce(SUPERSAMPLE).save(os.path.join(TARGET_DIR, name))
                written.append(name)
    for name, draw in (('mark_star.png', mark_star), ('mark_warning.png', mark_warning)):
        draw().save(os.path.join(TARGET_DIR, name))
        written.append(name)
    print('%d Icons, %dx%d: %s' % (len(written), SIZE, SIZE, ' '.join(written)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
