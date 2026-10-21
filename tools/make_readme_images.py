# -*- coding: utf-8 -*-
"""Erzeugt die Abbildungen der README (docs/images/), nur aus eigenen Grafiken.

    python3 -I tools/make_readme_images.py

- ampel.png:  Granate | Schild je Bedeutung (Spalten), Standard- und Farbenblind-Farben, mit Zeichen
- detail.png: Detailansicht wie im Spiel (Rahmen, farbige Mini-Icons, Schiffsname,
  Target oben, Me unten). Statt der Spiel-Silhouette steht das gezeichnete Schiff aus
  make_detail_icons, damit keine Spielgrafik ins Repository kommt.
Masse wie OVERMATCHER_SETTINGS in Overmatcher.unbound (silhouetteWidth/-Height, labelOverlap,
nameGap, nameBottom, shipGap, headLineAlpha). Erst make_ampel_icons und make_detail_icons laufen lassen.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ampel_icons as icons  # noqa: E402
import make_detail_icons as detail  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'docs', 'images')
ICONS = icons.TARGET_DIR
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BACKGROUND = (32, 36, 40, 255)
ZOOM = 2

SIL_W, SIL_H = 186, 48
LABEL_H, LABEL_OVERLAP = 24, 8
NAME_GAP, NAME_BOTTOM, SHIP_GAP, HEAD_LINE_ALPHA = 3, 4, 6, 0.55


def _icon(name):
    return Image.open(os.path.join(ICONS, name)).convert('RGBA')


def _with_mark(icon, mark):
    """Icon mit Zeichen rechts oben wie in Overmatcher.unbound (markOffset)."""
    pad = 8
    out = Image.new('RGBA', (icon.width + pad, icon.height + pad), (0, 0, 0, 0))
    out.alpha_composite(icon, (0, pad))
    if mark:
        m = _icon(mark)
        out.alpha_composite(m, (icon.width + pad - m.width, 0))
    return out


def ampel():
    """Spalten nach Bedeutung: Granate ich -> Ziel, Schild Ziel -> ich (Farbe = gut fuer mich)."""
    f = ImageFont.truetype(FONT, 13)
    fs = ImageFont.truetype(FONT_REGULAR, 12)
    rows = [('Standard', ''), ('Colour-blind', 'cb_')]
    columns = [('overmatch\neverywhere', 'green', 'red'), ('bow/stern\nonly', 'yellow', 'yellow'),
               ('no\novermatch', 'red', 'green'), ('no target /\nnot relevant', 'grey', 'grey')]
    cw = 130
    im = Image.new('RGBA', (140 + 4 * cw, 44 + 2 * 100), BACKGROUND)
    d = ImageDraw.Draw(im)
    for i, (label, _, _) in enumerate(columns):
        d.multiline_text((140 + i * cw, 6), label, font=fs, fill=(220, 222, 224), spacing=1)
    for r, (name, prefix) in enumerate(rows):
        y = 44 + r * 100
        d.text((14, y + 30), name, font=f, fill=(236, 238, 240))
        for i, (_, shell_state, shield_state) in enumerate(columns):
            shell = _with_mark(_icon('shell_%s%s.png' % (prefix, shell_state)),
                               'mark_star.png' if shell_state == 'green' else None)
            shield = _with_mark(_icon('shield_%s%s.png' % (prefix, shield_state)),
                                'mark_warning.png' if shield_state == 'red' else None)
            for j, icon in enumerate((shell, shield)):
                big = icon.resize((icon.width * ZOOM, icon.height * ZOOM), Image.LANCZOS)
                im.alpha_composite(big, (140 + i * cw + j * 60, y))
    d.text((14, 44 + 2 * 100 - 16), 'left: my shell vs target  -  right: target vs my shield',
           font=fs, fill=(170, 172, 174))
    im.save(os.path.join(OUT, 'ampel.png'))


def _silhouette(combo):
    """Gezeichnetes Schiff, auf die Silhouettenflaeche 186 x 48 zugeschnitten (unten buendig)."""
    ship = detail._ship(*(detail.COLORS[c] for c in combo)).reduce(detail.SUPERSAMPLE)
    ship = ship.crop(ship.getchannel('A').getbbox())
    scale = min(SIL_W * 0.92 / ship.width, SIL_H * 0.92 / ship.height)
    ship = ship.resize((int(ship.width * scale), int(ship.height * scale)), Image.LANCZOS)
    area = Image.new('RGBA', (SIL_W, SIL_H), (0, 0, 0, 0))
    area.alpha_composite(ship, ((SIL_W - ship.width) // 2, SIL_H - ship.height))
    return area


def _name(text):
    f = ImageFont.truetype(FONT, 13)
    im = Image.new('RGBA', (SIL_W, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = (SIL_W - d.textlength(text, font=f)) // 2
    d.text((x + 1, 1), text, font=f, fill=(0, 0, 0, 170))
    d.text((x, 0), text, font=f, fill=(236, 238, 240, 255))
    return im


def _ship_block(key, state, combo, name):
    """Ein Schiff wie OvermatcherSilhouetteShip: Rahmen, Beschriftung, Silhouette, Name."""
    top = LABEL_H - LABEL_OVERLAP
    h = top + SIL_H + NAME_GAP + 16 + NAME_BOTTOM
    im = Image.new('RGBA', (SIL_W, h), (0, 0, 0, 0))
    im.alpha_composite(_icon('frame_band.png').resize((SIL_W, h)))
    im.alpha_composite(_icon('frame_head.png').resize((SIL_W, LABEL_H - 2)), (0, 1))
    line = _icon('frame_line.png')
    head_line = line.copy()
    head_line.putalpha(head_line.getchannel('A').point(lambda v: int(v * HEAD_LINE_ALPHA)))
    im.alpha_composite(head_line, (0, LABEL_H - 1))
    im.alpha_composite(line, (0, 0))
    im.alpha_composite(line, (0, h - 1))
    im.alpha_composite(_silhouette(combo), (0, top))
    im.alpha_composite(_icon('label_%s_%s.png' % (key, state)), (0, 0))
    im.alpha_composite(_name(name), (0, top + SIL_H + NAME_GAP))
    return im


def detail_view():
    target = _ship_block('target', 'yellow', ('g', 'r', 'r'), 'TARGET SHIP')
    me = _ship_block('me', 'green', ('g', 'g', 'g'), 'YOUR SHIP')
    im = Image.new('RGBA', (SIL_W + 24, target.height + SHIP_GAP + me.height + 24), BACKGROUND)
    im.alpha_composite(target, (12, 12))
    im.alpha_composite(me, (12, 12 + target.height + SHIP_GAP))
    im.resize((im.width * ZOOM, im.height * ZOOM), Image.LANCZOS).save(os.path.join(OUT, 'detail.png'))


def main():
    os.makedirs(OUT, exist_ok=True)
    ampel()
    detail_view()
    print('docs/images/ampel.png, docs/images/detail.png')
    return 0


if __name__ == '__main__':
    sys.exit(main())
