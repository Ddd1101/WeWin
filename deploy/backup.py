#!/usr/bin/env python3
"""Create a consistent SQLite/media batch while holding the app write barrier."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tarfile
import tempfile
from datetime import datetime, timezone


def digest(path):
    value = hashlib.sha256()
    with open(path, 'rb') as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def verify_archive(path):
    with tarfile.open(path, 'r:gz') as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive paths')
        for member in members:
            p = Path(member.name)
            if p.is_absolute() or '..' in p.parts or not member.isfile():
                raise ValueError('Unsafe archive entry')
        manifest = json.load(archive.extractfile('manifest.json'))
        if set(names) != set(manifest['files']) | {'manifest.json'}:
            raise ValueError('Manifest does not match archive')
        for name, expected in manifest['files'].items():
            h = hashlib.sha256()
            stream = archive.extractfile(name)
            for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                h.update(chunk)
            if h.hexdigest() != expected:
                raise ValueError('Checksum mismatch: ' + name)
    return manifest


def create_batch(database, media, output, lock_path, status_path=None):
    output.mkdir(parents=True, exist_ok=True)
    batch = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    with tempfile.TemporaryDirectory(dir=output, prefix='.staging-') as staging:
        stage = Path(staging)
        with open(lock_path, 'a') as lock:
            # New application writes fail fast; in-flight writes finish first.
            fcntl.flock(lock, fcntl.LOCK_EX)
            with sqlite3.connect('file:' + str(database) + '?mode=ro', uri=True) as source:
                with sqlite3.connect(str(stage / 'db.sqlite3')) as target:
                    source.backup(target)
                    if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                        raise ValueError('Database integrity check failed')
                    if target.execute('PRAGMA foreign_key_check').fetchall():
                        raise ValueError('Database foreign key check failed')
            shutil.copytree(media, stage / 'media')
            fcntl.flock(lock, fcntl.LOCK_UN)
        files = {str(p.relative_to(stage)): digest(p) for p in sorted(stage.rglob('*')) if p.is_file()}
        manifest = {'batch': batch, 'created_at': datetime.now(timezone.utc).isoformat(), 'files': files}
        (stage / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        temporary = output / ('.' + batch + '.part')
        with tarfile.open(temporary, 'w:gz') as archive:
            for p in sorted(stage.rglob('*')):
                if p.is_file():
                    archive.add(p, arcname=str(p.relative_to(stage)), recursive=False)
        verify_archive(temporary)
        archive_path = output / (batch + '.tar.gz')
        temporary.rename(archive_path)
        info = {'batch': batch, 'sha256': digest(archive_path), 'size': archive_path.stat().st_size}
        (output / (batch + '.json')).write_text(json.dumps(info))
        (output / 'latest.json.tmp').write_text(json.dumps(info))
        (output / 'latest.json.tmp').replace(output / 'latest.json')
        # Never expire a batch that N1 has not acknowledged. Keep 14 confirmed
        # batches locally; an unavailable N1 must not silently discard the queue.
        acknowledged = ''
        if status_path and status_path.exists():
            acknowledged = json.loads(status_path.read_text()).get('batch', '')
        for old in sorted(output.glob('*.tar.gz'))[:-14]:
            if old.name.removesuffix('.tar.gz') <= acknowledged:
                old.unlink()
                old.with_name(old.name.replace('.tar.gz', '.json')).unlink(missing_ok=True)
        return info


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--media', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lock', required=True)
    parser.add_argument('--status', type=Path)
    args = parser.parse_args()
    print(json.dumps(create_batch(args.database, args.media, args.output, args.lock, args.status)))
