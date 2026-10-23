# -*- coding: utf-8 -*-
"""Release-Text aus docs/CHANGELOG.md und der Vorlage docs/RELEASE_NOTES.md.

    python3 -I tools/release_notes.py version mod/res_mods/ForgeBlueprints/PenLightContainer.xml
    python3 -I tools/release_notes.py notes VERSION VORHERIGER_TAG OWNER/REPO > notes.md
    python3 -I tools/release_notes.py finalize VERSION DATUM

Neue Eintraege kommen unter '## Unreleased'. 'notes' nimmt den Abschnitt '## VERSION', falls es ihn
schon gibt (Release wird ersetzt), sonst 'Unreleased'. 'finalize' macht nach dem Release aus
'Unreleased' den Abschnitt '## VERSION – DATUM' und legt ein leeres 'Unreleased' an.
Vorlage: {{VERSION}}, {{CHANGES}}, {{COMPARE}}.
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CHANGELOG = os.path.join(ROOT, 'docs', 'CHANGELOG.md')
TEMPLATE = os.path.join(ROOT, 'docs', 'RELEASE_NOTES.md')
UNRELEASED = 'Unreleased'


def container_version(xml):
    m = re.search(r'<mod\b[^>]*\bversion="([0-9]+\.[0-9]+\.[0-9]+)"', xml)
    if not m:
        raise ValueError('keine Version im ModForge-Manifest')
    return m.group(1)


def sections(changelog):
    """{name: inhalt} je '## '-Abschnitt; name = erstes Wort der Ueberschrift."""
    out, name = {}, None
    for line in changelog.splitlines():
        if line.startswith('## '):
            name = line[3:].split()[0]
            out[name] = []
        elif name is not None:
            out[name].append(line)
    return dict((k, _clean('\n'.join(v))) for k, v in out.items())


def _clean(text):
    return re.sub(r'<!--.*?-->', '', text, flags=re.S).strip()


def changes_for(changelog, version):
    found = sections(changelog)
    text = found.get(version) or found.get(UNRELEASED, '')
    if not text:
        raise ValueError('docs/CHANGELOG.md: keine Eintraege unter "## %s" oder "## %s"' % (UNRELEASED, version))
    return text


def build_notes(template, changelog, version, previous, repo):
    compare = ''
    if previous:
        compare = 'All changes since %s: [%s...v%s](https://github.com/%s/compare/%s...v%s)' % (
            previous, previous, version, repo, previous, version)
    notes = (template.replace('{{VERSION}}', version)
             .replace('{{CHANGES}}', changes_for(changelog, version))
             .replace('{{COMPARE}}', compare))
    if '{{' in notes:
        raise ValueError('unbekannter Platzhalter in docs/RELEASE_NOTES.md')
    return re.sub(r'\n{3,}', '\n\n', notes).strip() + '\n'


def finalize(changelog, version, date):
    """Unreleased -> VERSION; unveraendert, wenn es den Abschnitt schon gibt."""
    if version in sections(changelog):
        return changelog
    heading = '## %s\n' % UNRELEASED
    if heading not in changelog:
        raise ValueError('docs/CHANGELOG.md: Abschnitt "## %s" fehlt' % UNRELEASED)
    return changelog.replace(heading, '%s\n## %s – %s\n' % (heading, version, date), 1)


def _read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def main(argv):
    try:
        if argv[1:2] == ['version'] and len(argv) == 3:
            print(container_version(_read(argv[2])))
        elif argv[1:2] == ['notes'] and len(argv) == 5:
            sys.stdout.write(build_notes(_read(TEMPLATE), _read(CHANGELOG), argv[2], argv[3], argv[4]))
        elif argv[1:2] == ['finalize'] and len(argv) == 4:
            text = finalize(_read(CHANGELOG), argv[2], argv[3])
            with open(CHANGELOG, 'w', encoding='utf-8') as f:
                f.write(text)
        else:
            sys.stderr.write(__doc__)
            return 2
    except ValueError as e:
        sys.stderr.write('Fehler: %s\n' % e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
