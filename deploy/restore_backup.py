#!/usr/bin/env python3
"""Restore only into a new directory, verify every file, then check SQLite."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tarfile
from backup import verify_archive


def restore(archive_path, destination, media_root=None):
    manifest = verify_archive(archive_path)
    destination.mkdir(parents=True, exist_ok=False)
    # verify_archive has rejected absolute paths, traversal, links and duplicates.
    with tarfile.open(archive_path, 'r:gz') as archive:
        for member in archive.getmembers():
            target = destination / member.name
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, 'wb') as out:
                shutil.copyfileobj(archive.extractfile(member), out)
    with sqlite3.connect('file:' + str(destination / 'db.sqlite3') + '?mode=ro', uri=True) as db:
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
        assert not db.execute('PRAGMA foreign_key_check').fetchall()
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        counts = {table: db.execute('SELECT COUNT(*) FROM "' + table.replace('"', '""') + '"').fetchone()[0] for table in tables}
        images = [row[0] for row in db.execute("SELECT image FROM product WHERE image IS NOT NULL AND image != ''")]
    external = (destination / 'media-manifest.json').exists()
    source_media = media_root if media_root else destination / 'media'
    missing = [name for name in images if not (source_media / name).is_file()]
    if external and not media_root:
        inventory = json.loads((destination / 'media-manifest.json').read_text())
        missing = inventory['missing']
    verified = not external or media_root is not None
    if external and media_root:
        import hashlib
        for item in json.loads((destination / 'media-manifest.json').read_text())['files']:
            path = media_root / item['name']
            if not path.is_file():
                candidates = []
                for metadata in (media_root / '.trash').glob('*/metadata.json'):
                    record = json.loads(metadata.read_text())
                    if record.get('name') == item['name']:
                        candidates.append(metadata.parent / 'image')
                matching = [candidate for candidate in candidates if candidate.is_file()]
                if not matching:
                    raise FileNotFoundError(item['name'])
                path = matching[-1]
            with open(path, 'rb') as f:
                h = hashlib.sha256()
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(chunk)
            if h.hexdigest() != item['sha256']:
                raise ValueError('External media checksum mismatch')
            recovered = destination / 'media' / item['name']
            recovered.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, recovered)
        missing = [name for name in images if not (destination / 'media' / name).is_file()]
    result = {'batch': manifest['batch'], 'integrity': 'ok', 'foreign_keys': 'ok', 'tables': counts, 'image_references': len(images), 'missing_images': missing, 'media_verified': verified, 'media_external': external}
    (destination / 'restore-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--media-root', type=Path, help='Required to verify external N1 originals against the manifest')
    args = parser.parse_args()
    print(json.dumps(restore(args.archive, args.destination, args.media_root), ensure_ascii=False))
