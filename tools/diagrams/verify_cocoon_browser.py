"""Check generated Cocoon HTML layouts in the workspace's local Chrome."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path

from playwright.sync_api import sync_playwright

from generate_cocoon import OUTPUT, STEMS


CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")


if __name__ == "__main__":
    if not CHROME.is_file():
        raise SystemExit(f"Chrome is required at {CHROME}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=str(CHROME))
        for stem in STEMS:
            for width, height in ((1440, 900), (390, 844)):
                page = browser.new_page(viewport={"width": width, "height": height})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto((OUTPUT / f"{stem}.html").resolve().as_uri(), wait_until="load")
                layout = page.evaluate("""() => {
                    const header = document.querySelector('.header').getBoundingClientRect();
                    const diagram = document.querySelector('.diagram-container').getBoundingClientRect();
                    const svg = document.querySelector('svg').getBoundingClientRect();
                    return {
                        gap: diagram.top - header.bottom,
                        ratio: svg.width / svg.height,
                        toolbar: getComputedStyle(document.querySelector('.toolbar-actions')).display,
                        legendHasHex: [...document.querySelectorAll('svg text')].some(
                            label => /#[0-9a-f]{6}(?![0-9a-f])/i.test(label.textContent)),
                        html2canvas: typeof html2canvas,
                        jsPDF: typeof window.jspdf?.jsPDF
                    };
                }""")
                expected = 9 / 16 if stem.startswith("03") else 16 / 9
                assert abs(layout["ratio"] - expected) < 0.002, (stem, width, layout)
                assert layout["gap"] >= 0, (stem, width, layout)
                assert layout["toolbar"] == "none", (stem, width, layout)
                assert not layout["legendHasHex"], (stem, width, layout)
                assert layout["html2canvas"] == "function", (stem, width, layout)
                assert layout["jsPDF"] == "function", (stem, width, layout)
                page.locator(".toolbar-toggle").click()
                assert page.locator(".toolbar-actions").is_visible()
                assert not errors, (stem, width, errors)
                page.close()
                print(f"Browser verified {stem} at {width} × {height}")
        browser.close()
