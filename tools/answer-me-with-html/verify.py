"""Validate the generated guide with the repository's existing Playwright environment."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json
import re
from urllib.parse import unquote, urlsplit
from playwright.sync_api import sync_playwright

HERE = (FIGURES / 'answer-me-with-html')
ROOT = HERE.parent.parent
PAGE = HERE / 'architecture.html'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
source = (HERE / 'architecture.md').read_text()
files = sorted((ROOT / 'FencingVideoAnalysis').rglob('*.swift'))
functions = sum(len(re.findall(r'\bfunc\s+[A-Za-z_][A-Za-z0-9_]*\s*(?:<[^>]+>)?\s*\(', p.read_text())) for p in files)
assert len(files) == 35 and functions == 276
for path in files:
    assert f'../../{path.relative_to(ROOT).as_posix()}' in source
report = {'swiftFiles': len(files), 'namedFunctionDeclarations': functions, 'viewports': []}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=CHROME, headless=True)
    for width, height in [(1440, 1000), (1024, 768), (390, 844)]:
        page = browser.new_page(viewport={'width': width, 'height': height})
        errors = []
        requests = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: requests.append(request.url))
        page.goto(PAGE.as_uri())
        assert page.locator('nav a').count() == 8
        assert page.locator('svg').count() == 11
        for link in page.locator('nav a').all():
            target = link.get_attribute('href')
            assert page.locator(target).count() == 1
            link.click()
            assert page.evaluate('location.hash') == target
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.get_by_role('button', name='Theme: Blueprint').click()
        assert page.get_by_role('button', name='Theme: Cards').count() == 1
        page.get_by_role('button', name='Mode: Light').click()
        assert page.get_by_role('button', name='Mode: Dark').count() == 1
        page.get_by_role('button', name='Theme: Cards').click()
        page.get_by_role('button', name='Mode: Dark').click()
        links = page.locator('a[href]').evaluate_all('(elements) => elements.map(e => e.getAttribute("href"))')
        checked = 0
        for link in links:
            parts = urlsplit(link)
            if not parts.scheme and parts.path:
                assert (HERE / unquote(parts.path)).resolve().is_file(), link
                checked += 1
        assert not errors, errors
        assert not [url for url in requests if url.startswith(('http://', 'https://'))]
        page.locator('nav a').nth(0).click()
        page.screenshot(path=f'/tmp/sports-architecture-{width}.png')
        if width == 1440:
            page.locator('nav a').nth(4).click()
            page.screenshot(path='/tmp/sports-architecture-export-final.png')
        report['viewports'].append({'width': width, 'height': height, 'chapters': 8,
            'diagrams': 11, 'localLinksChecked': checked, 'horizontalOverflow': False,
            'browserErrors': errors, 'externalRequests': 0, 'navigation': 'passed',
            'themeAndModeControls': 'passed'})
        page.close()
    browser.close()
(HERE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
