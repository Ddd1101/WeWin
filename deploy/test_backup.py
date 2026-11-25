import io
import json
from pathlib import Path
import sqlite3
import tarfile
import tempfile
import unittest

from backup import create_batch, verify_archive
from restore_backup import restore


class BackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.database = self.root / 'source.sqlite3'
        with sqlite3.connect(self.database) as db:
            db.execute('CREATE TABLE product (id INTEGER PRIMARY KEY, image TEXT, price TEXT, created TEXT, payload TEXT)')
            db.execute('INSERT INTO product VALUES (1, ?, ?, ?, ?)', ('products/image.png', '123.45', '2026-11-25 13:00:00.123456', '{"amount":"123.45"}'))
        self.media = self.root / 'media'
        (self.media / 'products').mkdir(parents=True)
        (self.media / 'products/image.png').write_bytes(b'file content used for integrity check')
        self.output = self.root / 'batches'

    def test_joint_restore_preserves_precision_and_content(self):
        info = create_batch(self.database, self.media, self.output, self.root / 'lock')
        archive = self.output / (info['batch'] + '.tar.gz')
        destination = self.root / 'restored'
        report = restore(archive, destination)
        self.assertEqual(report['missing_images'], [])
        self.assertEqual(report['tables']['product'], 1)
        with sqlite3.connect(self.database) as before, sqlite3.connect(destination / 'db.sqlite3') as after:
            self.assertEqual(before.execute('SELECT * FROM product').fetchall(), after.execute('SELECT * FROM product').fetchall())
        self.assertEqual((destination / 'media/products/image.png').read_bytes(), (self.media / 'products/image.png').read_bytes())
        with self.assertRaises(FileExistsError):
            restore(archive, destination)

    def test_corruption_is_rejected(self):
        archive = self.root / 'bad.tar.gz'
        manifest = json.dumps({'files': {'db.sqlite3': 'incorrect-digest'}}).encode()
        with tarfile.open(archive, 'w:gz') as out:
            for name, content in [('manifest.json', manifest), ('db.sqlite3', b'bad')]:
                info = tarfile.TarInfo(name)
                info.size = len(content)
                out.addfile(info, io.BytesIO(content))
        with self.assertRaises(ValueError):
            verify_archive(archive)

    def test_traversal_is_rejected(self):
        archive = self.root / 'unsafe.tar.gz'
        with tarfile.open(archive, 'w:gz') as out:
            info = tarfile.TarInfo('../escape')
            info.size = 1
            out.addfile(info, io.BytesIO(b'x'))
        with self.assertRaises(ValueError):
            verify_archive(archive)

    def test_unacknowledged_batches_are_not_pruned(self):
        self.output.mkdir()
        for index in range(15):
            name = '20260101T0000%02d000000Z' % index
            (self.output / (name + '.tar.gz')).write_bytes(b'older queued batch')
            (self.output / (name + '.json')).write_text('{}')
        create_batch(self.database, self.media, self.output, self.root / 'lock')
        self.assertEqual(len(list(self.output.glob('*.tar.gz'))), 16)


class RemoteBackupTests(BackupTests):
    def test_remote_batch_contains_manifest_not_images(self):
        from unittest.mock import patch
        from contextlib import contextmanager
        import os
        import hashlib
        data = (self.media / 'products/image.png').read_bytes()
        inventory = {'files': [{'name': 'products/image.png', 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}]}
        @contextmanager
        def fetch(*args, **kwargs):
            yield io.BytesIO(json.dumps(inventory).encode())
        with patch.dict(os.environ, {'MEDIA_ORIGIN_URL': 'http://127.0.0.1:10080', 'MEDIA_ORIGIN_READ_TOKEN': 'test-token'}), patch('urllib.request.urlopen', fetch):
            info = create_batch(self.database, self.media, self.output, self.root / 'lock')
        archive = self.output / (info['batch'] + '.tar.gz')
        with tarfile.open(archive) as packed:
            self.assertIn('media-manifest.json', packed.getnames())
            self.assertNotIn('media/products/image.png', packed.getnames())
        report = restore(archive, self.root / 'external-restore', self.media)
        self.assertTrue(report['media_verified'])
        self.assertEqual(report['missing_images'], [])

    def test_cloud_budget_rejects_new_batch(self):
        sparse = self.output / 'backlog.bin'
        self.output.mkdir()
        with open(sparse, 'wb') as file:
            file.truncate(512 * 1024 * 1024)
        with self.assertRaises(OSError):
            create_batch(self.database, self.media, self.output, self.root / 'lock')
