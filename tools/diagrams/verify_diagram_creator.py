"""Check the diagram-creator pages in local Chrome using the ignored .venv."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path
import re

from playwright.sync_api import sync_playwright


ROOT = FIGURES
PAGES = sorted((ROOT / "diagram_creator").glob("diagram-*.html"))
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


if __name__ == "__main__":
    assert len(PAGES) == 5
    assert CHROME.is_file()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(CHROME))
        for page_file in PAGES:
            source = page_file.read_text()
            assert source.startswith("<!DOCTYPE html>")
            for width, height in ((1440, 900), (390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(page_file.as_uri(), wait_until="load")
                page.wait_for_timeout(700)
                report = page.evaluate("""() => {
                  const art = document.querySelector('.artboard');
                  const content = [...art.children];
                  const canvas = document.querySelector('#canvas');
                  const legend = document.querySelector('.legend');
                  const a = art.getBoundingClientRect();
                  const contained = content.every(item => {const c=item.getBoundingClientRect();
                    return c.top >= a.top-1 && c.bottom <= a.bottom+1 && c.left >= a.left-1 && c.right <= a.right+1});
                  return {ratio:art.clientWidth/art.clientHeight,
                    fit: contained,
                    legend: legend.children.length,
                    scale: canvas.style.transform,
                    title: document.querySelector('h1').getBoundingClientRect().bottom <= a.top,
                    labels: [...legend.querySelectorAll('.legend-item')].map(e=>e.textContent.trim())};
                }""")
                expected = 9 / 16 if "03" in page_file.name else 16 / 9
                assert abs(report["ratio"] - expected) < .02, (page_file, report)
                assert report["fit"], (page_file, width, report)
                assert report["title"], (page_file, width, report)
                assert report["legend"] >= 4, (page_file, report)
                assert not any(re.search(r"#[0-9a-fA-F]{6}\b", label) for label in report["labels"])
                assert report["scale"].startswith("translate(")
                page.locator("#zoom-in").click()
                assert not errors, (page_file, errors)
                print(f"PASS {page_file.name} at {width}x{height}")
                page.close()
        browser.close()
