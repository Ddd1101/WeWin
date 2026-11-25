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


def restore(archive_path, destination):
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
    missing = [name for name in images if not (destination / 'media' / name).is_file()]
    result = {'batch': manifest['batch'], 'integrity': 'ok', 'foreign_keys': 'ok', 'tables': counts, 'image_references': len(images), 'missing_images': missing}
    (destination / 'restore-report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(restore(args.archive, args.destination), ensure_ascii=False))
