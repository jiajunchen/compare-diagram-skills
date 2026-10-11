"""Validate the two alternative sets against the reviewed source diagrams."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import re
import struct
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from generate_alternatives import (PLANTUML_THEME, STEMS, legend_items,
                                   specification)


ROOT = FIGURES
for renderer in ("diagrams_library", "plantuml"):
    for stem in STEMS:
        folder = ROOT / renderer
        source, nodes, _, _ = specification(stem)
        expected = (1080, 1920) if stem.startswith("03") else (1920, 1080)
        svg = folder / f"{stem}.svg"
        pdf = folder / f"{stem}.pdf"
        png = folder / f"{stem}.png"
        for path in (svg, pdf, png):
            assert path.is_file() and path.stat().st_size > 100, path
        root = ET.parse(svg).getroot()
        assert (int(root.attrib["width"]), int(root.attrib["height"])) == expected
        labels = [element.text or "" for element in root.iter()
                  if element.tag.endswith("text")]
        assert "Color legend" in labels
        assert not any(re.search(r"#[0-9a-fA-F]{6}\b", value) for value in labels)
        for color, label in legend_items(stem, renderer):
            assert label in labels
            assert any(rect.attrib.get("fill") == color for rect in root.findall("{http://www.w3.org/2000/svg}rect"))
        with png.open("rb") as image:
            header = image.read(24)
        assert header[:8] == b"\x89PNG\r\n\x1a\n"
        assert struct.unpack(">II", header[16:24]) == expected
        details = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
        assert "Pages:           1" in details
        page = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", details)
        assert page
        page_width, page_height = map(float, page.groups())
        assert abs(page_width / page_height - expected[0] / expected[1]) < 0.001
        for node in nodes:
            assert node["label"].split("\n")[0] in " ".join(labels), (
                renderer, stem, node["name"])
        if renderer == "plantuml":
            puml = (folder / f"{stem}.puml").read_text()
            assert f"skinparam backgroundColor {PLANTUML_THEME['background']}" in puml
            assert f"skinparam defaultFontColor {PLANTUML_THEME['text']}" in puml
            assert root.find("{http://www.w3.org/2000/svg}rect").attrib["fill"] == PLANTUML_THEME["background"]
            for node in nodes:
                assert f'as {node["name"]} ' in puml
            for edge in source["edges"]:
                assert edge["tail"] != edge["head"]
            assert len(re.findall(r" (?:-->|\.\.>) ", puml)) == len(source["edges"])
        print(f"PASS {renderer}/{stem}: {len(nodes)} nodes, "
              f"{len(source['edges'])} edges, {expected[0]}x{expected[1]}")
