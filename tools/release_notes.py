# -*- coding: utf-8 -*-
"""Version und Release-Text fuer den Release-Workflow.

    python3 -I tools/release_notes.py pick GEWUENSCHT REPLACE [TAG ...]   -> VERSION=… / PREVIOUS=…
    python3 -I tools/release_notes.py set-version MANIFEST VERSION
    python3 -I tools/release_notes.py set-readme VERSION PRERELEASE README.md [README.de.md ...]
    python3 -I tools/release_notes.py notes VERSION VORHERIGER_TAG OWNER/REPO > notes.md
    python3 -I tools/release_notes.py finalize VERSION DATUM

Version: GEWUENSCHT (z. B. 0.4.0) oder leer = naechste Patch-Version nach dem neuesten Tag; leer mit
REPLACE=true = neuester Tag (Release wird ersetzt). 'set-version' schreibt sie ins ModForge-Manifest,
damit die Mod immer die Release-Version meldet. 'set-readme' schreibt sie in die Zeile
'Current version' / 'Aktuelle Version' der READMEs (PRERELEASE true: mit Hinweis Vorabversion).
Release-Text: neue Eintraege kommen unter '## Unreleased' in docs/CHANGELOG.md. 'notes' nimmt den
Abschnitt '## VERSION', falls es ihn schon gibt (Release wird ersetzt), sonst 'Unreleased'.
'finalize' macht aus 'Unreleased' den Abschnitt '## VERSION – DATUM' und legt ein leeres
'Unreleased' an. Vorlage docs/RELEASE_NOTES.md: {{VERSION}}, {{CHANGES}}, {{COMPARE}}.
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CHANGELOG = os.path.join(ROOT, 'docs', 'CHANGELOG.md')
TEMPLATE = os.path.join(ROOT, 'docs', 'RELEASE_NOTES.md')
UNRELEASED = 'Unreleased'
_VERSION = re.compile(r'^v?([0-9]+)\.([0-9]+)\.([0-9]+)$')
_MANIFEST_VERSION = re.compile(r'(<mod\b[^>]*\bversion=")([0-9]+\.[0-9]+\.[0-9]+)(")')


def _parse(text):
    m = _VERSION.match(text.strip())
    return tuple(int(n) for n in m.groups()) if m else None


def _fmt(parts):
    return '%d.%d.%d' % parts


def pick_version(requested, replace, tags):
    """(version, vorheriger_tag) aus Wunschversion, Ersetzen-Schalter und vorhandenen Tags."""
    known = sorted(p for p in (_parse(t) for t in tags) if p)
    latest = known[-1] if known else None
    if requested.strip():
        version = _parse(requested)
        if not version or requested.strip().startswith('v'):
            raise ValueError('Version "%s" hat nicht die Form 1.2.3' % requested)
        if version in known and not replace:
            raise ValueError('Tag v%s existiert bereits ("replace" waehlen zum Ersetzen)' % _fmt(version))
        if version not in known and latest and version < latest:
            raise ValueError('Version %s ist kleiner als der neueste Release v%s' % (_fmt(version), _fmt(latest)))
    elif latest is None:
        raise ValueError('noch kein Release-Tag: Version angeben')
    elif replace:
        version = latest
    else:
        version = (latest[0], latest[1], latest[2] + 1)
    older = [p for p in known if p < version]
    return _fmt(version), ('v' + _fmt(older[-1]) if older else '')


def container_version(xml):
    m = _MANIFEST_VERSION.search(xml)
    if not m:
        raise ValueError('keine Version im ModForge-Manifest')
    return m.group(2)


def set_container_version(xml, version):
    container_version(xml)
    return _MANIFEST_VERSION.sub(lambda m: m.group(1) + version + m.group(3), xml, count=1)


README_VERSION = (
    (re.compile(r'\*\*Current version: [0-9]+\.[0-9]+\.[0-9]+\*\*(?: \(pre-release\))?'),
     '**Current version: %s**', ' (pre-release)'),
    (re.compile(r'\*\*Aktuelle Version: [0-9]+\.[0-9]+\.[0-9]+\*\*(?: \(Vorabversion\))?'),
     '**Aktuelle Version: %s**', ' (Vorabversion)'),
)


def set_readme_version(text, version, prerelease):
    """Versionszeile der README (englisch oder deutsch) setzen; ohne Zeile -> ValueError."""
    for pattern, label, pre in README_VERSION:
        if pattern.search(text):
            return pattern.sub(lambda m: label % version + (pre if prerelease else ''), text, count=1)
    raise ValueError('README ohne Versionszeile (Current version / Aktuelle Version)')


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


def _write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else ''
    try:
        if cmd == 'pick' and len(argv) >= 4:
            version, previous = pick_version(argv[2], argv[3] == 'true', argv[4:])
            print('VERSION=%s\nPREVIOUS=%s' % (version, previous))
        elif cmd == 'set-version' and len(argv) == 4:
            _write(argv[2], set_container_version(_read(argv[2]), argv[3]))
        elif cmd == 'set-readme' and len(argv) >= 5:
            for path in argv[4:]:
                _write(path, set_readme_version(_read(path), argv[2], argv[3] == 'true'))
        elif cmd == 'notes' and len(argv) == 5:
            sys.stdout.write(build_notes(_read(TEMPLATE), _read(CHANGELOG), argv[2], argv[3], argv[4]))
        elif cmd == 'finalize' and len(argv) == 4:
            _write(CHANGELOG, finalize(_read(CHANGELOG), argv[2], argv[3]))
        else:
            sys.stderr.write(__doc__)
            return 2
    except ValueError as e:
        sys.stderr.write('Fehler: %s\n' % e)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
