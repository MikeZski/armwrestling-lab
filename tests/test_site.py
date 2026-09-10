"""Dependency-free source, build and HTTP regression tests.
Run from the project root: python -m unittest discover -s tests -p "test_*.py" -v
"""
from __future__ import annotations
import functools
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest
import zipfile
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    return json.loads((ROOT / 'content' / name).read_text(encoding='utf-8'))

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='awl-tests-')
        cls.parent = Path(cls.temp.name)
        cls.repo = cls.parent / 'armwrestling-lab'
        cls.repo.mkdir()
        for folder in ('content', 'static', 'scripts'):
            shutil.copytree(ROOT / folder, cls.repo / folder, ignore=shutil.ignore_patterns('__pycache__'))
        subprocess.run([sys.executable, 'scripts/build.py', '--site-url', 'https://example.github.io/lab'],
                       cwd=cls.repo, check=True, capture_output=True)
        cls.output = cls.repo / 'site'

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_enabled_languages_complete(self):
        cfg = load('site.json')
        expected = {a['id'] for a in load('articles.json')}
        keys = set(load('ui/en.json'))
        for language in cfg['published_languages']:
            with self.subTest(language=language):
                translated = load(f'articles/{language}.json')
                self.assertEqual(expected, set(translated))
                self.assertEqual(keys, set(load(f'ui/{language}.json')))
                for article in translated.values():
                    self.assertGreaterEqual(len(article['sections']), 3)
                    self.assertTrue(article['figure']['caption'])
                    self.assertTrue(article['limitations'])

    def test_calculated_figures(self):
        figures = load('figures.json')
        for body_fat, ffm, ffmi in figures['ffmi-example']['rows']:
            self.assertAlmostEqual(90 * (1 - float(body_fat.strip('%')) / 100), ffm, places=2)
            self.assertAlmostEqual(ffm / (1.8 ** 2), ffmi, places=2)
        for frequency, interval in figures['sampling-intervals']['rows']:
            self.assertAlmostEqual(1000 / float(frequency.split()[0]), interval, places=2)
        for force, arm, moment in figures['torque-example']['rows']:
            self.assertAlmostEqual(float(force.split()[0]) * float(arm.split()[0]), float(moment.split()[0]))
        a, b, difference = figures['enhanced-comparison']['values']
        self.assertAlmostEqual(b - a, difference, places=2)
        for figure in figures.values():
            if figure['kind'] == 'interval':
                for _, point, low, high in figure['rows']:
                    self.assertLessEqual(low, point)
                    self.assertLessEqual(point, high)

    def test_reports_are_real_pdfs_and_unchanged(self):
        for item in load('downloads.json'):
            if item.get('path'):
                original = ROOT / 'static' / item['path']
                built = self.output / item['path']
                self.assertTrue(original.read_bytes().startswith(b'%PDF-'))
                self.assertEqual(hashlib.sha256(original.read_bytes()).digest(), hashlib.sha256(built.read_bytes()).digest())

    def test_package_keeps_download_archives(self):
        asset = self.repo / 'static/downloads/software/regression-example.zip'
        asset.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(asset, 'w') as example:
            example.writestr('README.txt', 'Temporary regression fixture, not a published release.')
        try:
            subprocess.run([sys.executable, 'scripts/build.py', '--site-url', 'https://example.github.io/lab'],
                           cwd=self.repo, check=True, capture_output=True)
            packed = self.parent / 'regression-test.zip'
            subprocess.run([sys.executable, 'scripts/package.py', '--output', str(packed)],
                           cwd=self.repo, check=True, capture_output=True)
            with zipfile.ZipFile(packed) as archive:
                for prefix in ['static', 'site']:
                    name = 'armwrestling-lab/' + prefix + '/downloads/software/regression-example.zip'
                    self.assertIn(name, archive.namelist())
                    self.assertEqual(archive.read(name), asset.read_bytes())
        finally:
            asset.unlink()
            subprocess.run([sys.executable, 'scripts/build.py', '--site-url', 'https://example.github.io/lab'],
                           cwd=self.repo, check=True, capture_output=True)

    def test_public_url_metadata_and_sitemap(self):
        urls = ElementTree.parse(self.output / 'sitemap.xml').findall('{*}url')
        languages = load('site.json')['published_languages']
        self.assertEqual(len(urls), len(languages) * 21)
        for entry in urls:
            self.assertTrue(entry.find('{*}loc').text.startswith('https://example.github.io/lab/'))
            self.assertEqual(len(entry.findall('{*}link')), len(languages))
        article = (self.output / 'pl/articles/train-rfd/index.html').read_text(encoding='utf-8')
        self.assertIn('https://example.github.io/lab/pl/articles/train-rfd/index.html', article)
        self.assertIn('https://example.github.io/lab/assets/img/train-rfd.webp', article)
        self.assertIn('https://example.github.io/lab/en/index.html', (self.output / '404.html').read_text(encoding='utf-8'))
        self.assertIn('Sitemap: https://example.github.io/lab/sitemap.xml', (self.output / 'robots.txt').read_text(encoding='utf-8'))

    def test_structure_under_repository_path(self):
        result = subprocess.run([sys.executable, 'scripts/check.py'], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(json.loads(result.stdout)['passed'])

    def test_reproducible_build(self):
        def digest():
            return {p.relative_to(self.output).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in self.output.rglob('*') if p.is_file()}
        before = digest()
        subprocess.run([sys.executable, 'scripts/build.py', '--site-url', 'https://example.github.io/lab'],
                       cwd=self.repo, check=True, capture_output=True)
        self.assertEqual(before, digest())

    def test_http_delivery_root_and_subpath(self):
        # Real HTTP requests use Python, independently of browser navigation policies.
        for directory, prefix in [(self.output, ''), (self.parent, '/armwrestling-lab/site')]:
            server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(directory)))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                for resource in ['index.html', 'pl/articles/train-rfd/index.html', 'en/downloads/index.html',
                                 'assets/site.css', 'assets/site.js', 'assets/img/logo.webp',
                                 'downloads/reports/rfd-training-en.pdf', 'data/en/train-rfd.json']:
                    with self.subTest(prefix=prefix, resource=resource):
                        url = f'http://127.0.0.1:{server.server_port}{prefix}/{resource}'
                        with urlopen(url, timeout=5) as response:
                            self.assertEqual(response.status, 200)
                            self.assertEqual(response.read(), (self.output / resource).read_bytes())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_offline_build_does_not_publish_fake_domain(self):
        subprocess.run([sys.executable, 'scripts/build.py', '--site-url', ''], cwd=self.repo, check=True, capture_output=True)
        try:
            self.assertFalse((self.output / 'sitemap.xml').exists())
            content = (self.output / 'pl/index.html').read_text(encoding='utf-8')
            self.assertNotIn('rel="canonical"', content)
            self.assertNotIn('example.github.io', content)
        finally:
            subprocess.run([sys.executable, 'scripts/build.py', '--site-url', 'https://example.github.io/lab'],
                           cwd=self.repo, check=True, capture_output=True)

if __name__ == '__main__':
    unittest.main()
