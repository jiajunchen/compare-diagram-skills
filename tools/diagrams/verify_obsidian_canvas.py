"""Validate the five editable Canvas files against their reviewed DOT graphs."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import json
from pathlib import Path
import re

from generate_obsidian_canvas import (LEGENDS, OUTPUT, PALETTE, ROOT, STEMS,
                                      graph_spec, stable_id)


HEX = re.compile(r"#[0-9a-fA-F]{6}\b")
SIDES = {"top", "right", "bottom", "left"}


def intersects(a, b):
    width = min(a["x"] + a["width"], b["x"] + b["width"]) - max(a["x"], b["x"])
    height = min(a["y"] + a["height"], b["y"] + b["height"]) - max(a["y"], b["y"])
    return width > 2 and height > 2


for stem in STEMS:
    source = graph_spec(stem)
    page = OUTPUT / f"{stem}.canvas"
    data = json.loads(page.read_text())
    assert set(data) == {"nodes", "edges"}, page
    nodes, edges = data["nodes"], data["edges"]
    assert nodes and nodes[0]["type"] == "group", page
    expected_size = (1080, 1920) if stem.startswith("03") else (1920, 1080)
    assert (nodes[0]["width"], nodes[0]["height"]) == expected_size, page
    assert nodes[0]["x"] == nodes[0]["y"] == 0, page
    assert expected_size[0] / expected_size[1] == (9 / 16 if stem.startswith("03") else 16 / 9)
    assert len({item["id"] for item in nodes + edges}) == len(nodes) + len(edges), page

    primary = [item for item in source["objects"] if not item["name"].startswith("cluster_")]
    by_id = {item["id"]: item for item in nodes}
    primary_cards = []
    for item in primary:
        card = by_id[stable_id(stem, "node", item["name"])]
        assert card["type"] == "text" and item["label"].split("\n")[0] in card["text"]
        primary_cards.append(card)
    assert len(edges) == len(source["edges"]), page
    for item in nodes:
        assert item["type"] in {"text", "group"}, page
        assert all(isinstance(item[key], int) for key in ("x", "y", "width", "height")), page
        assert item["width"] > 0 and item["height"] > 0, page
        assert item["x"] >= 0 and item["y"] >= 0, page
        assert item["x"] + item["width"] <= expected_size[0], (page, item["id"])
        assert item["y"] + item["height"] <= expected_size[1], (page, item["id"])
        if "color" in item:
            assert item["color"] in PALETTE.values(), page
        if item["type"] == "text":
            assert not HEX.search(item["text"]), page
    text_cards = [item for item in nodes if item["type"] == "text"]
    for index, a in enumerate(text_cards):
        for b in text_cards[index + 1:]:
            assert not intersects(a, b), (page, a["id"], b["id"])

    for index, edge in enumerate(edges):
        assert edge["id"] == stable_id(stem, "edge", index)
        assert edge["fromNode"] in by_id and edge["toNode"] in by_id
        assert edge["fromSide"] in SIDES and edge["toSide"] in SIDES
        assert edge["color"] in PALETTE.values()
        assert not HEX.search(edge.get("label", ""))
    for index, (color, label) in enumerate(LEGENDS[stem]):
        card = by_id[stable_id(stem, "node", f"legend-{index}")]
        assert card["text"] == label and card["color"] == PALETTE[color]
    assert by_id[stable_id(stem, "node", "legend-title")]["text"] == "## Color legend"
    print(f"PASS {page.relative_to(ROOT)}: {len(primary)} source cards, "
          f"{len(edges)} links, {expected_size[0]}×{expected_size[1]} board")
