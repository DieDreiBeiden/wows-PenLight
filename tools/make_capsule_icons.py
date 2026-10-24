# -*- coding: utf-8 -*-
"""Zeichnet das Symbol-Set "Status-Kapseln" (Entwurf 1, Probe im Branch Test).

    python3 -I tools/make_capsule_icons.py

Zwei Kapseln uebereinander: oben ich -> Ziel (Munition AP/HE/SAP, HE optional mit IFHE-Marke),
unten Ziel -> ich (Schild, AP des Ziels). Drei Punkte = Bug/Heck, Mitte, Deck; gefuellt = kommt durch.
Farbe nur fuer die Aussage: Text und Symbol weiss, Punkte in der Zustandsfarbe; nur die Extremfaelle
(ich ueberall durch / Ziel ueberall durch) faerben auch Text bzw. Symbol und bekommen einen Rahmen.
"Nirgends" zeigt die leeren Punkte in der Zustandsfarbe umrandet, damit es sich von "kein Ziel" abhebt.

Ausgabe: mod/res_mods/PnFMods/PenLight/capsule/
  atk_<ap|he|he_if|sap>_<palette><bug><mitte><deck>.png   z. B. atk_he_cb_101.png
  atk_<...>_grey.png, def_<palette><bug><mitte><deck>.png, def_grey.png
  glow_atk[_if][_cb].png, glow_def[_cb].png: Leuchtring der Randfaelle (GLOW_PAD px groesser)
  alt/: Teile der Alt-Ansicht (ausgeklappte Kapseln): panel*, glow_*, dot_fill_*/dot_ring_*, shield*
"""
import itertools
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_ampel_icons import AMPEL, AMPEL_CB, ROOT  # noqa: E402

TARGET_DIR = os.path.join(ROOT, 'mod', 'res_mods', 'PnFMods', 'PenLight', 'capsule')
SS = 4
HEIGHT = 18
WIDTH = {'atk': 62, 'atk_if': 72, 'def': 62}
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'  # DejaVu-Lizenz, frei
WHITE = (236, 238, 240)
# Kontrast (WCAG 1.4.11, >= 3:1) auch auf heller Gischt/Himmel: Grund 84 % deckend, Grau aufgehellt
DIM = (140, 144, 148)
PANEL = (14, 16, 18, 215)
RIM = (255, 255, 255, 46)   # feine helle Kante, damit die Kapsel sich auf dunklem Wasser abhebt
PALETTES = {'': AMPEL, 'cb_': AMPEL_CB}
DOT_R, DOT_STEP = 3.4, 10


def attack_state(zones):
    if zones is None:
        return 'grey'
    return 'green' if all(zones) else ('red' if not any(zones) else 'yellow')


def defense_state(zones):
    """Gut fuer mich: Ziel kommt nirgends durch = gruen, ueberall = rot."""
    if zones is None:
        return 'grey'
    return 'red' if all(zones) else ('green' if not any(zones) else 'yellow')


def _font(px):
    return ImageFont.truetype(FONT_BOLD, int(px * SS))


def _shield(d, x, y, s, col, width):
    k = SS
    pts = [(0.5, 0.06), (0.88, 0.20), (0.84, 0.56), (0.5, 0.94), (0.16, 0.56), (0.12, 0.20), (0.5, 0.06)]
    d.line([((x + px * s) * k, (y + py * s) * k) for px, py in pts], fill=col, width=int(width * k), joint='curve')
    d.line([((x + 0.5 * s) * k, (y + 0.28 * s) * k), ((x + 0.5 * s) * k, (y + 0.72 * s) * k)], fill=col, width=int(width * k))


def _shield_filled(d, x, y, s, col):
    k = SS
    pts = [(0.5, 0.06), (0.88, 0.20), (0.84, 0.56), (0.5, 0.94), (0.16, 0.56), (0.12, 0.20)]
    d.polygon([((x + px * s) * k, (y + py * s) * k) for px, py in pts], fill=col)
    d.line([((x + 0.5 * s) * k, (y + 0.24 * s) * k), ((x + 0.5 * s) * k, (y + 0.58 * s) * k)], fill=PANEL[:3], width=int(1.8 * k))
    r = 0.075 * s
    cx, cy = x + 0.5 * s, y + 0.74 * s
    d.ellipse([(cx - r) * k, (cy - r) * k, (cx + r) * k, (cy + r) * k], fill=PANEL[:3])


