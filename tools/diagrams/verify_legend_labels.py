"""Audit visible labels across every diagram set created for the MVP review.

CSS and SVG color attributes still contain hex values; only rendered text is
checked. PDF and PNG exports are rendered from the verified SVG sources.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from html.parser import HTMLParser
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET


ROOT = FIGURES
STEMS = (
    "01_architecture", "02a_entities", "02b_object_calls",
    "03a_organization_pathways", "03b_media_pathways",
)
HEX = re.compile(r"#[0-9a-fA-F]{6}\b")


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.labels = []

    def handle_starttag(self, tag, attributes):
        if tag in ("style", "script"):
            self.hidden += 1

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden and data.strip():
            self.labels.append(data.strip())


if __name__ == "__main__":
    svg_count = 0
    for folder in (ROOT / "graphviz", ROOT / "diagrams_library", ROOT / "plantuml", ROOT / "cocoon_generator"):
        for stem in STEMS:
            path = folder / f"{stem}.svg"
            root = ET.parse(path).getroot()
            labels = [element.text or "" for element in root.iter() if element.tag.endswith("text")]
            assert "Color legend" in labels, path
            assert not any(HEX.search(label) for label in labels), path
            svg_count += 1

    html_paths = [*(ROOT / "interactive").glob("*.html"),
                  *(ROOT / "cocoon_generator").glob("*.html"),
                  *(ROOT / "diagram_creator").glob("*.html"),
                  ROOT / "visual_explainer/codebase_review.html"]
    assert len(html_paths) == 16
    for path in html_paths:
        source = path.read_text()
        parsed = VisibleText()
        parsed.feed(source)
        assert not any(HEX.search(label) for label in parsed.labels), path
        assert 'class="legend"' in source or "Color legend" in parsed.labels, path

    canvas_paths = list((ROOT / "obsidian_canvas").glob("*.canvas"))
    assert len(canvas_paths) == 5
    for path in canvas_paths:
        data = json.loads(path.read_text())
        labels = [item.get("text", item.get("label", "")) for item in data["nodes"]]
        labels += [item.get("label", "") for item in data["edges"]]
        assert not any(HEX.search(label) for label in labels), path
        assert "## Color legend" in labels, path

    print(f"PASS: no hex codes in visible text of {svg_count} SVG, "
          f"{len(html_paths)} HTML, and {len(canvas_paths)} Canvas diagrams")
