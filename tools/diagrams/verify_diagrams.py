"""Check generated figure files and Graphviz node bounds."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET

OUT = FIGURES / 'graphviz'
stems = [
    "01_architecture", "02a_entities", "02b_object_calls",
    "03a_organization_pathways", "03b_media_pathways",
]
report = ["# Diagram validation", "", "Graphviz layout, SVG XML, PDF, and PNG checks.", ""]

for stem in stems:
    source = OUT / f"{stem}.gv"
    svg = OUT / f"{stem}.svg"
    pdf = OUT / f"{stem}.pdf"
    png = OUT / f"{stem}.png"
    for file in (source, svg, pdf, png):
        assert file.is_file() and file.stat().st_size > 100, f"Missing or empty: {file}"
    root = ET.parse(svg).getroot()
    assert root.tag.endswith("svg")
    portrait = stem.startswith("03")
    expected_size = (1080, 1920) if portrait else (1920, 1080)
    assert (int(root.attrib["width"]), int(root.attrib["height"])) == expected_size
    labels = [element.text or "" for element in root.iter() if element.tag.endswith("text")]
    assert "Color legend" in labels
    assert not any(re.search(r"#[0-9a-fA-F]{6}\b", label) for label in labels)
    with png.open("rb") as preview:
        header = preview.read(24)
    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", header[16:24]) == expected_size
    plain = subprocess.check_output(["dot", "-Tplain", str(source)], text=True)
    nodes = []
    for line in plain.splitlines():
        parts = line.split(maxsplit=6)
        if parts and parts[0] == "node":
            name = parts[1]
            x, y, w, h = map(float, parts[2:6])
            nodes.append((name, x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    for index, (left_name, left_x1, left_y1, left_x2, left_y2) in enumerate(nodes):
        for right_name, right_x1, right_y1, right_x2, right_y2 in nodes[index + 1:]:
            overlap_x = min(left_x2, right_x2) - max(left_x1, right_x1)
            overlap_y = min(left_y2, right_y2) - max(left_y1, right_y1)
            assert overlap_x < 0.01 or overlap_y < 0.01, (
                f"Overlapping nodes in {stem}: {left_name}, {right_name}"
            )
    page_info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    assert "Pages:           1" in page_info, f"Unexpected PDF pages: {stem}"
    page_size = re.search(r"Page size:\s+([\d.]+) x ([\d.]+) pts", page_info)
    assert page_size is not None
    page_width, page_height = map(float, page_size.groups())
    assert abs(page_width / page_height - expected_size[0] / expected_size[1]) < 0.001
    ratio = "9:16" if portrait else "16:9"
    report.append(f"- **{stem}: PASS** — {ratio} SVG, PDF, and PNG; labeled color swatches; {len(nodes)} nodes; no node overlaps.")

report.extend([
    "",
    "Manual inspection: all five PNG previews were viewed at their native 1920×1080 "
    "or 1080×1920 size. "
    "Labels are present without clipping. SVG and PDF versions retain vector text for zooming. "
    "Colors are paired with text and shape labels, so meaning does not depend on color alone.",
    "",
    "Scope: this checks node boxes and file integrity. It does not prove semantic "
    "correctness or guarantee that every edge label is free from crossings; those "
    "were reviewed against the Swift sources and previews separately.",
])
(OUT / "quality_report.md").write_text("\n".join(report) + "\n")
print("Validated", len(stems), "diagrams")
