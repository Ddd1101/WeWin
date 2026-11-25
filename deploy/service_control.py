#!/usr/bin/env python3
"""Manage the exact systemd units of the deployed WeWin installation."""
import argparse
import shlex
import subprocess

GROUPS = {'frontend': ['nginx.service'], 'backend': ['wewin.service', 'wewin-scheduler.service'], 'data': ['wewin-backup.timer', 'wewin-storage-check.timer', 'wewin-cert-renew.timer']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('group', choices=GROUPS)
    parser.add_argument('action', choices=['start', 'stop', 'status'])
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    commands = [['systemctl', 'is-active' if args.action == 'status' else args.action, *GROUPS[args.group]]]
    if args.group == 'data' and args.action == 'start':
        commands.append(['systemctl', 'start', 'wewin-storage-check.service'])
    if args.group == 'data' and args.action == 'stop':
        commands.append(['systemctl', 'stop', 'wewin-backup.service', 'wewin-storage-check.service', 'wewin-cert-renew.service'])
    for command in commands:
        print(shlex.join(command), flush=True)
        if not args.dry_run:
            subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
