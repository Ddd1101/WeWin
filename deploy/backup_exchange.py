#!/usr/bin/env python3
"""Restricted SSH exporter and unprivileged N1 puller. Compatible with Python 3.7."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time
import fcntl
from datetime import datetime, timezone

from backup import digest, verify_archive


def serve(root, status):
    args = shlex.split(os.getenv('SSH_ORIGINAL_COMMAND', ''))
    if args == ['list']:
        print(json.dumps([json.loads(p.read_text()) for p in sorted(root.glob('*.json')) if re.fullmatch(r'\d{8}T\d{12}Z\.json', p.name)]))
        return
    if len(args) != 2 or args[0] not in ('get', 'ack') or not re.fullmatch(r'\d{8}T\d{12}Z', args[1]):
        raise ValueError('Unsupported backup command')
    info = json.loads((root / (args[1] + '.json')).read_text())
    if args[0] == 'get':
        with open(root / (args[1] + '.tar.gz'), 'rb') as archive:
            import shutil
            shutil.copyfileobj(archive, sys.stdout.buffer)
    else:
        latest = json.loads((root / 'latest.json').read_text())
        if info['batch'] == latest['batch']:
            status.parent.mkdir(parents=True, exist_ok=True)
            created_at = datetime.strptime(info['batch'], '%Y%m%dT%H%M%S%fZ').replace(tzinfo=timezone.utc).timestamp()
            status.with_suffix('.tmp').write_text(json.dumps(dict(info, completed_at=time.time(), source_created_at=created_at)))
            os.chmod(status.with_suffix('.tmp'), 0o644)
            status.with_suffix('.tmp').replace(status)
        print('verified')


def pull(root, host, identity, known_hosts):
    root.mkdir(parents=True, exist_ok=True)
    ssh = ['ssh', '-T', '-i', str(identity), '-o', 'IdentitiesOnly=yes', '-o', 'BatchMode=yes',
           '-o', 'StrictHostKeyChecking=yes', '-o', 'UserKnownHostsFile=' + str(known_hosts),
           '-o', 'ConnectTimeout=10', '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3', host]
    with open(root / '.pull.lock', 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        batches = json.loads(subprocess.check_output(ssh + ['list'], timeout=60))
        for info in batches:
            batch = info['batch']
            if not re.fullmatch(r'\d{8}T\d{12}Z', batch):
                raise ValueError('Invalid batch id')
            target = root / (batch + '.tar.gz')
            if not target.exists() or digest(target) != info['sha256']:
                partial = target.with_suffix('.part')
                try:
                    with open(partial, 'wb') as out:
                        subprocess.run(ssh + ['get ' + batch], stdout=out, check=True, timeout=1200)
                    if partial.stat().st_size != info['size'] or digest(partial) != info['sha256']:
                        raise ValueError('Transfer checksum mismatch')
                    verify_archive(partial)
                    partial.replace(target)
                finally:
                    if partial.exists():
                        partial.unlink()
            else:
                verify_archive(target)
            subprocess.run(ssh + ['ack ' + batch], check=True, timeout=60)
            try:
                current = json.loads((root / 'latest.json').read_text()).get('batch', '')
            except (OSError, ValueError):
                current = ''
            if info['batch'] >= current:
                (root / 'latest.json.tmp').write_text(json.dumps(dict(info, completed_at=time.time())))
                (root / 'latest.json.tmp').replace(root / 'latest.json')
        for old in sorted(root.glob('*.tar.gz'))[:-30]:
            old.unlink()
        print('Verified backup batches:', len(batches))


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['serve', 'pull'])
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--status', type=Path)
    parser.add_argument('--host')
    parser.add_argument('--identity', type=Path)
    parser.add_argument('--known-hosts', type=Path)
    args = parser.parse_args()
    if args.mode == 'serve':
        serve(args.root, args.status)
    else:
        try:
            pull(args.root, args.host, args.identity, args.known_hosts)
        except BlockingIOError:
            print('A backup pull is already running; the next cron tick will retry')
