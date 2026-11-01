# -*- coding: utf-8 -*-
# Statische Pruefungen der Unbound-Dateien (Befunde aus dem Client, siehe docs/KONZEPT.md).
import glob
import os
import re
import unittest

UNBOUND = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'mod', 'res_mods', 'gui', 'unbound2', '**', '*.unbound'),
                    recursive=True)


def code(path):
    """Inhalt ohne Kommentarzeilen."""
    with open(path, encoding='utf-8') as f:
        return '\n'.join(l for l in f.read().splitlines() if not l.lstrip().startswith('#'))


# --- Gueltigkeit der Namen in Ausdruecken ---------------------------------------------------------
# Jedes '(def element' hat einen eigenen Namensraum: Parameter, (var ...), (event ...), Variablen aus
# Makros. Ein Name aus einem anderen Element ist dort unbekannt; der Client meldet das nicht im
# python.log, die Anzeige bleibt dann einfach leer (Befund 0.5.0: isAirstrike in PenLightRoot).
UNBOUND_KEYWORDS = {'true', 'false', 'null', 'in'}
UNBOUND_GLOBALS = {'CC', 'CameraMode', 'Easing', 'EventDirection', '$datahub', '$event', '$index',
                   'tr', 'subst', 'toUpper', 'toString', 'isNumber', 'LOCKABLE_WEAPONS'}
# Variablen, die Makros aus TTaroModUtils bzw. dem Client anlegen
UNBOUND_MACRO_VARS = {'STAGE_SIZE': {'stageWidth', 'stageHeight'},
                      'TT_DRAGGABLE_POSITION': {'__dragPos', 'dragX', 'dragY'}}
# Attribute mit festem Text statt Ausdruck
UNBOUND_LITERAL_ATTRS = ('action', '_tooltipAlign', 'watch')


def unbound_elements(text):
    """([(name, parameter, rumpf)] je '(def element', {Konstanten})."""
    out, consts = [], set()
    for part in re.split(r'\n(?=\(def )', '\n' + text):
        m = re.match(r'\s*\(def constant (\w+)', part)
        if m:
            consts.add(m.group(1))
        m = re.match(r'\s*\(def element (\w+)\(([^)]*)\)', part)
        if m:
            out.append((m.group(1), set(re.findall(r'(\w+)\s*:', m.group(2))), part[m.end():]))
    return out, consts


def unbound_defined(body, params):
    names = set(params)
    names |= set(re.findall(r'\(var (\w+)\s*:', body))
    names |= set(re.findall(r'\(event (\w+)\)', body))
    names |= set(re.findall(r'_varName="\'(\w+)\'"', body))
    for macro, created in UNBOUND_MACRO_VARS.items():
        if '(macro %s' % macro in body:
            names |= created
    return names


def unbound_expressions(body):
    for m in re.finditer(r'"([^"]*)"', body):
        before = body[max(0, m.start() - 40):m.start()]
        if re.search(r'\(\w+\s*=\s*$', before):              # Stil: (position = "absolute")
            continue
        if re.search(r'\b(%s)=\s*$' % '|'.join(UNBOUND_LITERAL_ATTRS), before):
            continue
        yield m.group(1)


def unbound_identifiers(expr):
    expr = re.sub(r"'[^']*'", "''", expr)
    expr = re.sub(r'(?<=[{,])\s*\w+\s*:', ' ', expr)         # Schluessel in Objekt-Literalen
    return re.findall(r'(?<![.\w$])(\$?[A-Za-z_]\w*)', expr)


def unbound_unknown_names(text):
    elems, consts = unbound_elements(text)
    out = []
    for name, params, body in elems:
        known = unbound_defined(body, params) | consts | UNBOUND_GLOBALS | UNBOUND_KEYWORDS
        for expr in unbound_expressions(body):
            out += ['%s: %s in "%s"' % (name, ident, expr[:60]) for ident in unbound_identifiers(expr)
                    if ident not in known]
    return out


