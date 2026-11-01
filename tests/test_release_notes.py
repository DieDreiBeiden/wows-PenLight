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

    def test_readme_version(self):
        en = '> **Current version: 0.4.0** (pre-release) - [download](x).'
        self.assertEqual(rn.set_readme_version(en, '0.4.1', False), '> **Current version: 0.4.1** - [download](x).')
        de = '> **Aktuelle Version: 0.4.0** - x'
        self.assertEqual(rn.set_readme_version(de, '1.0.0', True), '> **Aktuelle Version: 1.0.0** (Vorabversion) - x')
        with self.assertRaises(ValueError):
            rn.set_readme_version('no version line', '0.4.1', False)
        for name in ('README.md', 'README.de.md'):
            with open(os.path.join(rn.ROOT, name), encoding='utf-8') as f:
                rn.set_readme_version(f.read(), '9.9.9', True)

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
        self.assertIn('PenLight-%s.zip' % version, notes)

    def test_game_version_from_ships(self):
        self.assertEqual(rn.game_version('{"gameVersion": "15,9,0,13357625", "ships": {}}'), '15.9.0.13357625')
        with self.assertRaises(ValueError):
            rn.game_version('{"gameVersion": "15.9"}')
        notes = rn.build_notes(TEMPLATE + '{{GAME_VERSION}}', CHANGELOG, '0.3.2', 'v0.3.1', 'o/r', '15.9.0.1')
        self.assertIn('15.9.0.1', notes)

    def test_add_change(self):
        out = rn.add_change(CHANGELOG, 'Ship data updated  for 15.10.')
        self.assertIn('- Fixed: deck\n- Ship data updated for 15.10.\n\n## 0.3.1', out)
        empty = rn.add_change('## Unreleased\n\n## 0.3.1\n', 'x')
        self.assertEqual(empty, '## Unreleased\n\n- x\n\n## 0.3.1\n')
        with self.assertRaises(ValueError):
            rn.add_change('## 0.3.1\n', 'x')


class ShipsDiffTest(unittest.TestCase):
    def test_report(self):
        import ships_diff
        old = {'gameVersion': '1,0,0,1', 'ships': {'A': ['Cruiser', 25.0, 30.0, 152.0, 25.0, None],
                                                    'B': ['Destroyer', 19.0, 19.0, 127.0, 19.0, None]}}
        new = {'gameVersion': '1,0,0,2', 'ships': {'A': ['Cruiser', 25.0, 32.0, 152.0, 25.0, 36.9],
                                                    'C': ['Battleship', 32.0, 57.0, 460.0, 32.0, None]}}
        self.assertEqual(ships_diff.diff(old, new)[:2], (['C'], ['B']))
        text = ships_diff.report(old, new)
        self.assertIn('2 ships, 1 new, 1 removed, 1 changed', text)
        self.assertIn('| A | deck 30 -> 32, airstrike - -> 36.9 |', text)


if __name__ == '__main__':
    unittest.main()
