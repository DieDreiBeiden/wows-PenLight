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


if __name__ == '__main__':
    unittest.main()
