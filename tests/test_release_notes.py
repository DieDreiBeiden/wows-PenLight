# -*- coding: utf-8 -*-
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

import release_notes as rn

CHANGELOG = """# Changelog

## Unreleased

<!-- neue Eintraege hier -->
- Fixed: deck

## 0.3.1 – 2026-10-21

- Aiming view only
"""
TEMPLATE = "## What's new in {{VERSION}}\n\n{{CHANGES}}\n\n- `PenLight-{{VERSION}}-ttaro.zip`\n\n{{COMPARE}}\n\nEnd\n"


class ReleaseNotesTest(unittest.TestCase):
    def test_notes_from_unreleased(self):
        notes = rn.build_notes(TEMPLATE, CHANGELOG, '0.3.2', 'v0.3.1', 'o/r')
        self.assertIn("What's new in 0.3.2\n\n- Fixed: deck\n", notes)
        self.assertIn('PenLight-0.3.2-ttaro.zip', notes)
        self.assertIn('https://github.com/o/r/compare/v0.3.1...v0.3.2', notes)
        self.assertNotIn('Aiming view', notes)
        self.assertNotIn('<!--', notes)

    def test_notes_existing_version_and_no_previous(self):
        notes = rn.build_notes(TEMPLATE, CHANGELOG, '0.3.1', '', 'o/r')
        self.assertIn('- Aiming view only', notes)
        self.assertNotIn('compare', notes)
        self.assertNotIn('\n\n\n', notes)

    def test_empty_unreleased_fails(self):
        empty = CHANGELOG.replace('- Fixed: deck\n', '')
        with self.assertRaises(ValueError):
            rn.build_notes(TEMPLATE, empty, '0.3.2', 'v0.3.1', 'o/r')

    def test_unknown_placeholder_fails(self):
        with self.assertRaises(ValueError):
            rn.build_notes(TEMPLATE + '{{DATE}}', CHANGELOG, '0.3.2', 'v0.3.1', 'o/r')

    def test_finalize(self):
        done = rn.finalize(CHANGELOG, '0.3.2', '2026-10-24')
        found = rn.sections(done)
        self.assertEqual(found['Unreleased'], '')
        self.assertEqual(found['0.3.2'], '- Fixed: deck')
        self.assertLess(done.index('## Unreleased'), done.index('## 0.3.2 – 2026-10-24'))
        self.assertEqual(rn.finalize(done, '0.3.2', '2026-10-25'), done)

    def test_container_version(self):
        xml = '<mod name="PenLightContainer" version="0.3.2" priority="0">\n  <requires installer="&gt;=1.0.0"/>'
        self.assertEqual(rn.container_version(xml), '0.3.2')
        done = rn.set_container_version(xml, '0.4.0')
        self.assertEqual(rn.container_version(done), '0.4.0')
        self.assertIn('installer="&gt;=1.0.0"', done)

    def test_pick_version(self):
        tags = ['v0.3.0', 'v0.3.1', 'v0.3.2', 'test-x']
        self.assertEqual(rn.pick_version('', False, tags), ('0.3.3', 'v0.3.2'))     # naechster Patch
        self.assertEqual(rn.pick_version('', True, tags), ('0.3.2', 'v0.3.1'))      # neuesten ersetzen
        self.assertEqual(rn.pick_version('0.4.0', False, tags), ('0.4.0', 'v0.3.2'))
        self.assertEqual(rn.pick_version('0.3.1', True, tags), ('0.3.1', 'v0.3.0'))
        self.assertEqual(rn.pick_version('0.1.0', False, []), ('0.1.0', ''))
        for requested, replace, known in (('0.3.2', False, tags), ('0.3.0.1', False, tags), ('v0.4.0', False, tags),
                                          ('0.2.9', False, tags), ('', False, [])):
            with self.assertRaises(ValueError):
                rn.pick_version(requested, replace, known)

    def test_repo_files(self):
        # echte Vorlage und Changelog passen zusammen
        with open(rn.TEMPLATE, encoding='utf-8') as f:
            template = f.read()
        with open(rn.CHANGELOG, encoding='utf-8') as f:
            changelog = f.read()
        with open(os.path.join(rn.ROOT, 'mod', 'res_mods', 'ForgeBlueprints', 'PenLightContainer.xml')) as f:
            version = rn.container_version(f.read())
        notes = rn.build_notes(template, changelog, version, 'v0.0.0', 'o/r')
        self.assertIn('PenLight-%s-standalone.zip' % version, notes)


if __name__ == '__main__':
    unittest.main()
