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

if __name__ == '__main__':
    unittest.main()
