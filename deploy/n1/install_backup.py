#!/usr/bin/env python3
"""Install the versioned backup client without copying keys, data, or unrelated cron jobs."""
import argparse
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import tempfile

FILES = ('backup.py', 'backup_exchange.py', 'restore_backup.py')
BEGIN = '# BEGIN WEWIN BACKUP'
END = '# END WEWIN BACKUP'


def managed_cron(existing, entry, script_path):
    lines = existing.splitlines()
    if lines.count(BEGIN) != lines.count(END) or lines.count(BEGIN) > 1:
        raise ValueError('Invalid existing WeWin cron block')
    if BEGIN in lines:
        start, end = lines.index(BEGIN), lines.index(END)
        if end < start:
            raise ValueError('Invalid existing WeWin cron order')
        lines = lines[:start] + lines[end + 1:]
    retained = []
    for line in lines:
        if line == entry:
            continue  # Adopt the exact legacy entry installed before this tool.
        if str(script_path) in line and not line.lstrip().startswith('#'):
            raise ValueError('Different unmarked backup cron entry; reconcile it explicitly first')
        retained.append(line)
    return '\n'.join(retained).rstrip() + '\n' + BEGIN + '\n' + entry + '\n' + END + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Repository deploy directory containing the three client scripts')
    parser.add_argument('--root', type=Path, required=True, help='Existing backup directory containing id_ed25519 and known_hosts')
    parser.add_argument('--host', required=True, help='Pinned SSH exporter, e.g. root@47.250.165.79')
    parser.add_argument('--python', default='/usr/bin/python3')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only; exit 1 when changes are needed (default)')
    mode.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    source, root = args.source.resolve(), args.root.resolve()
    if root == Path('/') or source == root or root in source.parents or source in root.parents:
        parser.error('Source and backup root must be independent directories')
    if any(c in str(root) + args.host + args.python for c in '\n\r%'):
        parser.error('Cron arguments cannot contain newline or percent characters')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+@[A-Za-z0-9_.-]+', args.host):
        parser.error('Host must have user@hostname form')
    for name in FILES:
        if not (source / name).is_file():
            parser.error('Missing source script: ' + name)
    key, known = root / 'id_ed25519', root / 'known_hosts'
    if not key.is_file() or not known.is_file():
        parser.error('Provision the dedicated SSH key and pinned known_hosts outside Git first')
    if key.stat().st_mode & 0o077:
        parser.error('Private key must not be accessible by group/other users')
    if not Path(args.python).is_file():
        parser.error('Python executable is missing')
    script_path = root / 'bin/backup_exchange.py'
    command = [args.python, str(script_path), 'pull', '--root', str(root / 'batches'), '--host', args.host,
               '--identity', str(key), '--known-hosts', str(known)]
    entry = '*/5 * * * * ' + ' '.join(shlex.quote(value) for value in command) + ' >> ' + shlex.quote(str(root / 'pull.log')) + ' 2>&1'
    env = dict(os.environ, LC_ALL='C', LANG='C')
    current = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, env=env)
    if current.returncode and 'no crontab' not in current.stderr.lower():
        raise RuntimeError(current.stderr.strip())
    existing = current.stdout if current.returncode == 0 else ''
    desired = managed_cron(existing, entry, script_path)
    changed = [name for name in FILES if not (root / 'bin' / name).is_file() or (source / name).read_bytes() != (root / 'bin' / name).read_bytes()]
    if args.apply:
        (root / 'bin').mkdir(parents=True, exist_ok=True)
        (root / 'batches').mkdir(parents=True, exist_ok=True)
        for name in changed:
            target = root / 'bin' / name
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.wewin-install-', delete=False) as temp:
                temporary = Path(temp.name)
            try:
                shutil.copyfile(source / name, temporary)
                temporary.chmod(0o644)
                temporary.replace(target)
            finally:
                if temporary.exists():
                    temporary.unlink()
        if desired != existing:
            subprocess.run(['crontab', '-'], input=desired, universal_newlines=True, env=env, check=True)
    print(json.dumps({'mode': 'apply' if args.apply else 'check', 'files_to_update': changed, 'cron_update': desired != existing}))
    if not args.apply and (changed or desired != existing):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
