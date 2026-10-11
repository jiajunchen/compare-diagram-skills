"""Build editable Obsidian JSON Canvas views from the reviewed DOT sources.

Run with the ignored workspace .venv. Graphviz provides node layout; this
script uses only Python's standard library and never edits an Obsidian vault.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from hashlib import blake2b
import json
from pathlib import Path
import subprocess


ROOT = FIGURES
OUTPUT = ROOT / "obsidian_canvas"
STEMS = (
    "01_architecture", "02a_entities", "02b_object_calls",
    "03a_organization_pathways", "03b_media_pathways",
)

# Exact accents from Diagram Creator's default dark theme. Obsidian controls
# the board's background and text appearance; Canvas stores card/edge colors.
PALETTE = {
    "blue": "#2d7aff", "cyan": "#00d4ff", "green": "#00e5a0",
    "orange": "#ff8c42", "red": "#ff4d6a", "dim": "#4a6080",
}
SOURCE_COLORS = {
    "#DCEAF5": "blue", "#ECE4F5": "cyan", "#DDF0E5": "green",
    "#FFF0D6": "orange", "#EFF2F4": "dim", "#FBE4E1": "red",
}
LEGENDS = {
    STEMS[0]: (("blue", "SwiftUI views"), ("cyan", "View models"),
               ("green", "On-device services"), ("orange", "Device-local state"),
               ("dim", "Person / Apple services")),
    STEMS[1]: (("cyan", "App settings"), ("blue", "Tournament / bout"),
               ("green", "Media records"), ("orange", "Schema-only run"),
               ("dim", "Apple media assets")),
    STEMS[2]: (("dim", "Entry / Apple frameworks"), ("blue", "UI and review state"),
               ("cyan", "Workflow orchestration"), ("green", "Application services"),
               ("orange", "Local repository")),
    STEMS[3]: (("dim", "User entry"), ("blue", "UI action / screen"),
               ("green", "On-device processing"), ("orange", "Decision")),
    STEMS[4]: (("dim", "User entry"), ("blue", "UI action / screen"),
               ("green", "On-device processing"), ("cyan", "Cloud upload"),
               ("orange", "Decision / local cleanup"), ("red", "Failure / deletion")),
}
NOTES = {
    STEMS[0]: "One native SwiftUI app. SwiftData is local; Photos retains originals; private CloudKit syncs confirmed metadata and edited clips. No app-owned backend server.",
    STEMS[1]: "Arrows represent UUID references or links to external assets, not runtime calls. ScheduleExtractionRun exists in the schema without a production insert path.",
    STEMS[2]: "Principal production cross-component calls. Private helpers and framework callbacks are indexed in figures/CALL_INDEX.md; addBout has no production view caller.",
    STEMS[3]: "Manual and screenshot paths meet at editable drafts. Confirmation inserts bouts; discarding drafts does not. Cloud refresh can continue after the local screen appears.",
    STEMS[4]: "Export or cloud failures retain retry states. Playback uses local export/cache or downloads an edited CKAsset. Cleanup leaves Photos originals intact.",
}


def stable_id(*parts):
    return blake2b("/".join(map(str, parts)).encode(), digest_size=8).hexdigest()


def graph_spec(stem):
    raw = subprocess.check_output(["dot", "-Tjson", str(ROOT / "graphviz" / f"{stem}.gv")])
    return json.loads(raw)


def text_node(stem, name, text, x, y, width, height, color=None):
    node = {"id": stable_id(stem, "node", name), "type": "text",
            "text": text, "x": round(x), "y": round(y),
            "width": round(width), "height": round(height)}
    if color:
        node["color"] = PALETTE[color]
    return node


def group_node(stem, name, label, x, y, width, height, color="dim"):
    return {"id": stable_id(stem, "group", name), "type": "group",
            "label": label, "x": round(x), "y": round(y),
            "width": round(width), "height": round(height),
            "color": PALETTE[color]}


def render(stem):
    source = graph_spec(stem)
    portrait = stem.startswith("03")
    board_width, board_height = (1080, 1920) if portrait else (1920, 1080)
    area = (55, 140, 970, 1410) if portrait else (65, 130, 1790, 660)
    left, top, available_width, available_height = area
    gx0, gy0, gx1, gy1 = map(float, source["bb"].split(","))
    graph_width, graph_height = gx1 - gx0, gy1 - gy0
    scale = min(available_width / graph_width, available_height / graph_height)
    origin_x = left + (available_width - graph_width * scale) / 2
    origin_y = top + (available_height - graph_height * scale) / 2

    def xy(dot_x, dot_y):
        return (origin_x + (dot_x - gx0) * scale,
                origin_y + (gy1 - dot_y) * scale)

    nodes = [group_node(stem, "board", source.get("label", stem),
                        0, 0, board_width, board_height)]
    for item in source["objects"]:
        if not item["name"].startswith("cluster_"):
            continue
        x0, y0, x1, y1 = map(float, item["bb"].split(","))
        x, y = xy(x0, y1)
        color = {"cluster_ui": "blue", "cluster_services": "green",
                 "cluster_local": "orange", "cluster_external": "dim"}.get(item["name"], "dim")
        nodes.append(group_node(stem, item["name"], item["label"],
                                x, y, (x1 - x0) * scale, (y1 - y0) * scale, color))

    title = source.get("label", stem).replace(" | ", " — ")
    nodes.append(text_node(stem, "title", f"# {title}",
                           44, 45, board_width - 88, 65, "cyan"))
    by_gvid = {}
    for item in source["objects"]:
        if item["name"].startswith("cluster_"):
            continue
        center_x, center_y = map(float, item["pos"].split(","))
        x, y = xy(center_x, center_y)
        width = max(140, float(item["width"]) * 72 * scale + 16)
        height = max(78, float(item["height"]) * 72 * scale + 14)
        lines = item["label"].split("\n")
        content = "**" + lines[0] + "**"
        if len(lines) > 1:
            content += "\n" + "\n".join(lines[1:])
        category = SOURCE_COLORS[item.get("fillcolor", "#DCEAF5")]
        node = text_node(stem, item["name"], content, x - width / 2, y - height / 2,
                         width, height, category)
        nodes.append(node)
        by_gvid[item["_gvid"]] = node

    note_y = 1585 if portrait else 830
    note_height = 75 if portrait else 60
    legend_top = 1725 if portrait else 950
    nodes.append(text_node(stem, "note", "**How to read**  " + NOTES[stem],
                           52, note_y, board_width - 104, note_height, "cyan"))
    nodes.append(text_node(stem, "legend-title", "## Color legend",
                           52, legend_top - 55, board_width - 104, 45))
    columns = 2 if portrait else 3
    cell_width = (board_width - 104) / columns
    for index, (color, label) in enumerate(LEGENDS[stem]):
        column, row = index % columns, index // columns
        nodes.append(text_node(stem, f"legend-{index}", label,
                               52 + column * cell_width,
                               legend_top + row * (65 if portrait else 60),
                               cell_width - 20, 50, color))

    edges = []
    for index, item in enumerate(source["edges"]):
        a, b = by_gvid[item["tail"]], by_gvid[item["head"]]
        from_x = a["x"] + a["width"] / 2
        from_y = a["y"] + a["height"] / 2
        to_x = b["x"] + b["width"] / 2
        to_y = b["y"] + b["height"] / 2
        dx, dy = to_x - from_x, to_y - from_y
        if abs(dy) >= abs(dx) * .7:
            from_side, to_side = (("bottom", "top") if dy >= 0 else ("top", "bottom"))
        else:
            from_side, to_side = (("right", "left") if dx >= 0 else ("left", "right"))
        edge = {"id": stable_id(stem, "edge", index),
                "fromNode": a["id"], "fromSide": from_side,
                "toNode": b["id"], "toSide": to_side,
                "color": PALETTE["blue"]}
        if item.get("dir") == "both":
            edge["fromEnd"] = "arrow"
        label = item.get("label", "").replace("\n", " ").strip()
        if item.get("style") in ("dashed", "dotted"):
            qualifier = "schema" if item["style"] == "dotted" else "reference / optional"
            label = f"{qualifier}: {label}" if label else qualifier
        if label:
            edge["label"] = label
        edges.append(edge)

    OUTPUT.mkdir(exist_ok=True)
    path = OUTPUT / f"{stem}.canvas"
    path.write_text(json.dumps({"nodes": nodes, "edges": edges}, indent=2,
                               ensure_ascii=False) + "\n")
    print(f"{path.relative_to(ROOT)}: {len(nodes)} nodes, {len(edges)} edges")


if __name__ == "__main__":
    for name in STEMS:
        render(name)
