"""Exercise fullscreen layout in a local Chrome/Chromium browser.

Install figures/tools/diagrams/requirements-browser.txt in the ignored .venv before running.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright

from generate_interactive import OUTPUT, SPECS


BROWSER = next((candidate for candidate in (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"), shutil.which("chromium"),
    shutil.which("chrome"),
) if candidate and Path(candidate).is_file()), None)
if BROWSER is None:
    raise SystemExit("Chrome or Chromium is required for interactive browser checks")


def layout_state(page):
    return page.evaluate("""() => {
      const box = (element) => element.getBoundingClientRect();
      const canvas = document.querySelector('.canvas');
      const head = box(document.querySelector('.canvas-head'));
      const stage = box(document.querySelector('.stage'));
      const nodes = [...document.querySelectorAll('.node')].map((element) => ({
        id: element.dataset.id, box: box(element)
      }));
      const overlap = [];
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i].box, b = nodes[j].box;
          if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 1 &&
              Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 1) {
            overlap.push([nodes[i].id, nodes[j].id]);
          }
        }
      }
      const topElement = document.elementFromPoint(100, 80);
      return {
        ratio: stage.width / stage.height,
        titleClear: nodes.every((node) => node.box.top >= head.bottom),
        pageHeaderCovered: Boolean(topElement && topElement.closest('.canvas') === canvas),
        legendHasHex: /#[0-9a-f]{6}(?![0-9a-f])/i.test(document.querySelector('.legend').textContent),
        overlap
      };
    }""")


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=BROWSER, headless=True)
    for width, height in ((1600, 900), (900, 700), (390, 844)):
        for stem in SPECS:
            page = browser.new_page(viewport={"width": width, "height": height})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto((OUTPUT / f"{stem}.html").as_uri())
            page.wait_for_function(
                "document.getElementById('stepIdx').textContent.startsWith('1 /')")
            page.locator("#btnFullscreen").click()
            page.wait_for_timeout(100)
            state = layout_state(page)
            expected = 9 / 16 if stem.startswith("03") else 16 / 9
            assert abs(state["ratio"] - expected) < 0.001, (stem, width, state)
            assert state["titleClear"], (stem, width, state)
            assert state["pageHeaderCovered"], (stem, width, state)
            assert not state["legendHasHex"], (stem, width, state)
            assert not state["overlap"], (stem, width, state)
            assert not errors, (stem, width, errors)
            page.keyboard.press("Escape")
            assert "is-fullscreen" not in page.locator(".canvas").get_attribute("class")
            assert "diagram-fullscreen" not in page.locator("body").get_attribute("class")
            page.close()
            print(f"PASS fullscreen {stem} at {width}x{height}")
    browser.close()
