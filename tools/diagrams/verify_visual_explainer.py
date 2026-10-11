"""Browser and source checks for the visual-explainer codebase review.

Run with the ignored workspace .venv. Requires Playwright and local Chrome.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from html.parser import HTMLParser
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = FIGURES
PAGE = ROOT / "visual_explainer/codebase_review.html"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
SECTIONS = ("architecture", "entities", "calls", "organization", "media", "review", "sources")


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.local = []

    def handle_starttag(self, tag, attributes):
        if tag != "a":
            return
        href = dict(attributes).get("href", "")
        if href.startswith("../"):
            self.local.append(href)


if __name__ == "__main__":
    assert CHROME.is_file(), f"Chrome is required at {CHROME}"
    page_source = PAGE.read_text()
    links = Links()
    links.feed(page_source)
    assert links.local
    for link in links.local:
        assert (PAGE.parent / link).is_file(), f"Broken source link: {link}"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(CHROME))
        for color in ("dark", "light"):
            for width, height in ((1280, 900), (390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height}, color_scheme=color)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(PAGE.resolve().as_uri(), wait_until="load")
                assert page.evaluate("document.documentElement.scrollWidth") == width
                assert page.locator("section").count() == len(SECTIONS)
                assert page.locator("figure svg[role=img]").count() == 5
                assert page.locator(".legend").count() == 5
                assert page.locator(".legend text").count() >= 20
                assert not page.locator(".legend text").evaluate_all(
                    "items => items.some(item => /#[0-9a-f]{6}\\b/i.test(item.textContent))"
                )
                for index, svg in enumerate(page.locator("figure svg").all()):
                    expected = 9 / 16 if index >= 3 else 16 / 9
                    box = svg.bounding_box()
                    assert abs(box["width"] / box["height"] - expected) < 0.002
                failures = page.evaluate("""() => [...document.querySelectorAll('figure svg')].flatMap((svg, i) => {
                    const bad = [];
                    const nodes = [...svg.querySelectorAll('g.node')];
                    nodes.forEach(g => {
                        const r = g.querySelector('rect').getBBox();
                        g.querySelectorAll('text').forEach(t => {
                            const b = t.getBBox();
                            if (b.x < r.x + 3 || b.x + b.width > r.x + r.width - 3 ||
                                b.y < r.y || b.y + b.height > r.y + r.height + 3)
                                bad.push(`${i}: text ${t.textContent}`);
                        });
                    });
                    nodes.forEach((g, a) => nodes.slice(a + 1).forEach(h => {
                        const x = g.querySelector('rect').getBBox();
                        const y = h.querySelector('rect').getBBox();
                        if (Math.min(x.x+x.width, y.x+y.width)-Math.max(x.x,y.x) > 1 &&
                            Math.min(x.y+x.height,y.y+y.height)-Math.max(x.y,y.y) > 1)
                            bad.push(`${i}: overlapping nodes`);
                    }));
                    svg.querySelectorAll('text.edge-label').forEach(t => {
                        const x = t.getBBox();
                        nodes.forEach(g => {
                            const y = g.querySelector('rect').getBBox();
                            if (Math.min(x.x+x.width,y.x+y.width)-Math.max(x.x,y.x) > 1 &&
                                Math.min(x.y+x.height,y.y+y.height)-Math.max(x.y,y.y) > 1)
                                bad.push(`${i}: edge label ${t.textContent} overlaps node`);
                        });
                    });
                    return bad;
                })""")
                assert not failures, failures
                page.locator('nav a[href="#media"]').click()
                nav = page.locator("nav").bounding_box()
                heading = page.locator("#media .section-head").bounding_box()
                assert heading["y"] >= nav["y"] + nav["height"] - 2
                page.locator('#architecture button[data-ref="viewmodel"]').hover()
                assert page.locator('#architecture g[data-ref="viewmodel"]').evaluate(
                    "el => el.classList.contains('is-emphasis')"
                )
                assert not errors, errors
                print(f"Verified {color} {width} × {height}: five figures, ratios, links, navigation")
                page.close()
        browser.close()
    print(f"Verified {len(links.local)} local source links")
