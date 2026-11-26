#!/usr/bin/env python3
"""Copy local originals to the authenticated N1 origin and verify all content."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request
from urllib.parse import quote
from dotenv import dotenv_values


def migrate(source, origin, token, read_token):
    copied = []
    for path in sorted((source / 'products').rglob('*')):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError('Symbolic media paths cannot be migrated')
        name = str(path.relative_to(source))
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        req = urllib.request.Request(origin + '/objects/' + quote(name, safe='/'), data=payload, method='PUT',
                                     headers={'Authorization': 'Bearer ' + token, 'X-Content-SHA256': digest})
        with urllib.request.urlopen(req, timeout=120) as response:
            item = json.load(response)
            if item['sha256'] != digest:
                raise ValueError('Origin digest mismatch')
        copied.append(item)
    req = urllib.request.Request(origin + '/manifest', headers={'Authorization': 'Bearer ' + read_token})
    with urllib.request.urlopen(req, timeout=10) as response:
        inventory = {item['name']: item for item in json.load(response)['files']}
    for item in copied:
        if inventory.get(item['name']) != item:
            raise ValueError('Post-copy manifest mismatch')
    return {'copied_files': len(copied), 'copied_bytes': sum(item['size'] for item in copied), 'files': copied}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--origin-config', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    credentials = json.loads(args.origin_config.read_text())
    result = migrate(args.source, 'http://127.0.0.1:10080', credentials['write_token'], credentials['read_token'])
    args.report.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print('Migrated', result['copied_files'], 'images;', result['copied_bytes'], 'bytes; hashes verified')
