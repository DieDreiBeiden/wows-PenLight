# -*- coding: utf-8 -*-
"""Erzeugt die Abbildungen der README (docs/images/).

    python3 -I tools/make_readme_images.py

- ampel.png:  Slot-Paar (Munition | Schild) je Bedeutung (Spalten), Standard- und Farbenblind-Farben
- ammo.png:   Slot je Munition (AP / HE / HE + IFHE / SAP / Luftschlag), je Zustand (Spalten)
- styles.png: zwei Lagen in den Darstellungen Klassisch, Modern und Nur Text
  (Munitionsleisten-Design seit 0.5.0; Spiel-Symbole aus ammobar/game/)
- detail.png: Detailansicht wie im Spiel (Rahmen, farbige Mini-Icons, Schiffsname,
  Target oben, Me unten). Statt der Spiel-Silhouette steht das gezeichnete Schiff aus
  make_detail_icons, damit keine Spielgrafik ins Repository kommt.
Masse wie PENLIGHT_SETTINGS in PenLight.unbound (silhouetteWidth/-Height, labelOverlap,
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


# Munitionsleisten-Design (seit 0.5.0): Teile aus make_ammobar_icons, Symbole aus ammobar/game/ (Kopien aus
# den Spieldateien, Wargaming). Masse wie PENLIGHT_SETTINGS (ammoBarSlot 46, ammoBarIcon 40, SegGap 3,
# SegHeight 7, Gap 6, CapWidth 72, CapHeight 22, CapIcon 22, capsuleGap 4, TextIcon 17, glowPad 5,
# glowRestAlpha 0.45 = Ruhezustand nach dem Pulsieren).
AMMOBAR = os.path.join(ICONS, 'ammobar')
GAME = os.path.join(AMMOBAR, 'game')
SLOT, SLOT_ICON, SEG_GAP, SEG_H, GAP = 46, 40, 3, 7, 6
CAP_W, CAP_H, CAP_ICON, CAP_GAP, TEXT_ICON, GLOW_PAD, GLOW_REST = 72, 22, 22, 4, 17, 5, 0.45
# Nur Text: Unterlage 0xD90E1012, Textfarben wie PENLIGHT_TEXT_CT bzw. _CB
TEXT_PLATE = (14, 16, 18, 217)
TEXT_COLORS = {'': {'green': (61, 220, 90), 'yellow': (255, 140, 0), 'red': (255, 112, 96), 'grey': (176, 181, 186)},
               'cb_': {'green': (88, 170, 255), 'yellow': (240, 228, 66), 'red': (245, 128, 40),
                       'grey': (176, 181, 186)}}
SHIELD = 'planes_ap_damage'
DIM = (0.38, 0.4, 0.42)   # PENLIGHT_ICON_CT_DIM


def _part(name):
    return Image.open(os.path.join(AMMOBAR, name + '.png')).convert('RGBA')


def _game(name, size, dim=False):
    im = Image.open(os.path.join(GAME, name + '.png')).convert('RGBA').resize((size, size), Image.LANCZOS)
    if dim:
        r, g, b, a = im.split()
        im = Image.merge('RGBA', [c.point(lambda v, k=k: int(v * k)) for c, k in zip((r, g, b), DIM)] + [a])
    return im


def _glow(name):
    g = _part(name)
    g.putalpha(g.getchannel('A').point(lambda v: int(v * GLOW_REST)))
    return g


def _state(kind, bits, rated=True, airstrike=False):
    """Zustand wie attackState/defenseState in PenLight.unbound."""
    if not rated:
        return 'grey'
    if airstrike:
        return 'green' if bits[2] == '1' else 'red'
    good, bad = ('green', 'red') if kind == 'atk' else ('red', 'green')
    return good if bits == '111' else (bad if bits == '000' else 'yellow')


def _frame_names(kind, bits, pal, rated, airstrike=False):
    st = _state(kind, bits, rated, airstrike)
    ext = rated and (bits[2] == '1' if airstrike else bits == '111')
    air = 'air_' if airstrike else ''
    if not rated:
        return 'slot_grey', 'seg_%sgrey' % air, 'cap_%sgrey' % air, 'stripe_grey', None, None, st
    glow = ('green' if kind == 'atk' else 'red') if ext else None
    suffix = '' if airstrike else '_' + bits
    return ('slot_%s%s%s' % ('ext_' if ext else '', pal, st), 'seg_%s%s%s%s' % (air, pal, st, suffix),
            'cap_%s%s%s%s' % (air, pal, st, suffix), 'stripe_%s%s' % (pal, st),
            'glow_slot_%s%s' % (pal, glow) if glow else None, 'glow_cap_%s%s' % (pal, glow) if glow else None, st)


def ab_slot(kind, icon, bits, pal='', rated=True, airstrike=False, ifhe=False):
    """Klassisch: Slot mit Spiel-Symbol, darunter drei Zonen-Balken (PenLightAmmoSlot)."""
    slot, seg, _, _, glow, _, _ = _frame_names(kind, bits, pal, rated, airstrike)
    p = GLOW_PAD
    im = Image.new('RGBA', (SLOT + 2 * p, SLOT + SEG_GAP + SEG_H + 2 * p), (0, 0, 0, 0))
    if glow:
        im.alpha_composite(_glow(glow), (0, 0))
    im.alpha_composite(_part(slot), (p, p))
    o = (SLOT - SLOT_ICON) // 2
    im.alpha_composite(_game(icon, SLOT_ICON, kind == 'def' and not rated), (p + o, p + o))
    if ifhe:
        im.alpha_composite(_icon('tag_ifhe.png'), (p + 2, p + SLOT - 12))
    im.alpha_composite(_part(seg), (p, p + SLOT + SEG_GAP))
    return im


def ab_capsule(kind, icon, bits, pal='', rated=True, airstrike=False, ifhe=False):
    """Modern: Kapsel mit Symbol links und drei Punkten (PenLightAmmoCapsule)."""
    _, _, cap, _, _, glow, _ = _frame_names(kind, bits, pal, rated, airstrike)
    p = GLOW_PAD
    im = Image.new('RGBA', (CAP_W + 2 * p, CAP_H + 2 * p), (0, 0, 0, 0))
    if glow:
        im.alpha_composite(_glow(glow), (0, 0))
    im.alpha_composite(_part(cap), (p, p))
    im.alpha_composite(_game(icon, CAP_ICON, kind == 'def' and not rated), (p + 2, p))
    if ifhe:
        im.alpha_composite(_icon('tag_ifhe.png'), (p + 1, p + CAP_H - 9))
    return im


def ab_text(kind, icon, bits, text, pal='', rated=True, airstrike=False):
    """Nur Text: Unterlage, Farbstreifen, kleines Symbol, Text (PenLightAmmoTextLine)."""
    _, _, _, stripe, _, _, st = _frame_names(kind, bits, pal, rated, airstrike)
    f = ImageFont.truetype(FONT, 12)
    w = int(ImageDraw.Draw(Image.new('RGBA', (1, 1))).textlength(text, font=f))
    im = Image.new('RGBA', (3 + 3 + TEXT_ICON + 4 + w + 5, 19), TEXT_PLATE)
    im.alpha_composite(_part(stripe), (0, 0))
    im.alpha_composite(_game(icon, TEXT_ICON, kind == 'def' and not rated), (6, 1))
    ImageDraw.Draw(im).text((6 + TEXT_ICON + 4, 1), text, font=f, fill=TEXT_COLORS[pal][st])
    return im


def _pair(a, b, vertical=False, gap=0):
    if vertical:
        out = Image.new('RGBA', (max(a.width, b.width), a.height + b.height + gap), (0, 0, 0, 0))
        out.alpha_composite(a, (0, 0))
        out.alpha_composite(b, (0, a.height + gap))
    else:
        out = Image.new('RGBA', (a.width + b.width + gap, max(a.height, b.height)), (0, 0, 0, 0))
        out.alpha_composite(a, (0, 0))
        out.alpha_composite(b, (a.width + gap, 0))
    return out


def _zoom(im):
    return im.resize((im.width * ZOOM, im.height * ZOOM), Image.LANCZOS)


def ampel():
    """Spalten nach Bedeutung: links mein Schuss -> Ziel, rechts AP des Ziels -> ich (Farbe = gut fuer mich)."""
    f = ImageFont.truetype(FONT, 13)
    fs = ImageFont.truetype(FONT_REGULAR, 12)
    rows = [('Standard', ''), ('Colour-blind', 'cb_')]
    columns = [('overmatch\neverywhere', '111', True), ('bow/stern\nonly', '100', True),
               ('no\novermatch', '000', True), ('no target /\nnot rated', '000', False)]
    cw, rh, x0 = 250, 150, 140
    im = Image.new('RGBA', (x0 + len(columns) * cw, 44 + len(rows) * rh + 20), BACKGROUND)
    d = ImageDraw.Draw(im)
    for i, (label, _, _) in enumerate(columns):
        d.multiline_text((x0 + i * cw, 6), label, font=fs, fill=(220, 222, 224), spacing=1)
    for r, (name, pal) in enumerate(rows):
        y = 44 + r * rh
        d.text((14, y + 50), name, font=f, fill=(236, 238, 240))
        for i, (_, bits, rated) in enumerate(columns):
            pair = _pair(ab_slot('atk', 'ap' if rated else 'ap_inactive', bits, pal, rated),
                         ab_slot('def', SHIELD, bits, pal, rated), gap=GAP - 2 * GLOW_PAD)
            im.alpha_composite(_zoom(pair), (x0 + i * cw, y))
    d.text((14, im.height - 22), 'left: my shell vs target  -  right (shield): target\'s AP vs me  -  '
           'bars: bow | upper deck, lower midship | stern', font=fs, fill=(170, 172, 174))
    im.save(os.path.join(OUT, 'ampel.png'))


def ammo():
    """Zeilen je Munition, Spalten je Zustand; AP kennt kein 'nur Deck', der Luftschlag nur das Deck."""
    f = ImageFont.truetype(FONT, 13)
    fs = ImageFont.truetype(FONT_REGULAR, 12)
    columns = [('everywhere', '111'), ('bow/stern\n+ midship', '110'), ('bow/stern', '100'),
               ('deck\n(airstrike)', '001'), ('nowhere', '000'), ('no target /\nnot rated', None)]
    common = ('111', '110', '100', '000')
    rows = [('AP', 'ap', common), ('HE', 'he', common), ('HE + IFHE', 'he', common), ('SAP', 'cs', common),
            ('Airstrike', 'airsupport_he', ('001', '000'))]
    cw, rh, x0 = 124, 134, 120
    im = Image.new('RGBA', (x0 + len(columns) * cw, 44 + len(rows) * rh + 24), BACKGROUND)
    d = ImageDraw.Draw(im)
    for i, (label, _) in enumerate(columns):
        d.multiline_text((x0 + i * cw, 6), label, font=fs, fill=(220, 222, 224), spacing=1)
    for r, (name, icon, allowed) in enumerate(rows):
        y = 44 + r * rh
        d.text((14, y + 50), name, font=f, fill=(236, 238, 240))
        for i, (_, bits) in enumerate(columns):
            if bits is None:
                slot = ab_slot('atk', icon + '_inactive', '000', rated=False, airstrike=icon == 'airsupport_he')
            elif bits not in allowed:
                continue
            else:
                slot = ab_slot('atk', icon, bits, airstrike=icon == 'airsupport_he', ifhe=name.endswith('IFHE'))
            im.alpha_composite(_zoom(slot), (x0 + i * cw, y))
    d.text((14, im.height - 22), 'bars: bow | upper deck, lower midship | stern  -  HE/SAP: penetration >= plate, '
           'HE incl. IFHE  -  airstrike: deck only', font=fs, fill=(170, 172, 174))
    im.save(os.path.join(OUT, 'ammo.png'))


def styles():
    """Zwei Lagen, drei Darstellungen."""
    fs = ImageFont.truetype(FONT_REGULAR, 12)
    f = ImageFont.truetype(FONT, 13)
    scenes = [
        ('HE gets through bow/stern only,\ntarget\'s AP overmatches me everywhere',
         ('he', '100', False), ('111',), 'HE: Bow/Stern', 'Enemy AP: everywhere'),
        ('Airstrike selected: bombs get through\nthe deck, target\'s AP bow/stern only',
         ('airsupport_he', '001', True), ('100',), 'Airstrike: Deck', 'Enemy AP: Bow/Stern'),
    ]
    columns = ['Classic', 'Modern (default)', 'Text only']
    cw, rh, x0 = 260, 150, 290
    im = Image.new('RGBA', (x0 + (len(columns) - 1) * cw + 2 * 210, 40 + len(scenes) * rh), BACKGROUND)
    d = ImageDraw.Draw(im)
    for i, label in enumerate(columns):
        d.text((x0 + i * cw, 10), label, font=f, fill=(236, 238, 240))
    for r, (title, (icon, abits, air), (dbits,), t_atk, t_def) in enumerate(scenes):
        y = 40 + r * rh
        d.multiline_text((14, y + 40), title, font=fs, fill=(220, 222, 224), spacing=3)
        classic = _pair(ab_slot('atk', icon, abits, airstrike=air), ab_slot('def', SHIELD, dbits),
                        gap=GAP - 2 * GLOW_PAD)
        modern = _pair(ab_capsule('atk', icon, abits, airstrike=air), ab_capsule('def', SHIELD, dbits),
                       vertical=True, gap=CAP_GAP - 2 * GLOW_PAD)
        text = _pair(ab_text('atk', icon, abits, t_atk, airstrike=air), ab_text('def', SHIELD, dbits, t_def),
                     vertical=True, gap=2)
        for i, part in enumerate((classic, modern, text)):
            im.alpha_composite(_zoom(part), (x0 + i * cw, y))
    im.save(os.path.join(OUT, 'styles.png'))


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
    """Ein Schiff wie PenLightSilhouetteShip: Rahmen, Beschriftung, Silhouette, Name."""
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
    ammo()
    styles()
    detail_view()
    print('docs/images/ampel.png, docs/images/ammo.png, docs/images/styles.png, docs/images/detail.png')
    return 0


if __name__ == '__main__':
    sys.exit(main())
