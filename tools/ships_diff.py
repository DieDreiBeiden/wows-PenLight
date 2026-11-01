# -*- coding: utf-8 -*-
"""Vergleicht zwei Mod-Tabellen (ships.json) und schreibt eine Zusammenfassung in Markdown.

    python3 -I tools/ships_diff.py ALT.json NEU.json [--max-changed N]

Fuer den Workflow "Data update": zeigt, welche Schiffe neu sind, wegfallen oder andere Werte haben
(Klasse, Bug/Heck, Deck, Kaliber, Mitte, Luftschlag). Exit 0 auch bei Unterschieden; Exit 1 nur, wenn
eine Datei fehlt oder kein gueltiges JSON ist.
"""
import json
import sys

FIELDS = ('class', 'bow/stern', 'deck', 'calibre', 'midship', 'airstrike')


def load(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def _fmt(value):
    if value is None:
        return '-'
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def diff(old, new):
    """(added, removed, changed) mit changed = [(name, [(feld, alt, neu), ...])]."""
    a, b = old.get('ships', {}), new.get('ships', {})
    added = sorted(set(b) - set(a))
    removed = sorted(set(a) - set(b))
    changed = []
    for name in sorted(set(a) & set(b)):
        ra, rb = list(a[name]) + [None] * 6, list(b[name]) + [None] * 6
        fields = [(FIELDS[i], ra[i], rb[i]) for i in range(len(FIELDS)) if ra[i] != rb[i]]
        if fields:
            changed.append((name, fields))
    return added, removed, changed


def report(old, new, max_changed=60):
    added, removed, changed = diff(old, new)
    lines = ['## Ship data %s -> %s' % (old.get('gameVersion'), new.get('gameVersion')), '',
             '%d ships, %d new, %d removed, %d changed' % (len(new.get('ships', {})), len(added), len(removed),
                                                           len(changed)), '']
    if added:
        lines += ['**New:** ' + ', '.join(added), '']
    if removed:
        lines += ['**Removed:** ' + ', '.join(removed), '']
    if changed:
        lines += ['| Ship | Changes |', '|---|---|']
        for name, fields in changed[:max_changed]:
            lines.append('| %s | %s |' % (name, ', '.join('%s %s -> %s' % (f, _fmt(x), _fmt(y)) for f, x, y in fields)))
        if len(changed) > max_changed:
            lines.append('| ... | %d more |' % (len(changed) - max_changed))
        lines.append('')
    return '\n'.join(lines)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    max_changed = 60
    if '--max-changed' in argv:
        max_changed = int(argv[argv.index('--max-changed') + 1])
        args = [a for a in args if a != str(max_changed)]
    if len(args) != 2:
        sys.stderr.write(__doc__)
        return 2
    try:
        old, new = load(args[0]), load(args[1])
    except (IOError, OSError, ValueError) as e:
        sys.stderr.write('Fehler: %s\n' % e)
        return 1
    sys.stdout.write(report(old, new, max_changed) + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
