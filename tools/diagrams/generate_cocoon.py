"""Render the reviewed diagrams with Cocoon AI's HTML/SVG skill template.

All Python work stays in the ignored workspace environment. DOT files are the
reviewed source of nodes, links, and layout; this script applies Cocoon's
component style and preserves its HTML export toolbar and summary cards.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import html
from pathlib import Path
import subprocess

from generate_alternatives import STEMS, specification


ROOT = FIGURES
TEMPLATE = ROOT.parent / ".agents/skills/architecture-diagram-generator/resources/template.html"
OUTPUT = ROOT / "cocoon_generator"
PALETTE = {
    "frontend": ("rgba(8, 51, 68, 0.4)", "#22d3ee", "Frontend / UI"),
    "backend": ("rgba(6, 78, 59, 0.4)", "#34d399", "Models / services"),
    "database": ("rgba(76, 29, 149, 0.4)", "#a78bfa", "Local state"),
    "cloud": ("rgba(120, 53, 15, 0.3)", "#fbbf24", "Private cloud"),
    "external": ("rgba(30, 41, 59, 0.5)", "#94a3b8", "Person / Apple"),
    "attention": ("rgba(136, 19, 55, 0.4)", "#fb7185", "Failure / deletion"),
    "schema": ("rgba(251, 146, 60, 0.3)", "#fb923c", "Schema-only"),
}
TYPE_BY_OLD_COLOR = {
    "#DCEAF5": "frontend", "#ECE4F5": "backend",
    "#DDF0E5": "backend", "#FFF0D6": "database",
    "#EFF2F4": "external", "#FBE4E1": "attention",
}
TITLES = {
    STEMS[0]: ("Overall codebase architecture", "SwiftUI, on-device services, SwiftData, Photos, and private CloudKit"),
    STEMS[1]: ("Entity relationships", "Persisted UUID references and external media identifiers"),
    STEMS[2]: ("Object call map", "Principal production cross-component method calls"),
    STEMS[3]: ("Organization pathways", "Launch, tournament creation, and schedule confirmation"),
    STEMS[4]: ("Media pathways", "Recording import, clip export, playback, retry, and cleanup"),
}
CARDS = {
    STEMS[0]: [
        ("One native app", "SwiftUI runs on iPhone and iPad; there is no app-owned backend server."),
        ("Private sync", "SwiftData stores local records. Private CloudKit holds confirmed metadata and edited clips."),
        ("Original videos", "Photos and iCloud Photos keep source originals; the app stores links."),
    ],
    STEMS[1]: [
        ("UUID references", "Entities link through identifier fields rather than SwiftData @Relationship properties."),
        ("External assets", "SourceRecording references Photos; ReviewClip references a private CKAsset."),
        ("Schema-only record", "ScheduleExtractionRun is modeled but has no production insertion path."),
    ],
    STEMS[2]: [
        ("UI commands", "SwiftUI views call AppViewModel and ScheduleReviewViewModel."),
        ("Service calls", "Import, editing, upload, download, and playback use on-device services."),
        ("Method index", "CALL_INDEX.md lists every production Swift function declaration."),
    ],
    STEMS[3]: [
        ("Launch", "Dependencies open SwiftData, then local settings choose setup or navigation."),
        ("Tournament", "The form validates and saves a Tournament before its schedule is confirmed."),
        ("Draft review", "Manual and screenshot drafts are edited before new Bouts are inserted."),
    ],
    STEMS[4]: [
        ("Source originals", "PhotoPicker selections create links; originals stay in Photos."),
        ("Edited clips", "AVFoundation exports a local trim, then private CloudKit stores the edited asset."),
        ("Recovery", "Failures retain retry states; offload and deletion leave Photos originals untouched."),
    ],
}


def element(tag, **attributes):
    args = " ".join(f'{name.replace("_", "-")}="{html.escape(str(value), quote=True)}"'
                    for name, value in attributes.items())
    return f"<{tag} {args}/>"


def text(x, y, value, *, color="#e2e8f0", size=13, weight="400", anchor="middle",
         max_width=None):
    fit = (f' textLength="{max_width:.2f}" lengthAdjust="spacingAndGlyphs"'
           if max_width and len(value) * size * 0.62 > max_width else "")
    return (f'<text x="{x:.2f}" y="{y:.2f}" fill="{color}" font-size="{size:.2f}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{fit}>{html.escape(value)}</text>')


def node_type(item):
    if item["name"] in ("cloud", "asset", "ck"):
        return "cloud"
    if item["name"] == "run":
        return "schema"
    return TYPE_BY_OLD_COLOR[item.get("fillcolor", "#DCEAF5")]


def make_svg(stem):
    data, nodes, by_id, clusters = specification(stem)
    portrait = stem.startswith("03")
    width, height = (1080, 1920) if portrait else (1920, 1080)
    legend_y = 1680 if portrait else 890
    x0, y0, x1, y1 = map(float, data["bb"].split(","))
    gw, gh = x1 - x0, y1 - y0
    scale = min((width - 100) / gw, (legend_y - 125) / gh)
    left = (width - gw * scale) / 2
    top = 70 + (legend_y - 125 - gh * scale) / 2

    def point(x, y):
        return left + (x - x0) * scale, top + (y1 - y) * scale

    defs = ('''<defs>
<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/></marker>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/></pattern>
</defs>''')
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" font-family="JetBrains Mono, Menlo, monospace" aria-label="{html.escape(TITLES[stem][0])}">',
             defs, element("rect", x=0, y=0, width=width, height=height, fill="#020617"),
             element("rect", x=0, y=0, width=width, height=height, fill="url(#grid)"),
             text(50, 40, TITLES[stem][0], color="white", size=25, weight="700", anchor="start")]
    # Logical boundaries are drawn behind the links and components.
    for cluster in clusters:
        cx0, cy0, cx1, cy1 = map(float, cluster["bb"].split(","))
        rx, ry = point(cx0, cy1)
        bx, by = point(cx1, cy0)
        parts.append(element("rect", x=f"{rx:.2f}", y=f"{ry:.2f}",
                             width=f"{bx-rx:.2f}", height=f"{by-ry:.2f}",
                             data_cluster=cluster["name"],
                             rx=12, fill="rgba(30, 41, 59, 0.25)",
                             stroke="#64748b", stroke_width=1.5, stroke_dasharray="8,4"))
        parts.append(text(rx + 13, ry + 23, cluster["label"], color="#cbd5e1",
                          size=15, weight="600", anchor="start"))

    # The source's spline geometry retains every reviewed connection. Draw it
    # before boxes so arrow paths cannot sit on top of component labels.
    for edge in data["edges"]:
        curves = [command["points"] for command in edge.get("_draw_", [])
                  if command["op"] in ("b", "B")]
        if not curves:
            continue
        commands = []
        for curve in curves:
            start_x, start_y = point(*curve[0])
            commands.append(f"M {start_x:.2f} {start_y:.2f}")
            for index in range(1, len(curve), 3):
                section = curve[index:index + 3]
                if len(section) == 3:
                    coords = [point(*pair) for pair in section]
                    commands.append("C " + " ".join(f"{x:.2f} {y:.2f}" for x, y in coords))
        style = edge.get("style", "")
        markers = {"marker_end": "url(#arrowhead)"}
        if edge.get("dir") == "both":
            markers["marker_start"] = "url(#arrowhead)"
        if edge.get("arrowhead") == "none":
            markers.pop("marker_end", None)
        parts.append(element("path", d=" ".join(commands), fill="none",
                             data_edge=f'{by_id[edge["tail"]]["name"]}->{by_id[edge["head"]]["name"]}',
                             stroke="#64748b", stroke_width=f"{max(1.5, 1.4*scale):.2f}",
                             **({"stroke_dasharray": "6,5"} if style in ("dashed", "dotted") else {}),
                             **markers))

    for item in nodes:
        cx, cy = map(float, item["pos"].split(","))
        center_x, center_y = point(cx, cy)
        box_w = float(item["width"]) * 72 * scale
        box_h = float(item["height"]) * 72 * scale
        x, y = center_x - box_w / 2, center_y - box_h / 2
        fill, stroke, _ = PALETTE[node_type(item)]
        parts.append(f'<g data-node="{html.escape(item["name"], quote=True)}"><title>{html.escape(item["label"])}</title>')
        parts.append(element("rect", x=f"{x:.2f}", y=f"{y:.2f}", width=f"{box_w:.2f}",
                             height=f"{box_h:.2f}", rx=7, fill="#0f172a"))
        parts.append(element("rect", x=f"{x:.2f}", y=f"{y:.2f}", width=f"{box_w:.2f}",
                             height=f"{box_h:.2f}", rx=7, fill=fill,
                             stroke=stroke, stroke_width=2))
        lines = item["label"].split("\n")
        max_len = max(len(line) for line in lines)
        font_size = min(18, box_w / max(1, max_len) / 0.60,
                        (box_h - 12) / max(1, len(lines)) / 1.15)
        font_size = max(8, font_size)
        line_h = font_size * 1.18
        first_y = center_y - (len(lines) - 1) * line_h / 2 + font_size * 0.34
        for index, line in enumerate(lines):
            parts.append(text(center_x, first_y + index * line_h, line,
                              color="white" if index == 0 else "#cbd5e1",
                              size=font_size, weight="600" if index == 0 else "400",
                              max_width=box_w - 12))
        parts.append("</g>")

    # Edge labels are placed after nodes at Graphviz's label coordinates.
    for edge in data["edges"]:
        if not edge.get("label") or not edge.get("lp"):
            continue
        lx, ly = map(float, edge["lp"].split(","))
        px, py = point(lx, ly)
        label = edge["label"].replace("\n", " / ")
        fs = min(15, max(10, 8.5 * scale))
        lw = len(label) * fs * 0.61 + 12
        parts.append(element("rect", x=f"{px-lw/2:.2f}", y=f"{py-fs:.2f}",
                             width=f"{lw:.2f}", height=f"{fs+5:.2f}", rx=3,
                             fill="#020617"))
        parts.append(text(px, py, label, color="#cbd5e1", size=fs))

    parts.append(element("line", x1=42, y1=legend_y, x2=width - 42, y2=legend_y,
                         stroke="#334155", stroke_width=2))
    parts.append(text(52, legend_y + 40, "Color legend", color="white", size=23,
                      weight="700", anchor="start"))
    used = list(dict.fromkeys(node_type(item) for item in nodes))
    cols = 2 if portrait else 3
    col_w = (width - 100) / cols
    for index, kind in enumerate(used):
        fill, stroke, label = PALETTE[kind]
        cx = 52 + index % cols * col_w
        cy = legend_y + 86 + index // cols * (66 if portrait else 54)
        parts.append(element("rect", x=f"{cx:.2f}", y=f"{cy-21:.2f}", width=30,
                             height=27, rx=4, fill=fill, stroke=stroke, stroke_width=1.5))
        parts.append(text(cx + 44, cy, label, color="#cbd5e1",
                          size=18, anchor="start"))
    parts.append("</svg>")
    return "\n".join(parts), len(nodes), len(data["edges"])


def make_html(stem, svg):
    title, subtitle = TITLES[stem]
    page = TEMPLATE.read_text()
    page = page.replace("[PROJECT NAME] Architecture Diagram", html.escape(title))
    page = page.replace("[PROJECT NAME] Architecture", html.escape(title))
    page = page.replace("[Subtitle description]", html.escape(subtitle))
    # The template scales the SVG width, but its fixed height attribute would
    # otherwise distort our fixed-ratio artwork in the browser.
    page = page.replace("svg {\n      width: 100%;", "svg {\n      width: 100%;\n      height: auto;")
    start = page.index('<svg viewBox="0 0 1000 680">')
    end = page.index("</svg>", start) + len("</svg>")
    page = page[:start] + svg + page[end:]
    cards = ['    <!-- Info Cards -->', '    <div class="cards">']
    dots = ("cyan", "emerald", "violet")
    for index, (heading, detail) in enumerate(CARDS[stem]):
        cards.append(f'''      <div class="card"><div class="card-header"><div class="card-dot {dots[index]}"></div><h3>{html.escape(heading)}</h3></div><ul><li>{html.escape(detail)}</li></ul></div>''')
    cards.append("    </div>\n\n")
    page = page[:page.index("    <!-- Info Cards -->")] + "\n".join(cards) + page[page.index("    <!-- Footer -->"):]
    page = page.replace("[Project Name] • [Additional metadata]",
                        f"Fencing Video Analysis • source-traced MVP • {html.escape(title)}")
    if stem.startswith("03"):
        page = page.replace("min-width: 900px;", "min-width: 540px; max-width: 650px; margin: 0 auto;")
    assert "[PROJECT NAME]" not in page and "Card Title" not in page
    assert 'id="report-container"' in page and 'id="arrowhead"' in page
    return "\n".join(line.rstrip() for line in page.splitlines()) + "\n"


if __name__ == "__main__":
    if not TEMPLATE.is_file():
        raise SystemExit(f"Install the Cocoon AI skill at {TEMPLATE.parent.parent}")
    OUTPUT.mkdir(exist_ok=True)
    for name in STEMS:
        svg, node_count, edge_count = make_svg(name)
        html_page = make_html(name, svg)
        svg_path = OUTPUT / f"{name}.svg"
        svg_path.write_text(svg)
        (OUTPUT / f"{name}.html").write_text(html_page)
        subprocess.run(["rsvg-convert", "-f", "pdf", "-o",
                        str(OUTPUT / f"{name}.pdf"), str(svg_path)], check=True)
        subprocess.run(["rsvg-convert", "-f", "png", "-o",
                        str(OUTPUT / f"{name}.png"), str(svg_path)], check=True)
        print("Rendered Cocoon", name, node_count, "nodes", edge_count, "edges")
