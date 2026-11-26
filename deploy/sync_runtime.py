#!/usr/bin/env python3
"""Audit/copy Git-managed Server and deploy source, excluding runtime data."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--check', action='store_true', help='Read-only audit (default), exit 1 for drift')
    mode.add_argument('--apply', action='store_true', help='Copy changed source only; does not migrate/restart/delete files')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    destination = args.destination.resolve()
    if destination == Path('/') or destination == repo or repo in destination.parents or destination in repo.parents:
        parser.error('Destination must be an independent runtime directory')
    names = subprocess.check_output(['git', '-C', str(repo), 'ls-files', '-z', '--', 'Server', 'deploy']).decode().split('\0')
    excluded = {'media', 'venv', 'venv2', 'staticfiles', '__pycache__', 'node_modules'}
    suffixes = {'.py', '.sh', '.txt', '.md', '.json', '.conf', '.service', '.timer', '.example'}
    changed = []
    for name in filter(None, names):
        relative = Path(name)
        if excluded.intersection(relative.parts) or relative.name == 'token.txt' or relative.suffix not in suffixes:
            continue
        source = repo / relative
        if not source.is_file() or source.is_symlink():
            raise RuntimeError('Missing or symbolic-link source: ' + name)
        target = destination / relative
        if destination not in target.resolve().parents or target.is_symlink():
            raise RuntimeError('Unsafe runtime path: ' + name)
        if target.is_file() and source.read_bytes() == target.read_bytes():
            continue
        changed.append(name)
        if args.apply:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.wewin-source-', delete=False) as temp:
                temporary = Path(temp.name)
            try:
                shutil.copy2(source, temporary)
                temporary.replace(target)
            finally:
                if temporary.exists():
                    temporary.unlink()
    print(json.dumps({'mode': 'apply' if args.apply else 'check', 'changed': changed}, ensure_ascii=False))
    if changed and not args.apply:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
