#!/usr/bin/env python3
"""Compatibility entry for production services; local development uses make run-* targets."""
from pathlib import Path
import subprocess
import sys

if __name__ == '__main__':
    raise SystemExit(subprocess.call(['bash', str(Path(__file__).resolve().with_name('start.sh')), *sys.argv[1:]]))
