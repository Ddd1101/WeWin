#!/usr/bin/env python3
"""Build Web assets outside the repository; production API defaults to same-origin."""
import argparse
from pathlib import Path
import shlex
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='New or empty output directory outside the checkout')
    parser.add_argument('--skip-install', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output == repo or repo in output.parents:
        parser.error('Build output must be outside the Git checkout')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        parser.error('Output must be a new or empty directory')
    commands = [] if args.skip_install else [['npm', 'ci', '--no-audit', '--no-fund']]
    commands.append(['npm', 'run', 'build', '--', '--outDir', str(output)])
    for command in commands:
        print(shlex.join(command), flush=True)
        if not args.dry_run:
            subprocess.run(command, cwd=repo / 'Page', check=True)


if __name__ == '__main__':
    main()