def capsule(kind, zones, palette, ammo='AP', ifhe=False):
    """kind 'atk' oder 'def'; zones (bug, mitte, deck) mit 1/0 oder None (kein Ziel)."""
    w = WIDTH['atk_if' if ifhe else kind]
    im = Image.new('RGBA', (w * SS, HEIGHT * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, w * SS - 1, HEIGHT * SS - 1], radius=HEIGHT * SS // 2, fill=PANEL,
                        outline=RIM, width=int(0.8 * SS))
    state = attack_state(zones) if kind == 'atk' else defense_state(zones)
    col = DIM if state == 'grey' else palette[state]
    extreme = (kind == 'atk' and state == 'green') or (kind == 'def' and state == 'red')
    label = col if extreme else (DIM if state == 'grey' else WHITE)
    if kind == 'atk':
        small = len(ammo) > 2
        d.text((7 * SS, (3.4 if small else 2.2) * SS), ammo, font=_font(8.5 if small else 10.5), fill=label)
        if ifhe:   # hochgestelltes "IF" ohne Kasten, in 1x noch lesbar
            d.text((25.5 * SS, 1.0 * SS), 'IF', font=_font(8), fill=label)
    else:
        if extreme:   # Ziel kommt ueberall durch: Schild gefuellt mit "!" (Hinweis auch ohne Farbe)
            _shield_filled(d, 6, 2.5, 13, label)
        else:
            _shield(d, 6, 2.5, 13, label, 1.5)
    nowhere = zones is not None and not any(zones)
    x0 = w - 3 * DOT_STEP + 3
    for i in range(3):
        cx, cy = x0 + i * DOT_STEP, HEIGHT / 2
        box = [(cx - DOT_R) * SS, (cy - DOT_R) * SS, (cx + DOT_R) * SS, (cy + DOT_R) * SS]
        if zones is not None and zones[i]:
            d.ellipse(box, fill=col)
        else:
            ring = col if nowhere else DIM
            d.ellipse(box, outline=ring + (255,), width=int(1.2 * SS))
    if extreme:
        d.rounded_rectangle([0, 0, w * SS - 1, HEIGHT * SS - 1], radius=HEIGHT * SS // 2,
                            outline=col + (255,), width=int(1.3 * SS))
    return im.reduce(SS)


GLOW_PAD = 5   # px Rand rund um die Kapsel fuer den Leuchtring


def glow(kind, palette, ifhe=False, size=None, radius=None):
    """Weicher Leuchtring in Zustandsfarbe um eine Flaeche (Randfaelle; pulsiert in der Anzeige)."""
    from PIL import ImageFilter
    w, h = size or (WIDTH['atk_if' if ifhe else kind], HEIGHT)
    r = radius if radius is not None else h / 2
    color = palette['green' if kind == 'atk' else 'red']
    W2, H2 = (w + 2 * GLOW_PAD) * SS, (h + 2 * GLOW_PAD) * SS
    mask = Image.new('L', (W2, H2), 0)
    md = ImageDraw.Draw(mask)
    p = GLOW_PAD * SS
    md.rounded_rectangle([p - 1.5 * SS, p - 1.5 * SS, W2 - p + 1.5 * SS, H2 - p + 1.5 * SS], radius=(r + 1.5) * SS,
                         outline=255, width=int(2.2 * SS))
    mask = mask.filter(ImageFilter.GaussianBlur(1.6 * SS))
    im = Image.new('RGBA', (W2, H2), color + (0,))
    im.putalpha(mask.point(lambda v: min(255, int(v * 1.6))))
    return im.reduce(SS)


# ---------------------------------------------------------------- Alt-Ansicht (Variante A)
# Ausgeklappte Kapseln: Flaeche, Punkte und Schild als Bilder; Munition, Zonen-Namen, mm-Werte und
# Schiffsname setzt die Anzeige als Text darauf (englisch, siehe PenLight.unbound).
ALT_W, ALT_H, ALT_R = 250, 56, 14   # Platz fuer 12-px-Text ohne Skalierung (Kopfzeile, Zonenname und Wert)
DOT_PX = 8


