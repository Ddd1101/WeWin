#!/usr/bin/env python3
"""Unprivileged N1 process supervision with one instance and bounded reconnect."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def supervise(root, role):
    config = json.loads((root / 'tunnel.json').read_text())
    if role == 'origin':
        command = [str(root / 'bin/wewin-media'), str(root / 'origin.json')]
    else:
        command = ['ssh', '-NT', '-i', str(root / 'id_ed25519'), '-o', 'IdentitiesOnly=yes',
                   '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                   '-o', 'UserKnownHostsFile=' + str(root / 'known_hosts'),
                   '-o', 'ConnectTimeout=10', '-o', 'ExitOnForwardFailure=yes',
                   '-o', 'ServerAliveInterval=15', '-o', 'ServerAliveCountMax=3',
                   '-R', '127.0.0.1:10080:127.0.0.1:18080', config['host']]
    with open(root / (role + '.lock'), 'a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        stopping = [False]
        child = [None]
        def stop(*_):
            stopping[0] = True
            if child[0] is not None:
                child[0].terminate()
        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        with open(root / (role + '.log'), 'a') as output:
            while not stopping[0]:
                child[0] = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
                child[0].wait()
                if not stopping[0]:
                    time.sleep(5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--role', choices=['origin', 'tunnel'], required=True)
    args = parser.parse_args()
    supervise(args.root.resolve(), args.role)
