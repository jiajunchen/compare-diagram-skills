"""Build interactive HTML/Markdown from the reviewed architecture diagram source.

Uses the installed architecture-diagram skill template. No Python packages are
required beyond the ignored workspace .venv interpreter and system Graphviz.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


import html
import json
from pathlib import Path
import re
import subprocess


ROOT = FIGURES
TEMPLATE = ROOT.parent / ".agents/skills/architecture-diagram/assets/template.html"
OUTPUT = ROOT / "interactive"
ROLE_BY_COLOR = {
    "#DCEAF5": ("user", "UI / view"),
    "#ECE4F5": ("orch", "Workflow model"),
    "#DDF0E5": ("compute", "On-device service / media"),
    "#FFF0D6": ("vector", "Device-local state / decision"),
    "#EFF2F4": ("seed", "Person / Apple service"),
    "#FBE4E1": ("embed", "Failure / deletion"),
}
ROLE_CSS = {"user": "--c-user", "orch": "--c-orch",
            "compute": "--c-compute", "vector": "--c-vector",
            "seed": "--c-seed", "embed": "--c-embed"}


def flow(name, note, *steps, mode=None):
    return {"name": name, "note": note, "mode": mode, "steps": steps}


SPECS = {
    "01_architecture": {
        "title": "Overall codebase architecture", "tagline": "Data flows",
        "subtitle": "Trace SwiftUI actions through on-device services, SwiftData, Photos, and private CloudKit.",
        "order": "user root views vm review schedule drafts repo import photos editing files upload cloud play".split(),
        "flows": [
            flow("Launch and local state", "Root wiring, local load, and first screen.",
                 ("root", "vm", "load / refresh"), ("vm", "repo", "fetch records"),
                 ("user", "views", "open app"), ("views", "vm", "observed state")),
            flow("Schedule extraction", "Drafts stay in memory until confirmation.",
                 ("views", "review", "Import Schedule"), ("review", "schedule", "extract"),
                 ("review", "drafts", "temporary proposal"),
                 ("review", "vm", "confirm drafts"), ("vm", "repo", "insert bouts")),
            flow("Import recordings", "Original videos remain in Photos.",
                 ("views", "vm", "import action"), ("vm", "import", "prepare / confirm"),
                 ("import", "photos", "read video + IDs"),
                 ("import", "repo", "source links")),
            flow("Create and upload clip", "Export locally, then sync metadata and edited CKAsset.",
                 ("views", "vm", "trim selection"), ("vm", "editing", "trim / export"),
                 ("editing", "files", "local clip"),
                 ("editing", "repo", "clip status"),
                 ("vm", "upload", "sync / retry"),
                 ("upload", "cloud", "metadata + CKAsset"),
                 ("upload", "repo", "sync state"), mode="online"),
            flow("Play and cache", "Use a local export or managed cache; download if needed.",
                 ("views", "play", "player controls"),
                 ("vm", "play", "clip URL / unload"),
                 ("play", "files", "cache / replay"),
                 ("play", "cloud", "download clip"), mode="online"),
        ],
    },
    "02a_entities": {
        "title": "Entity relationships", "tagline": "UUID links",
        "subtitle": "Follow persisted identifiers, Photos references, and CloudKit assets. These are relationships, not runtime calls.",
        "order": "settings tournament bout run source clip photo asset".split(),
        "flows": [
            flow("Tournament records", "One tournament owns ordered bouts and linked recordings.",
                 ("settings", "tournament", "fencer name"),
                 ("tournament", "bout", "1 to many"),
                 ("bout", "source", "1 to many"),
                 ("source", "clip", "1 to many")),
            flow("Direct UUID references", "Links are ID fields, not SwiftData @Relationship properties.",
                 ("tournament", "source", "tournamentID"),
                 ("bout", "clip", "boutID")),
            flow("Photos original", "SourceRecording stores identifiers for an external original.",
                 ("source", "photo", "Photos asset IDs")),
            flow("Cloud clip asset", "Edited review clip points to its private CloudKit asset.",
                 ("clip", "asset", "cloudAssetRecordName"), mode="online"),
            flow("Schema-only run", "ScheduleExtractionRun is modeled but has no production insertion path.",
                 ("tournament", "run", "schema reference")),
        ],
    },
    "02b_object_calls": {
        "title": "Object call map", "tagline": "Principal methods",
        "subtitle": "Explore production cross-component calls. The function index documents private helpers and framework callbacks.",
        "order": "entry ui vm review schedule bout photos clip editor repo queue cloud assets ck download player".split(),
        "flows": [
            flow("Launch", "App composition, UI, and local read.",
                 ("entry", "ui", "AppRootView"),
                 ("ui", "vm", "load"), ("vm", "repo", "fetch")),
            flow("Schedule confirmation", "Recognize and review before any bout insert.",
                 ("ui", "review", "extract"),
                 ("review", "schedule", "recognize / parse / reconcile"),
                 ("review", "vm", "confirmed drafts"),
                 ("vm", "repo", "insert / saveChanges")),
            flow("Recording and clip", "Prepare Photos links, then export a trimmed clip.",
                 ("ui", "vm", "prepare / confirm"),
                 ("vm", "bout", "import coordinator"),
                 ("bout", "photos", "videoAsset / IDs"),
                 ("bout", "repo", "source links"),
                 ("vm", "clip", "createClip"),
                 ("clip", "editor", "export"),
                 ("clip", "repo", "clip status")),
            flow("Cloud synchronization", "Confirmed metadata and edited clip asset only.",
                 ("vm", "queue", "upload / retry"),
                 ("queue", "cloud", "synchronize"),
                 ("cloud", "repo", "apply records"),
                 ("queue", "assets", "saveExportedClip"),
                 ("assets", "ck", "CKAsset"), mode="online"),
            flow("Playback download", "Resolve clip URL for the player queue.",
                 ("ui", "player", "playback controls"),
                 ("vm", "download", "playableURL"),
                 ("download", "assets", "downloadClip"),
                 ("assets", "ck", "private asset"), mode="online"),
        ],
    },
    "03a_organization_pathways": {
        "title": "Organization pathways", "tagline": "Launch to bout",
        "subtitle": "Step through first launch, tournament creation, and manual or screenshot schedule entry.",
        "order": "launch boot load settings first nav new save detail import manual ocr review confirm bout".split(),
        "flows": [
            flow("First launch", "Local settings missing; save the fencer name.",
                 ("launch", "boot", "wire services"),
                 ("boot", "load", "load"), ("load", "settings", "check settings"),
                 ("settings", "first", "no"), ("first", "nav", "save name")),
            flow("Returning launch", "Existing local settings open navigation.",
                 ("launch", "boot", "wire services"),
                 ("boot", "load", "load"), ("load", "settings", "check settings"),
                 ("settings", "nav", "yes")),
            flow("Create tournament", "Save one Tournament record before importing bouts.",
                 ("nav", "new", "New Tournament"),
                 ("new", "save", "validate / insert"),
                 ("save", "detail", "open detail")),
            flow("Manual schedule", "Manual drafts use full-order bout numbers.",
                 ("detail", "import", "Import Schedule"),
                 ("import", "manual", "manual"),
                 ("manual", "review", "edit drafts"),
                 ("review", "confirm", "confirm"),
                 ("confirm", "bout", "open bout")),
            flow("Screenshot schedule", "Vision and parser produce editable source-backed proposals.",
                 ("detail", "import", "Import Schedule"),
                 ("import", "ocr", "screenshots"),
                 ("ocr", "review", "edit drafts"),
                 ("review", "confirm", "confirm"),
                 ("confirm", "bout", "open bout")),
        ],
    },
    "03b_media_pathways": {
        "title": "Media pathways", "tagline": "Original to replay",
        "subtitle": "Track Photos links, trim/export, private asset upload, playback, retry, and cleanup.",
        "order": "bout pick prepare confirm timeline asset trim upload fail play local download player offload delete".split(),
        "flows": [
            flow("Import recordings", "Selections are reviewed before SourceRecording links are inserted.",
                 ("bout", "pick", "PhotosPicker"),
                 ("pick", "prepare", "prepareSelections"),
                 ("prepare", "confirm", "Add to Bout"),
                 ("confirm", "timeline", "load sources")),
            flow("Trim and upload", "Export locally first; upload confirmed edited clip.",
                 ("timeline", "asset", "open source"),
                 ("asset", "trim", "select range"),
                 ("trim", "upload", "export success"),
                 ("upload", "play", "available"), mode="online"),
            flow("Retry a failure", "Status is retained for export or cloud retry.",
                 ("trim", "fail", "export failure"),
                 ("fail", "upload", "retry"),
                 ("upload", "play", "available"), mode="online"),
            flow("Local playback", "A local export or managed cache plays without a fresh download.",
                 ("play", "local", "resolve URL"),
                 ("local", "player", "yes"),
                 ("player", "offload", "optional cleanup")),
            flow("Cloud playback", "Download edited clip when local media is unavailable.",
                 ("play", "local", "resolve URL"),
                 ("local", "download", "no"),
                 ("download", "player", "cached URL"), mode="online"),
            flow("Delete safely", "Cloud asset deletion precedes local record cleanup; Photos original remains.",
                 ("timeline", "delete", "delete action")),
        ],
    },
}


def source(stem):
    document = json.loads(subprocess.check_output(
        ["dot", "-Tjson", str(ROOT / "graphviz" / f"{stem}.gv")]))
    nodes = {item["name"]: item for item in document["objects"]
             if not item["name"].startswith("cluster_")}
    return document, nodes


def replace_between(page, before, after, new):
    start = page.index(before)
    end = page.index(after, start)
    return page[:start] + new + page[end:]


def node_html(item, x, y, online_only=False):
    color = item.get("fillcolor", "#DCEAF5")
    role, category = ROLE_BY_COLOR[color]
    lines = item["label"].split("\n")
    label = html.escape(lines[0])
    detail = html.escape(" · ".join(lines[1:])[:72])
    title = html.escape(item["label"].replace("\n", " | "), quote=True)
    mode = ' data-modes="online"' if online_only else ""
    return (f'<div class="node" data-role="{role}" data-id="{item["name"]}"'
            f'{mode} title="{title}" style="left:{x}%;top:{y}%">'
            f'<div class="label">{label}</div><div class="tech">{detail}</div>'
            f'<div class="port">{html.escape(category)}</div>'
            '<span class="step-badge">·</span></div>')


def build(stem, spec):
    document, nodes = source(stem)
    assert set(spec["order"]) == set(nodes), stem
    portrait = stem.startswith("03")
    cols = 3 if portrait else 4
    xs = [2, 35, 68] if portrait else [2, 26, 50, 74]
    ys = [2, 21, 40, 59, 78] if portrait else [2, 26, 50, 74]
    node_markup = []
    for i, key in enumerate(spec["order"]):
        node_markup.append(node_html(nodes[key], xs[i % cols], ys[i // cols],
                                     key in ("cloud", "ck", "asset") and stem != "03b_media_pathways"))

    flows_js = {}
    tabs = []
    markdown = [f'# {spec["title"]}', '', spec["subtitle"], '',
                'The source is the reviewed production-code analysis. Select a flow in the HTML to step through it. '
                'The Local only / iCloud available toggle reflects whether cloud-dependent steps can run.', '',
                '## Components', '']
    for key in spec["order"]:
        item = nodes[key]
        markdown.append(f'- **{item["label"].split(chr(10))[0]}** (`{key}`): '
                        + item["label"].replace("\n", "; "))
    markdown.extend(['', '## Flows', ''])
    for index, f in enumerate(spec["flows"]):
        flow_key = f"flow_{chr(97 + index)}"
        tabs.append(f'<button class="flowtab" data-flow="{flow_key}" aria-pressed="'
                    f'{"true" if index == 0 else "false"}"><span class="num">{index + 1}</span> '
                    f'{html.escape(f["name"])}</button>')
        steps = []
        markdown.extend([f'### {f["name"]}', '', f["note"], ''])
        for step_index, (a, b, action) in enumerate(f["steps"], 1):
            assert a in nodes and b in nodes, (stem, a, b)
            a_name = nodes[a]["label"].split("\n")[0]
            b_name = nodes[b]["label"].split("\n")[0]
            role = ROLE_BY_COLOR[nodes[b].get("fillcolor", "#DCEAF5")][0]
            target_detail = nodes[b]["label"].replace("\n", "; ")
            steps.append({"from": a, "to": b, "color": ROLE_CSS[role],
                          "title": action[0].upper() + action[1:],
                          "route": action,
                          "desc": f"{a_name} → {b_name}. {target_detail}",
                          "payload": f"{a_name}\n  -- {action} -->\n{b_name}",
                          "chips": ["Local" if not f["mode"] else "Private CloudKit"]})
            markdown.append(f'{step_index}. **{a_name} → {b_name}:** {action}.')
        markdown.append('')
        flows_js[flow_key] = {"name": f["name"], "note": f["note"],
                              **({"onlyMode": f["mode"]} if f["mode"] else {}),
                              "steps": steps}
    markdown.extend(['## Scope notes', '',
                     '- The entity page shows UUID references; its steps are relationship traversal, not method calls.',
                     '- The object-call page shows principal production calls. See [CALL_INDEX.md](../CALL_INDEX.md) for all function declarations.',
                     '- Photos originals are external. CloudKit stores confirmed metadata and edited review clips.',
                     '- Schema-only ScheduleExtractionRun has no production insertion call.', ''])

    page = TEMPLATE.read_text()
    page = re.sub(r'<link rel="preconnect"[^>]+>\n', '', page)
    page = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]+>\n', '', page)
    page = re.sub(r'<noscript><link[^>]+></noscript>\n', '', page)
    labels = {"{{SYSTEM_NAME}}": spec["title"], "{{PROJECT_LABEL}}": "Fencing Video Analysis · MVP",
              "{{TAGLINE}}": spec["tagline"], "{{SUBTITLE}}": spec["subtitle"]}
    for token, value in labels.items():
        page = page.replace(token, html.escape(value))
    mode_markup = ('<div class="modepick" role="group" aria-label="iCloud availability">'
                   '<button data-mode="offline" aria-pressed="true">Local only <span class="pill">device</span></button>'
                   '<button data-mode="online" aria-pressed="false">iCloud available <span class="pill">private</span></button>'
                   '</div>\n')
    page = replace_between(page, '  <div class="modepick" role="group"', '  <!-- 3. Legend.', '  ' + mode_markup + '\n')
    used_roles = {ROLE_BY_COLOR[nodes[key].get("fillcolor", "#DCEAF5")][0]
                  for key in spec["order"]}
    role_names = {"user": "UI / view", "orch": "Workflow model", "compute": "Processing",
                  "vector": "Local state", "seed": "Person / Apple", "embed": "Failure / deletion"}
    legend = '<div class="legend" aria-label="Component legend">\n' + '\n'.join(
        f'<span class="item"><span class="swatch" style="background:var({ROLE_CSS[r]})"></span> '
        f'{role_names[r]}</span>' for r in ROLE_CSS if r in used_roles) + '\n</div>\n'
    page = replace_between(page, '  <div class="legend" aria-label="Component legend">',
                           '  <!-- 3b. Theme toggle', '  ' + legend + '\n')
    page = replace_between(page, '<nav class="flowtabs" aria-label="Scenarios">',
                           '<p class="scenario-note">',
                           '<nav class="flowtabs" aria-label="Scenarios">\n' + '\n'.join(tabs) + '</nav>\n\n')
    page = page.replace('<kbd id="kbFlowMax">3</kbd>', f'<kbd id="kbFlowMax">{len(tabs)}</kbd>')
    page = replace_between(page, '      <!-- User / client / browser -->',
                           '      <!-- SVG wires, drawn after nodes',
                           '      ' + '\n      '.join(node_markup) + '\n\n')
    encoded = json.dumps(flows_js, ensure_ascii=False, indent=2).replace('</script>', '<\\/script>')
    page = replace_between(page, 'const flows = {', '/* ─── state',
                           f'const flows = {encoded};\n\n')
    page = re.sub(r'keyboardFlowOrder: \[[^\]]+\]',
                  'keyboardFlowOrder: ' + json.dumps(list(flows_js)), page)
    size = ('630px', '1120px') if portrait else ('896px', '504px')
    page = page.replace('height: 460px;', f'height: {size[1]}; width: {size[0]}; max-width: none; margin: 0 auto;')
    page = page.replace('overflow: hidden;\n  }\n  .canvas::before',
                        'overflow: auto;\n  }\n  .canvas::before')
    page = page.replace('min-height: 540px;', f'min-height: {int(size[1][:-2]) + 100}px;')
    # The installed template supplies the layering fix; only the dimensions
    # are specialized for this project's 16:9 and 9:16 canvases.
    assert 'body.diagram-fullscreen main{ z-index:10000; }' in page
    assert 'document.body.classList.toggle("diagram-fullscreen"' in page
    fullscreen_stage = (
        '  .canvas.is-fullscreen .stage{ width:min(100%, 700px); min-width:630px; '
        'height:auto; aspect-ratio:9/16; }' if portrait else
        '  .canvas.is-fullscreen .stage{ width:min(100%, 1280px); min-width:896px; '
        'height:auto; aspect-ratio:16/9; }')
    page, replacements = re.subn(r'  \.canvas\.is-fullscreen \.stage\{[^}]+\}',
                                 fullscreen_stage, page, count=1)
    assert replacements == 1
    page = page.replace('</style>', '''
  /* Compact cards keep all nodes within the requested 16:9 / 9:16 canvas. */
  .node { height: 108px; padding: 9px 11px; overflow: hidden; }
  .node .label { display: -webkit-box; -webkit-box-orient: vertical;
    -webkit-line-clamp: 2; overflow: hidden; font-size: 12px; line-height: 1.2; }
  .node .tech { display: -webkit-box; -webkit-box-orient: vertical;
    -webkit-line-clamp: 2; overflow: hidden; font-size: 9px; }
  .node .port { margin-top: 4px; font-size: 9px; }
</style>''')
    assert '{{' not in page, stem
    assert all(f'data-id="{key}"' in page for key in nodes)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / f'{stem}.html').write_text(page)
    (OUTPUT / f'{stem}.md').write_text('\n'.join(markdown))


if __name__ == '__main__':
    assert TEMPLATE.is_file(), TEMPLATE
    for name, config in SPECS.items():
        build(name, config)
        print('Generated interactive', name)
