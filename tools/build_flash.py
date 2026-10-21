# -*- coding: utf-8 -*-
"""Baut den Flash-Teil (Main.swf) der Standalone-Fassung.

    FLEX_HOME=/pfad/apache-flex-sdk-4.16.1-bin WOWS_SWC=/pfad/wows_library.swc \
        python3 -I tools/build_flash.py

Benoetigt:
- Apache Flex SDK 4.16.1 (archive.apache.org/dist/flex/4.16.1/binaries/) mit
  frameworks/libs/player/32.0/playerglobal.swc (Adobe, playerglobal32_0.swc) und Java
- wows_library.swc aus dem offiziellen ModSDK (as3_library/), nur zum Kompilieren gegen
  lesta.api.ModBase; die Klassen liefert der Client, sie werden nicht eingebunden
Quelle: src/as3/Main.as (nicht src/flash: das wuerde in den Tests das Modul 'flash' verdecken).
Ausgabe: mod/res_mods/PnFMods/Overmatcher/Main.swf
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, 'src', 'as3', 'Main.as')
TARGET = os.path.join(ROOT, 'mod', 'res_mods', 'PnFMods', 'Overmatcher', 'Main.swf')


def main():
    flex = os.environ.get('FLEX_HOME')
    swc = os.environ.get('WOWS_SWC')
    if not flex or not swc:
        sys.stderr.write(__doc__)
        return 2
    cmd = [
        os.path.join(flex, 'bin', 'mxmlc'),
        '-target-player=32.0',
        # SWF-Version wie die Spieldateien (swf_external im ModSDK: 12-15, Scaleform)
        '-swf-version=13',
        '-static-link-runtime-shared-libraries=true',
        # ModBase & Co. stellt der Client bereit -> nur zum Pruefen, nicht einbinden
        '-external-library-path+=' + swc,
        '-default-size=1,1',
        '-optimize=true',
        '-output=' + TARGET,
        SOURCE,
    ]
    env = dict(os.environ)
    env.setdefault('PLAYERGLOBAL_HOME', os.path.join(flex, 'frameworks', 'libs', 'player'))
    result = subprocess.call(cmd, env=env)
    if result == 0:
        print('%s (%d Bytes)' % (TARGET, os.path.getsize(TARGET)))
    return result


if __name__ == '__main__':
    sys.exit(main())
