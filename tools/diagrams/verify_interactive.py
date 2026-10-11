"""Structural checks for the self-contained interactive diagram set."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import json
from html.parser import HTMLParser
from pathlib import Path
import re

from generate_interactive import OUTPUT, ROLE_BY_COLOR, ROLE_CSS, SPECS, source


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.tabs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "div" and "node" in values.get("class", "").split():
            assert values["data-id"] not in self.nodes
            self.nodes[values["data-id"]] = values
        if tag == "button" and "flowtab" in values.get("class", "").split():
            self.tabs.append(values["data-flow"])


for stem, spec in SPECS.items():
    html_path = OUTPUT / f"{stem}.html"
    md_path = OUTPUT / f"{stem}.md"
    assert html_path.is_file() and md_path.is_file()
    page = html_path.read_text()
    companion = md_path.read_text()
    parser = Elements()
    parser.feed(page)
    _, expected_nodes = source(stem)
    assert set(parser.nodes) == set(expected_nodes)
    match = re.search(r"const flows = (\{.*?\});\s*/\* ─── state", page, re.S)
    assert match, stem
    flows = json.loads(match.group(1))
    assert set(flows) == set(parser.tabs)
    assert 1 <= len(flows) <= 6
    assert all(flow["steps"] for flow in flows.values())
    for flow in flows.values():
        for step in flow["steps"]:
            assert step["from"] in parser.nodes
            assert step["to"] in parser.nodes
            assert step["color"] and step["title"]
            assert step["desc"] and step["payload"]
        assert f'### {flow["name"]}' in companion
    used_roles = {ROLE_BY_COLOR[item.get("fillcolor", "#DCEAF5")][0]
                  for item in expected_nodes.values()}
    assert 'class="legend"' in page
    legend = page.split('<div class="legend" aria-label="Component legend">', 1)[1].split('</div>', 1)[0]
    assert not re.search(r"#[0-9a-fA-F]{6}\b", legend)
    assert all(f"var({ROLE_CSS[role]})" in legend for role in used_roles)
    assert "{{" not in page
    assert "fonts.googleapis.com" not in page
    assert "data-mode=\"offline\"" in page and "data-mode=\"online\"" in page
    width, height = (630, 1120) if stem.startswith("03") else (896, 504)
    assert f"height: {height}px; width: {width}px" in page
    assert "function applyStep()" in page and "function drawWires()" in page
    print(f"PASS {stem}: {len(parser.nodes)} nodes, {len(flows)} flows, "
          f"{sum(len(f['steps']) for f in flows.values())} steps, {width}:{height} canvas")
