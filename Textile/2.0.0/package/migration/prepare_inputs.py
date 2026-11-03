"""Preserve the accepted package and stage owner-designated CORE sources.

Run from any directory: python migration/prepare_inputs.py --core DIRECTORY
No runtime files, catalogue mappings, or upstream RDF are rewritten.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BASELINE = '1ca2aa89241785dedeab430247bc9947daf69881'
SOURCES = ('actor.owl', 'connector.owl', 'event.owl', 'mat.owl', 'p_dpp.owl',
           'soc.owl', 'LICENSE.md', 'README.md')


def blob(path):
    return subprocess.check_output(['git', 'show', f'{BASELINE}:{path}'], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_once(path, data):
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f'Refusing to replace different preserved bytes: {path.name}')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def prepare(core):
    manifest = blob('PUBLICATION_MANIFEST.txt').decode('utf8')
    paths = {line for line in manifest.splitlines()
             if line and not line.startswith(('#', '['))}
    # Preserve WIDOCO generation inputs as well as the published outputs.
    paths.update(subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', BASELINE, 'widoco'],
        cwd=ROOT, text=True).splitlines())
    contents = {path: blob(path) for path in sorted(paths)}
    for line in contents['SHA256SUMS'].decode('utf8').splitlines():
        expected, path = line.split('  ', 1)
        if digest(contents[path]) != expected:
            raise ValueError(f'Accepted baseline checksum mismatch: {path}')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', compression=zipfile.ZIP_STORED) as archive:
        for path, data in contents.items():
            info = zipfile.ZipInfo(path, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    historical = ROOT / 'migration/historical'
    name = f'textile-1.1.2-{BASELINE}.zip'
    write_once(historical / name, buffer.getvalue())
    inventory = {
        'baseline_commit': BASELINE,
        'archive': name,
        'archive_sha256': digest(buffer.getvalue()),
        'files': {path: digest(data) for path, data in contents.items()},
    }
    write_once(historical / 'inventory.json',
               (json.dumps(inventory, indent=2) + '\n').encode('utf8'))
    staged = ROOT / 'migration/core-sources'
    source_hashes = {}
    for name in SOURCES:
        data = (core / name).read_bytes()
        write_once(staged / name, data)
        source_hashes[name] = digest(data)
    write_once(staged / 'SHA256SUMS', ''.join(
        f'{value}  {name}\n' for name, value in sorted(source_hashes.items())).encode('utf8'))
    # Verify stored bytes independently of archive construction.
    with zipfile.ZipFile(historical / inventory['archive']) as archive:
        assert set(archive.namelist()) == set(contents)
        for path, expected in inventory['files'].items():
            assert digest(archive.read(path)) == expected, path
    print(json.dumps({'historical_files': len(contents),
                      'archive_sha256': inventory['archive_sha256'],
                      'core_sources': source_hashes,
                      'verification': 'passed'}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--core', required=True, type=Path)
    prepare(parser.parse_args().core)
