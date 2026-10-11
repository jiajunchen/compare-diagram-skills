"""Check that the static catalog can be published from the repository root."""
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.paths = set()

    def handle_starttag(self, tag, attributes):
        for key, value in attributes:
            if key in {'href', 'src'} and value:
                parts = urlsplit(value)
                if not parts.scheme and parts.path:
                    self.paths.add(unquote(parts.path))


class PublishingTests(unittest.TestCase):
    def test_homepage_contains_current_catalog(self):
        self.assertEqual((ROOT / 'index.html').read_bytes(),
                         (ROOT / 'README.html').read_bytes())

    def test_catalog_local_links_exist_and_are_publishable(self):
        parser = Links()
        parser.feed((ROOT / 'README.html').read_text())
        for path in sorted(parser.paths):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).exists(), path)
                result = subprocess.run(['git', 'check-ignore', '--', path],
                                        cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stdout)


if __name__ == '__main__':
    unittest.main()
