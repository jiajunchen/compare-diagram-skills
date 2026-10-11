"""Check the Cocoon-style exports against their reviewed DOT sources.

Run with the workspace's ignored .venv/bin/python after generate_cocoon.py.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path
import re
import struct
import subprocess
import xml.etree.ElementTree as ET

from generate_cocoon import OUTPUT, STEMS, specification


SVG = "{http://www.w3.org/2000/svg}"


def verify(stem):
    data, source_nodes, by_id, source_clusters = specification(stem)
    portrait = stem.startswith("03")
    expected_size = (1080, 1920) if portrait else (1920, 1080)
    svg_path = OUTPUT / f"{stem}.svg"
    root = ET.parse(svg_path).getroot()
    assert tuple(map(int, root.attrib["viewBox"].split()[2:])) == expected_size
    assert root.attrib["role"] == "img"

    nodes = root.findall(f".//{SVG}g[@data-node]")
    edges = root.findall(f".//{SVG}path[@data-edge]")
    clusters = root.findall(f".//{SVG}rect[@data-cluster]")
    assert {node.attrib["data-node"] for node in nodes} == {
        node["name"] for node in source_nodes
    }
    assert sorted(edge.attrib["data-edge"] for edge in edges) == sorted(
        f'{by_id[edge["tail"]]["name"]}->{by_id[edge["head"]]["name"]}'
        for edge in data["edges"]
    )
    assert len(clusters) == len(source_clusters)

    # Component rectangles may not cover one another, and the legend starts
    # below every source cluster and component.
    boxes = []
    for node in nodes:
        rect = node.find(f"{SVG}rect")
        box = tuple(float(rect.attrib[key]) for key in ("x", "y", "width", "height"))
        assert box[0] >= 0 and box[1] >= 0
        assert box[0] + box[2] <= expected_size[0]
        boxes.append(box)
        assert node.find(f"{SVG}title") is not None
        assert node.findall(f"{SVG}text")
    for index, (x, y, width, height) in enumerate(boxes):
        for other_x, other_y, other_width, other_height in boxes[index + 1:]:
            assert min(x + width, other_x + other_width) - max(x, other_x) <= 1 or (
                min(y + height, other_y + other_height) - max(y, other_y) <= 1
            ), f"Overlapping nodes in {stem}"
    legend_y = 1680 if portrait else 890
    assert all(y + height < legend_y for _, y, _, height in boxes)
    assert all(float(rect.attrib["y"]) + float(rect.attrib["height"]) < legend_y
               for rect in clusters)
    visible_text = [element.text or "" for element in root.iter(f"{SVG}text")]
    assert "Color legend" in " ".join(visible_text)
    assert not any(re.search(r"#[0-9a-fA-F]{6}\b", label) for label in visible_text)

    html_page = (OUTPUT / f"{stem}.html").read_text()
    assert html_page.count("<svg ") == 1
    assert 'id="report-container"' in html_page
    assert 'class="toolbar-toggle"' in html_page
    assert "function downloadPNG" in html_page and "function downloadPDF" in html_page
    assert "#22d3ee" in html_page
    assert all(element.attrib["data-node"] in html_page for element in nodes)

    png = (OUTPUT / f"{stem}.png").read_bytes()
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", png[16:24]) == expected_size
    pdf = OUTPUT / f"{stem}.pdf"
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
    assert "Pages:           1" in info
    print(f"Verified {stem}: {len(nodes)} nodes, {len(edges)} connections, {expected_size}")


if __name__ == "__main__":
    assert Path(OUTPUT).is_dir()
    for diagram in STEMS:
        verify(diagram)
