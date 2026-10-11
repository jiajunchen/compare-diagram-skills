"""Rebuild the five reviewed figures with Diagrams and local PlantUML.

Run from the repository root with .venv/bin/python. The original DOT files are
the reviewed semantic source; each backend creates its own layout and artwork.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

from diagrams import Cluster, Diagram, Edge
from diagrams.generic.blank import Blank
import plantuml

from generate_diagrams import (BLUE, GRAY, GREEN, NAVY, ORANGE, PURPLE, RED,
                               SVG_NS, add_text, svg_element)


ROOT = FIGURES
JAR = ROOT.parent / ".venv/tools/plantuml.jar"
STEMS = (
    "01_architecture", "02a_entities", "02b_object_calls",
    "03a_organization_pathways", "03b_media_pathways",
)
LEGENDS = {
    STEMS[0]: [(BLUE, "SwiftUI views"), (PURPLE, "View models"),
               (GREEN, "On-device services"), (ORANGE, "Device-local state"),
               (GRAY, "Person / Apple services")],
    STEMS[1]: [(PURPLE, "App settings"), (BLUE, "Tournament / bout"),
               (GREEN, "Media records"), (ORANGE, "Schema-only run"),
               (GRAY, "Apple media assets")],
    STEMS[2]: [(GRAY, "Entry / Apple frameworks"), (BLUE, "UI and review state"),
               (PURPLE, "Workflow orchestration"), (GREEN, "Application services"),
               (ORANGE, "Local repository")],
    STEMS[3]: [(GRAY, "User entry"), (BLUE, "UI action / screen"),
               (GREEN, "On-device processing"), (ORANGE, "Decision")],
    STEMS[4]: [(GRAY, "User entry"), (BLUE, "UI action / screen"),
               (GREEN, "On-device processing"), (PURPLE, "Cloud upload"),
               (ORANGE, "Decision / local cleanup"), (RED, "Failure / deletion")],
}

# Diagram Creator's default dark theme. Keep the semantic labels above while
# using its accent colors for PlantUML borders and legend swatches.
PLANTUML_THEME = {
    "background": "#0a0e1a", "panel": "#0f1528",
    "border": "#1e2d4a", "text": "#c8d8f0",
    "dim": "#4a6080",
    "blue": "#2d7aff", "cyan": "#00d4ff", "green": "#00e5a0",
    "orange": "#ff8c42", "red": "#ff4d6a",
}
PLANTUML_ACCENTS = {
    BLUE: PLANTUML_THEME["blue"],
    PURPLE: PLANTUML_THEME["cyan"],
    GREEN: PLANTUML_THEME["green"],
    ORANGE: PLANTUML_THEME["orange"],
    GRAY: PLANTUML_THEME["dim"],
    RED: PLANTUML_THEME["red"],
}
PLANTUML_ROLES = {
    BLUE: "blue", PURPLE: "cyan", GREEN: "green",
    ORANGE: "orange", GRAY: "dim", RED: "red",
}


def legend_items(stem, renderer):
    items = LEGENDS[stem]
    if renderer == "plantuml":
        return [(PLANTUML_ACCENTS[color], label) for color, label in items]
    return items


class Box(Blank):
    """Diagrams node with a compact labeled box instead of a provider icon."""

    _icon = None


def specification(stem):
    data = json.loads(subprocess.check_output(
        ["dot", "-Tjson", str(ROOT / "graphviz" / f"{stem}.gv")]))
    objects = data["objects"]
    nodes = [item for item in objects if not item["name"].startswith("cluster_")]
    by_id = {item["_gvid"]: item for item in nodes}
    clusters = [item for item in objects if item["name"].startswith("cluster_")]
    return data, nodes, by_id, clusters


def save_page(raw_svg, path, stem, renderer="diagrams_library"):
    """Place independently rendered art on the requested ratio with a legend."""
    art = ET.fromstring(raw_svg)
    box = art.attrib.get("viewBox")
    if box:
        x, y, art_width, art_height = map(float, box.split())
    else:
        x = y = 0.0
        art_width = float(art.attrib["width"].replace("pt", ""))
        art_height = float(art.attrib["height"].replace("pt", ""))
        art.set("viewBox", f"0 0 {art_width} {art_height}")
    portrait = stem.startswith("03")
    width, height = (1080, 1920) if portrait else (1920, 1080)
    legend_top = 1680 if portrait else 900
    margin = 42
    scale = min((width - 2 * margin) / art_width,
                (legend_top - 2 * margin) / art_height)
    dx = (width - art_width * scale) / 2 - x * scale
    dy = margin + (legend_top - 2 * margin - art_height * scale) / 2 - y * scale
    page = svg_element("svg", width=str(width), height=str(height),
                       viewBox=f"0 0 {width} {height}", version="1.1")
    dark = renderer == "plantuml"
    text_color = PLANTUML_THEME["text"] if dark else NAVY
    border_color = PLANTUML_THEME["border"] if dark else "#8AA4B8"
    page.append(svg_element("rect", x="0", y="0", width=str(width),
                            height=str(height),
                            fill=PLANTUML_THEME["background"] if dark else "white"))
    drawing = ET.SubElement(page, f"{{{SVG_NS}}}g", {
        "transform": f"translate({dx:.3f} {dy:.3f}) scale({scale:.6f})",
        "aria-label": f"{stem} alternative diagram",
    })
    drawing.extend(list(art))
    page.append(svg_element("line", x1="42", y1=str(legend_top),
                            x2=str(width - 42), y2=str(legend_top),
                            stroke=border_color, **{"stroke-width": "2"}))
    if dark:
        ET.SubElement(page, f"{{{SVG_NS}}}text", {
            "x": "52", "y": str(legend_top + 35), "fill": text_color,
            "font-family": "Helvetica", "font-size": "22", "font-weight": "bold",
        }).text = "Color legend"
    else:
        add_text(page, 52, legend_top + 35, "Color legend", size=22, weight="bold")
    columns = 2 if portrait else 3
    col_width = (width - 100) / columns
    for index, (color, label) in enumerate(legend_items(stem, renderer)):
        col = index % columns
        row = index // columns
        px = 52 + col * col_width
        py = legend_top + 73 + row * (57 if portrait else 48)
        page.append(svg_element("rect", x=f"{px:.1f}", y=str(py - 22),
                                width="31", height="27", rx="5", fill=color,
                                stroke=border_color if dark else NAVY,
                                **{"stroke-width": "1.5"}))
        if dark:
            ET.SubElement(page, f"{{{SVG_NS}}}text", {
                "x": f"{px + 44:.1f}", "y": str(py), "fill": text_color,
                "font-family": "Helvetica", "font-size": "18",
            }).text = label
        else:
            add_text(page, px + 44, py, label, size=18)
    ET.ElementTree(page).write(path, encoding="utf-8", xml_declaration=True)
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o",
                    str(path.with_suffix(".pdf")), str(path)], check=True)
    subprocess.run(["rsvg-convert", "-f", "png", "-o",
                    str(path.with_suffix(".png")), str(path)], check=True)


def diagrams_version(stem):
    data, nodes, by_id, clusters = specification(stem)
    output = ROOT / "diagrams_library"
    output.mkdir(exist_ok=True)
    portrait = stem.startswith("03")
    direction = "TB" if portrait or stem != "01_architecture" else "LR"
    graph_attr = {"bgcolor": "white", "pad": "0.2", "nodesep": "0.3",
                  "ranksep": "0.55", "fontname": "Helvetica", "fontsize": "18",
                  "fontcolor": NAVY, "splines": "polyline"}
    node_attr = {"shape": "box", "style": "rounded,filled", "color": NAVY,
                 "fontname": "Helvetica", "fontcolor": NAVY,
                 "fontsize": "11", "margin": "0.14,0.1",
                 "fixedsize": "false", "width": "0", "height": "0",
                 "labelloc": "c"}
    edge_attr = {"color": "#526779", "fontname": "Helvetica",
                 "fontcolor": NAVY, "fontsize": "9"}
    filename = output / f"{stem}_raw"
    with Diagram(data.get("label", stem), filename=str(filename),
                 direction=direction, outformat="svg", show=False,
                 graph_attr=graph_attr, node_attr=node_attr,
                 edge_attr=edge_attr) as diagram:
        objects = {}
        grouped = set()
        for cluster in clusters:
            with Cluster(cluster["label"]):
                for gvid in cluster.get("nodes", []):
                    item = by_id[gvid]
                    objects[gvid] = Box(item["label"], nodeid=item["name"],
                                        fillcolor=item.get("fillcolor", BLUE),
                                        shape=item.get("shape", "box"))
                    grouped.add(gvid)
        for item in nodes:
            if item["_gvid"] not in grouped:
                objects[item["_gvid"]] = Box(
                    item["label"], nodeid=item["name"],
                    fillcolor=item.get("fillcolor", BLUE),
                    shape=item.get("shape", "box"))
        for link in data["edges"]:
            opts = {"label": link.get("label", "")}
            if link.get("style") in ("dashed", "dotted"):
                opts["style"] = link["style"]
            objects[link["tail"]] >> Edge(**opts) >> objects[link["head"]]
    raw_path = filename.with_suffix(".svg")
    save_page(raw_path.read_bytes(), output / f"{stem}.svg", stem)
    raw_path.unlink()


def plantuml_version(stem):
    data, nodes, by_id, clusters = specification(stem)
    output = ROOT / "plantuml"
    output.mkdir(exist_ok=True)
    theme = PLANTUML_THEME
    lines = ["@startuml", "!pragma layout smetana",
             f"skinparam backgroundColor {theme['background']}",
             "skinparam shadowing false", "skinparam defaultFontName Helvetica",
             f"skinparam defaultFontColor {theme['text']}",
             f"skinparam ArrowColor {theme['blue']}",
             f"skinparam ArrowFontColor {theme['text']}",
             f"skinparam TitleFontColor {theme['text']}",
             f"skinparam packageBackgroundColor {theme['panel']}",
             f"skinparam packageBorderColor {theme['border']}",
             f"skinparam packageFontColor {theme['text']}",
             f"skinparam rectangleBackgroundColor {theme['panel']}",
             f"skinparam rectangleFontColor {theme['text']}",
             f"skinparam classBackgroundColor {theme['panel']}",
             f"skinparam classFontColor {theme['text']}",
             "skinparam RoundCorner 12", "skinparam linetype polyline",
             "hide stereotype", "hide circle",
             f"title {data.get('label', stem)}"]
    for role in ("blue", "cyan", "green", "orange", "red", "dim"):
        for kind in ("rectangle", "class"):
            lines.extend([
                f"skinparam {kind}<<theme_{role}>> {{",
                f"  BackgroundColor {theme['panel']}",
                f"  BorderColor {theme[role]}",
                f"  FontColor {theme['text']}",
                "}",
            ])
    grouped = set()

    def add_item(item):
        # The Python plantuml package encodes the same source for validation;
        # local jar execution renders it without sending source to a server.
        label = item["label"].replace("\n", "\\n").replace('"', "'")
        role = PLANTUML_ROLES[item.get("fillcolor", BLUE)]
        kind = "class" if stem == "02a_entities" else "rectangle"
        lines.append(f'{kind} "{label}" as {item["name"]} <<theme_{role}>>')

    for cluster in clusters:
        lines.append(f'package "{cluster["label"]}" {{')
        for gvid in cluster.get("nodes", []):
            add_item(by_id[gvid])
            grouped.add(gvid)
        lines.append("}")
    for item in nodes:
        if item["_gvid"] not in grouped:
            add_item(item)
    for link in data["edges"]:
        tail = by_id[link["tail"]]["name"]
        head = by_id[link["head"]]["name"]
        arrow = "..>" if link.get("style") in ("dashed", "dotted") else "-->"
        label = link.get("label", "").replace("\n", " ").replace(":", "-")
        lines.append(f"{tail} {arrow} {head}" + (f" : {label}" if label else ""))
    lines.append("@enduml")
    source = "\n".join(lines) + "\n"
    (output / f"{stem}.puml").write_text(source)
    encoded = plantuml.deflate_and_encode(source)
    assert encoded and len(encoded) > 10
    render = subprocess.run(["java", "-jar", str(JAR), "--svg", "-pipe"],
                            input=source.encode(), capture_output=True, check=True)
    if b"Syntax Error" in render.stdout:
        raise ValueError(f"PlantUML syntax error in {stem}")
    save_page(render.stdout, output / f"{stem}.svg", stem, renderer="plantuml")


if __name__ == "__main__":
    if not JAR.is_file():
        raise SystemExit(f"Install the local PlantUML jar at {JAR} first")
    for name in STEMS:
        print("Rendering", name, flush=True)
        diagrams_version(name)
        plantuml_version(name)