class UnboundTest(unittest.TestCase):
    def test_files_found(self):
        self.assertTrue(UNBOUND)

    def test_no_vblock(self):
        # Unbound 2 zeichnet vblock nicht (Container samt Inhalt unsichtbar); block stapelt untereinander
        for path in UNBOUND:
            self.assertIsNone(re.search(r'\(vblock\b', code(path)), os.path.basename(path))

    def test_balanced_parentheses(self):
        for path in UNBOUND:
            depth, quoted = 0, False
            for ch in code(path):
                if ch == '"':
                    quoted = not quoted
                elif not quoted:
                    depth += (ch == '(') - (ch == ')')
                    self.assertGreaterEqual(depth, 0, os.path.basename(path))
            self.assertEqual(depth, 0, os.path.basename(path))


    def test_ammobar_images_complete(self):
        # Redesign Munitionsleiste: jede Kombination, die PenLight.unbound zusammensetzt, liegt als Bild vor
        import itertools
        folder = os.path.join(os.path.dirname(__file__), '..', 'mod', 'res_mods', 'PnFMods', 'PenLight', 'ammobar')
        names = {'slot_grey', 'seg_grey', 'cap_grey', 'stripe_grey', 'seg_air_grey', 'cap_air_grey'}
        for pal in ('', 'cb_'):
            for state in ('green', 'yellow', 'red'):
                names |= {'slot_%s%s' % (pal, state), 'stripe_%s%s' % (pal, state)}
                for bits in itertools.product('01', repeat=3):
                    names |= {'seg_%s%s_%s' % (pal, state, ''.join(bits)), 'cap_%s%s_%s' % (pal, state, ''.join(bits))}
            for state in ('green', 'red'):
                names |= {'slot_ext_%s%s' % (pal, state), 'glow_slot_%s%s' % (pal, state), 'glow_cap_%s%s' % (pal, state),
                          'seg_air_%s%s' % (pal, state), 'cap_air_%s%s' % (pal, state)}
        # Spiel-Symbole (Kopien aus den Spieldateien): Munition je Zustand und das Schild
        for ammo in ('ap', 'he', 'cs', 'airsupport_he'):
            names |= {'game/' + ammo, 'game/%s_inactive' % ammo}
        names.add('game/planes_ap_damage')
        missing = sorted(n for n in names if not os.path.exists(os.path.join(folder, n + '.png')))
        self.assertEqual(missing, [])

    def test_names_defined_in_element(self):
        for path in UNBOUND:
            self.assertEqual(unbound_unknown_names(code(path)), [], os.path.basename(path))

    def test_fixed_image_names_exist(self):
        # feste Bildnamen (ohne zusammengesetzte Teile) muessen im Mod-Ordner liegen
        mod_dir = os.path.join(os.path.dirname(__file__), '..', 'mod', 'res_mods', 'PnFMods', 'PenLight')
        for path in UNBOUND:
            text = code(path)
            names = re.findall(r"PENLIGHT_ICON_PATH \+ '([\w/]+\.png)'", text)
            names += re.findall(r"url:\.\./\.\./\.\./PnFMods/PenLight/([\w/]+\.png)", text)
            missing = sorted(n for n in set(names) if not os.path.exists(os.path.join(mod_dir, n)))
            self.assertTrue(names)
            self.assertEqual(missing, [], os.path.basename(path))

    def test_name_check_finds_foreign_variable(self):
        # Gegenprobe: Variable aus einem anderen Element (Fehler aus dem Luftschlag-Probe-Build)
        text = ('(def element A() layout=true\n\t(scope (var isAirstrike:bool = "true"))\n)\n'
                '(def element B() layout=true\n\t(bind visible "isAirstrike || other.x")\n)\n')
        self.assertEqual(unbound_unknown_names(text), ['B: isAirstrike in "isAirstrike || other.x"',
                                                       'B: other in "isAirstrike || other.x"'])

if __name__ == '__main__':
    unittest.main()
