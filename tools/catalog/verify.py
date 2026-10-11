"""Verify the finished visual catalog without changing the original results."""
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

from support import FIGURES, HERE, REPO


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = set()

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == 'a' and 'href' in attrs:
            self.links.add(attrs['href'])


def main() -> None:
    catalog = json.loads((HERE / 'catalog.json').read_text())
    page_path = FIGURES / 'README.html'
    parser = Links()
    parser.feed(page_path.read_text())
    missing = set(catalog['requiredLinks']) - parser.links
    assert not missing, f'Original results or references missing: {missing}'
    for url in parser.links:
        parts = urlsplit(url)
        if not parts.scheme and parts.path:
            assert (FIGURES / unquote(parts.path)).exists(), url
    expected = sum(len(section['cards']) for section in catalog['sections'])
    checks = []
    scratch = REPO / '.runtime/figures/catalog/qa'
    scratch.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
        for width, height in [(1440, 1000), (1024, 900), (390, 844)]:
            context = browser.new_context(viewport={'width': width, 'height': height}, offline=True)
            page = context.new_page()
            errors, external = [], []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.on('request', lambda request: external.append(request.url) if request.url.startswith(('http:', 'https:')) else None)
            page.goto(page_path.as_uri(), wait_until='load')
            page.evaluate('document.fonts.ready')
            page.locator('.result img').evaluate_all('(images)=>images.forEach(i=>i.loading="eager")')
            page.locator('.result img').evaluate_all('(images)=>Promise.all(images.map(i=>i.decode()))')
            assert page.locator('.result').count() == expected
            assert page.locator('.collection').count() == len(catalog['sections'])
            for section in catalog['sections']:
                assert page.locator('#' + section['id'] + ' figure').count() == len(section['cards'])
            assert page.locator('.result img').evaluate_all('(images)=>images.every(i=>i.src.startsWith("data:image/jpeg;base64,")&&i.naturalWidth>500&&i.naturalHeight>200)')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), f'Overflow at {width}'
            assert page.evaluate('document.fonts.check("17px Geist") && document.fonts.check("48px \'Instrument Serif\'")')
            page.screenshot(path=str(scratch / f'catalog-{width}.png'), full_page=False)

            for section in catalog['sections']:
                page.locator('[data-filter="' + section['id'] + '"]').click()
                assert page.locator('.result:visible').count() == len(section['cards'])
                assert page.locator('.collection:visible').count() == 1
            page.locator('#reset').click()
            page.locator('#search').fill('qwen')
            assert page.locator('.result:visible').count() == 3
            page.locator('#search').fill('term-with-no-match')
            assert page.locator('#empty').is_visible()
            assert page.locator('.result:visible').count() == 0
            page.locator('#reset').click()
            assert page.locator('.result:visible').count() == expected

            page.locator('.preview').first.click()
            assert page.locator('dialog').is_visible()
            assert page.locator('#preview-image').evaluate('(image)=>image.complete&&image.naturalWidth>500')
            page.keyboard.press('Escape')
            assert not page.locator('dialog').is_visible()
            assert page.locator('.preview').first.evaluate('(button)=>button===document.activeElement')
            page.locator('#result-graphviz summary').click()
            assert page.locator('#result-graphviz table').is_visible()
            page.locator('#complete-index summary').click()
            assert page.locator('#complete-index .index').is_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            assert not errors, errors
            assert not external, external
            checks.append({'width': width, 'height': height, 'offline': True, 'previews': expected,
                           'filters': 'passed', 'search': 'passed', 'previewDialogAndKeyboard': 'passed',
                           'noHorizontalOverflow': True, 'browserErrors': errors, 'externalRequests': external})
            context.close()
        browser.close()
    report = {'collections': expected, 'originalLinksPreserved': len(catalog['requiredLinks']),
              'embeddedFontsAndPreviews': True, 'viewports': checks}
    (HERE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