def alt_panel(kind=None, palette=None):
    """Grundflaeche; kind gesetzt = Randfall mit Rahmen in Zustandsfarbe."""
    im = Image.new('RGBA', (ALT_W * SS, ALT_H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = [0, 0, ALT_W * SS - 1, ALT_H * SS - 1]
    d.rounded_rectangle(box, radius=ALT_R * SS, fill=PANEL, outline=RIM, width=int(0.8 * SS))
    if kind:
        col = palette['green' if kind == 'atk' else 'red']
        d.rounded_rectangle(box, radius=ALT_R * SS, outline=col + (255,), width=int(1.3 * SS))
    return im.reduce(SS)


def alt_dot(color, filled):
    im = Image.new('RGBA', (DOT_PX * SS, DOT_PX * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r = DOT_PX / 2, DOT_R
    box = [(c - r) * SS, (c - r) * SS, (c + r) * SS, (c + r) * SS]
    if filled:
        d.ellipse(box, fill=color + (255,))
    else:
        d.ellipse(box, outline=color + (255,), width=int(1.2 * SS))
    return im.reduce(SS)


def alt_shield(color, warn=False):
    im = Image.new('RGBA', (14 * SS, 14 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if warn:
        _shield_filled(d, 0.5, 0.5, 13, color)
    else:
        _shield(d, 0.5, 0.5, 13, color, 1.5)
    return im.reduce(SS)


def alt_set():
    out = {'alt/panel.png': alt_panel(), 'alt/dot_ring_grey.png': alt_dot(DIM, False),
           'alt/shield.png': alt_shield(WHITE), 'alt/shield_grey.png': alt_shield(DIM)}
    for prefix, palette in sorted(PALETTES.items()):
        cb = '_cb' if prefix else ''
        out['alt/panel_atk_ext%s.png' % cb] = alt_panel('atk', palette)
        out['alt/panel_def_ext%s.png' % cb] = alt_panel('def', palette)
        out['alt/glow_atk%s.png' % cb] = glow('atk', palette, size=(ALT_W, ALT_H), radius=ALT_R)
        out['alt/glow_def%s.png' % cb] = glow('def', palette, size=(ALT_W, ALT_H), radius=ALT_R)
        out['alt/shield_warn%s.png' % cb] = alt_shield(palette['red'], warn=True)
        for state, color in sorted(palette.items()):
            out['alt/dot_fill_%s%s.png' % (prefix, state)] = alt_dot(color, True)
            out['alt/dot_ring_%s%s.png' % (prefix, state)] = alt_dot(color, False)
    return out


def icon_set():
    """{dateiname: bild} fuer alle Kombinationen."""
    out = {}
    combos = list(itertools.product((1, 0), repeat=3))
    attacks = [('ap', 'AP', False), ('he', 'HE', False), ('he_if', 'HE', True), ('sap', 'SAP', False)]
    for name, ammo, ifhe in attacks:
        out['atk_%s_grey.png' % name] = capsule('atk', None, AMPEL, ammo, ifhe)
        for prefix, palette in sorted(PALETTES.items()):
            for z in combos:
                out['atk_%s_%s%s.png' % (name, prefix, ''.join(map(str, z)))] = capsule('atk', z, palette, ammo, ifhe)
    for prefix, palette in sorted(PALETTES.items()):
        out['glow_atk%s.png' % ('_cb' if prefix else '')] = glow('atk', palette)
        out['glow_atk_if%s.png' % ('_cb' if prefix else '')] = glow('atk', palette, ifhe=True)
        out['glow_def%s.png' % ('_cb' if prefix else '')] = glow('def', palette)
    out['def_grey.png'] = capsule('def', None, AMPEL)
    for prefix, palette in sorted(PALETTES.items()):
        for z in combos:
            out['def_%s%s.png' % (prefix, ''.join(map(str, z)))] = capsule('def', z, palette)
    out.update(alt_set())
    return out


def main():
    os.makedirs(os.path.join(TARGET_DIR, 'alt'), exist_ok=True)
    icons = icon_set()
    for name, im in sorted(icons.items()):
        im.save(os.path.join(TARGET_DIR, name))
    print('%d Kapseln in %s' % (len(icons), TARGET_DIR))
    return 0


if __name__ == '__main__':
    sys.exit(main())
