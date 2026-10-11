"""Render the five source-traced MVP reviews with the diagram-creator design system.

Run with the ignored workspace .venv. Outputs are dependency-free HTML pages.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from html import escape
from pathlib import Path


ROOT = FIGURES
OUT = ROOT / "diagram_creator"


def card(title, detail, color="blue", tag="div"):
    return (f'<{tag} class="node-card accent-{color}" title="{escape(title + " — " + detail, quote=True)}">'
            f'<strong class="node-name">{escape(title)}</strong>'
            f'<span class="node-detail">{escape(detail)}</span></{tag}>')


def layer(title, color, content, note=""):
    return (f'<div class="layer accent-{color}"><div class="layer-label">{escape(title)}</div>'
            f'{content}{f"<p class=layer-note>{escape(note)}</p>" if note else ""}</div>')


def connector(label):
    return f'<div class="connector"><span class="connector-line"></span><span class="connector-label">{escape(label)}</span><span class="arrowhead">▼</span></div>'


def nested():
    ui = '<div class="node-row">' + ''.join([
        card("SwiftUI views", "Tournament · schedule · bout · player", "blue"),
        card("AppViewModel", "load · save · import · play", "cyan"),
        card("ScheduleReviewVM", "editable drafts until confirm", "cyan"),
    ]) + '</div>'
    services = '<div class="node-row">' + ''.join([
        card("Schedule services", "Vision → parser → optional model → validator", "green"),
        card("Import + Photos", "selection review · Photos IDs", "green"),
        card("ClipWorkflow", "trim · AVFoundation export", "green"),
        card("Sync + playback", "CloudKit upload · download · AVPlayer", "green"),
    ]) + '</div>'
    local = '<div class="node-row">' + ''.join([
        card("SwiftData", "confirmed metadata + clip state", "orange"),
        card("App files", "exports + managed cache", "orange"),
        card("In-memory drafts", "unconfirmed schedule proposals", "orange"),
    ]) + '</div>'
    external = '<div class="node-row">' + ''.join([
        card("Photos / iCloud Photos", "original videos · read-only", "red"),
        card("Private CloudKit", "metadata + edited CKAssets", "red"),
    ]) + '</div>'
    return ('<div class="nested">' + layer("User action → native app", "blue", ui)
            + connector("commands + observed state") + layer("On-device application services", "green", services)
            + connector("write confirmed records · read originals · sync edited clips")
            + '<div class="split-layers">' + layer("Device-local", "orange", local)
            + layer("Apple-managed", "red", external) + '</div>'
            + '<p class="callout">No app-owned backend server. Originals stay in Photos; only edited clips become CloudKit assets.</p></div>')


def tree_item(title, detail, color, children=""):
    return f'<li>{card(title, detail, color)}{f"<ul>{children}</ul>" if children else ""}</li>'


def entities():
    photos = tree_item("PHAsset", "external original · device/cloud Photos IDs", "red")
    asset = tree_item("CKRecord + CKAsset", "edited clip · cloudAssetRecordName", "red")
    clip = tree_item("ReviewClip", "boutID + sourceRecordingID · trim · sync status", "green", asset)
    source = tree_item("SourceRecording", "tournamentID + boutID · Photos IDs", "green", photos + clip)
    bout = tree_item("Bout", "tournamentID · phase · opponent · sequence", "blue", source)
    run = tree_item("ScheduleExtractionRun", "tournamentID · schema only; no production insert", "orange")
    tournament = tree_item("Tournament", "name · venue · date · sync state", "blue", bout + run)
    settings = tree_item("AppSettings", "fencer name · stable cloud ID", "cyan")
    return ('<div class="tree"><ul>' + tournament + settings + '</ul></div>'
            '<p class="callout">The branches show logical ownership. SwiftData stores UUID fields, not @Relationship links. '
            'Bout also directly identifies its ReviewClips; Tournament directly identifies SourceRecordings.</p>')


CALLS = [
    ("AppRootView", "AppViewModel.load / refreshCloud", "blue"),
    ("TournamentFormView", "AppViewModel.saveTournament", "blue"),
    ("ScheduleImportView", "ScheduleReviewViewModel.extract / addDraft / moveDraft", "blue"),
    ("ScheduleReviewVM", "Vision recognize → parser → model assist → validator", "green"),
    ("ScheduleImportView", "AppViewModel.confirmSchedule → LocalRepository.insert", "cyan"),
    ("BoutDetailView", "AppViewModel.prepare / confirmRecordings", "blue"),
    ("BoutImportCoordinator", "PhotoLibraryService.importSelections / videoAsset", "green"),
    ("AppViewModel", "ClipWorkflow.createClip → VideoEditingService.export", "cyan"),
    ("ClipWorkflow", "LocalRepository.insert / saveChanges", "orange"),
    ("AppViewModel", "ClipUploadQueue.upload / retry", "cyan"),
    ("ClipUploadQueue", "CloudMetadataService.synchronize + CloudAssetService.saveExportedClip", "green"),
    ("AppViewModel", "ClipDownloadCoordinator.resolve → CloudAssetService.downloadClip", "cyan"),
    ("BoutPlayerView", "BoutPlaybackQueue.next / previous; MediaPlayerModel.play / seek / scrub", "blue"),
    ("CloudMetadataService", "CloudMetadataMapper.apply → LocalRepository records", "orange"),
]


def calls():
    rows = ['<div class="call-grid"><div class="grid-category">Caller</div><div class="grid-category">Principal production call → callee</div>']
    for caller, action, color in CALLS:
        rows.append(card(caller, "object / view", color))
        rows.append(card(action, "direct or composed cross-component path", color))
    rows.append('</div><p class="callout">Representative cross-component paths; private helpers and framework callbacks are indexed in CALL_INDEX.md. '
                'AppViewModel.addBout has no production view caller.</p>')
    return ''.join(rows)


ORG = [
    ("Open app", "AppDependencies.make opens SwiftData and wires services", "blue"),
    ("Load records", "AppViewModel checks iCloud, reads local settings and tournaments", "cyan"),
    ("Choose first screen", "No settings → FirstRunSetupView; otherwise tournament navigation", "orange"),
    ("Create tournament", "Form validates name → saveTournament inserts/updates Tournament", "blue"),
    ("Import Schedule", "Choose manual entry or one or more screenshots", "blue"),
    ("Build draft bouts", "Manual numbers; or Vision OCR → parser → optional model → validator", "green"),
    ("Review proposal", "Edit, reorder, discard, or confirm in ScheduleReviewViewModel", "orange"),
    ("Confirm schedule", "Validate nonempty, opponent, unique positive numbers → insert Bouts", "green"),
    ("Open bout", "BoutDetailView offers edits, recording import and playback", "blue"),
]


MEDIA = [
    ("Choose recordings", "PhotosPicker selects up to 20 original videos", "blue"),
    ("Prepare batch", "PhotoLibraryService reads metadata and IDs; review failures", "green"),
    ("Confirm import", "Insert SourceRecording links; originals remain in Photos", "orange"),
    ("Open and trim", "PhotoKit AVAsset or fallback → select range → AVFoundation export", "green"),
    ("Store review clip", "ReviewClip moves exporting → pendingUpload; local file retained", "orange"),
    ("Upload private asset", "Sync metadata, save CKAsset; mark available or retry state", "cyan"),
    ("Play Bout", "Ordered clips resolve local export/cache or download CKAsset", "blue"),
    ("Control playback", "AVPlayer seek, scrub, speed, next/previous; no concatenation", "green"),
    ("Clean up", "Offload safe local copies; deletion removes cloud asset before local rows", "red"),
]


def timeline(steps, footer):
    content = ['<div class="timeline">']
    for index, (title, detail, color) in enumerate(steps, 1):
        content.append(f'<div class="timeline-step accent-{color}"><span class="step-number">{index:02d}</span>'
                       f'<strong class="node-name">{escape(title)}</strong><span class="node-detail">{escape(detail)}</span></div>')
    content.append('</div><p class="callout">' + escape(footer) + '</p>')
    return ''.join(content)


SPECS = {
    "01_architecture": ("Architecture", "Frontend, on-device logic, and data boundaries", "nested", nested,
        [("blue", "UI"), ("cyan", "Workflow models"), ("green", "Services"), ("orange", "Local state"), ("red", "Apple-managed")],
        ["SwiftUI sends commands to view models; services carry out schedule, media, synchronization, and playback work.",
         "SwiftData stores confirmed records. Temporary schedule drafts stay in memory until confirmation.",
         "Photos retains original videos. Private CloudKit holds confirmed metadata and edited clip assets."]),
    "02a_entities": ("Entity relationships", "Persisted UUID links and external assets", "tree", entities,
        [("blue", "Tournament / bout"), ("cyan", "Settings"), ("green", "Media record"), ("orange", "Schema-only"), ("red", "External asset")],
        ["Tournament → Bout → SourceRecording → ReviewClip is the main logical chain, with additional direct UUID references shown in the note.",
         "SourceRecording points to Photos originals; ReviewClip points to an edited CloudKit asset.",
         "ScheduleExtractionRun is in the schema but has no production insertion path."]),
    "02b_object_calls": ("Object calls", "Principal cross-component production methods", "grid", calls,
        [("blue", "UI caller"), ("cyan", "Workflow model"), ("green", "Service"), ("orange", "Repository")],
        ["Read each row left to right: the caller invokes the named method or service chain.",
         "Schedule proposals are reviewed before AppViewModel.confirmSchedule writes Bout records.",
         "The full production function declaration list is in CALL_INDEX.md; this diagram focuses on cross-component routes."]),
    "03a_organization_pathways": ("Organization pathways", "Launch, tournament, and schedule confirmation", "timeline", lambda: timeline(ORG, "Manual and screenshot entry converge at editable drafts. Discard returns without writing bouts. Cloud refresh may continue after the local first screen appears."),
        [("blue", "UI action"), ("cyan", "View model"), ("green", "Processing"), ("orange", "Decision / write")],
        ["Launch opens local storage, loads settings and tournaments, then chooses setup or navigation.",
         "Tournament creation saves a record before either schedule import route begins.",
         "Both manual and screenshot routes create editable drafts; confirmation validates and inserts Bouts."]),
    "03b_media_pathways": ("Media pathways", "Recording import through replay and cleanup", "timeline", lambda: timeline(MEDIA, "Export or cloud failures retain retry status. Playback prefers a local export or cache, downloading the edited asset when needed. Deletion does not remove Photos originals."),
        [("blue", "UI action"), ("cyan", "Cloud sync"), ("green", "Processing"), ("orange", "Local record"), ("red", "Cleanup")],
        ["Photos selections are reviewed before the app inserts SourceRecording links.",
         "Trimming creates a local ReviewClip export; the queue then syncs metadata and its private CKAsset.",
         "Playback resolves each clip separately. Offloading clears safe local copies; deletion removes app-managed assets and records while leaving Photos originals intact."]),
}


CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@400;700;800&display=swap');
:root{--bg:#0a0e1a;--panel:#0f1528;--border:#1e2d4a;--blue:#2d7aff;--cyan:#00d4ff;--green:#00e5a0;--orange:#ff8c42;--red:#ff4d6a;--text:#c8d8f0;--dim:#4a6080;--grid-opacity:.04;--title-color:#ffffff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:'JetBrains Mono',monospace;min-height:100vh;overflow:hidden}
body::before{content:'';position:fixed;inset:0;background-image:linear-gradient(rgba(45,122,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(45,122,255,.04) 1px,transparent 1px);background-size:40px 40px;pointer-events:none;z-index:0}
#canvas-container{position:fixed;inset:0;overflow:hidden;cursor:grab;z-index:1;touch-action:none}#canvas-container.grabbing{cursor:grabbing}
.wrapper{position:absolute;z-index:1;width:1020px;min-width:320px;overflow-x:auto;transform-origin:0 0;padding:20px 30px 24px;background:rgba(10,14,26,.96);border:1px solid var(--border);border-radius:18px}
.wrapper.portrait{width:600px}header{text-align:center;margin:0 0 12px}h1{font-family:Syne,sans-serif;font-size:1.6rem;color:var(--title-color);margin:0;font-weight:800}h1 .highlight{color:var(--cyan)}.subtitle{font-size:.75rem;color:var(--dim);text-transform:uppercase;letter-spacing:.1em;margin:5px 0 0}
.artboard{width:960px;height:540px;aspect-ratio:16/9;border:1px solid var(--border);border-radius:14px;padding:18px;background:var(--bg);overflow:hidden;display:flex;flex-direction:column;justify-content:center}
.portrait .artboard{width:540px;height:960px;aspect-ratio:9/16;padding:18px 24px}.node-card{background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:12px;padding:12px 14px;transition:border-color .2s;min-width:0}.node-card:hover{border-color:var(--cyan)}.node-name{display:block;color:white;font-family:Syne,sans-serif;font-size:.85rem;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.node-detail{display:block;color:var(--text);font-size:.65rem;line-height:1.35;margin-top:5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.accent-blue{--accent:var(--blue)}.accent-cyan{--accent:var(--cyan)}.accent-green{--accent:var(--green)}.accent-orange{--accent:var(--orange)}.accent-red{--accent:var(--red)}
.nested{width:100%;display:flex;flex-direction:column;gap:5px}.layer{min-height:80px;border:1px solid var(--accent);border-radius:16px;padding:10px 14px;background:color-mix(in srgb,var(--accent) 6%,var(--panel));}.layer-label{font-size:.65rem;font-weight:700;letter-spacing:.15em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}.layer-label::before{content:'';display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--accent);box-shadow:0 0 8px var(--accent);margin-right:8px;vertical-align:middle}.node-row{display:flex;flex-wrap:wrap;gap:12px;justify-content:center;align-items:stretch}.node-row .node-card{flex:1;min-width:140px;max-width:180px}.split-layers{display:grid;grid-template-columns:1.5fr 1fr;gap:12px}.split-layers .node-card{min-width:100px;max-width:160px}.connector{display:flex;flex-direction:column;align-items:center;margin:0 auto;color:var(--blue)}.connector-line{width:2px;height:10px;background:linear-gradient(to bottom,var(--dim),var(--blue))}.connector-label{font-size:.6rem;text-transform:uppercase;background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:2px 8px;color:var(--text)}.arrowhead{font-size:10px}.callout{background:rgba(0,212,255,.05);border:1px solid rgba(0,212,255,.2);border-radius:10px;padding:10px 14px;font-size:.65rem;line-height:1.4;text-align:center;margin:8px 0 0}
.tree{width:100%;padding-left:0}.tree ul{list-style:none;padding-left:28px;position:relative;margin:0}.tree>ul{display:grid;grid-template-columns:3fr 1fr;gap:10px;padding:0}.tree li{position:relative;padding:3px 0 3px 20px}.tree li::before{content:'';position:absolute;left:0;top:0;bottom:0;width:1px;background:var(--border)}.tree li::after{content:'';position:absolute;left:0;top:18px;width:16px;height:1px;background:var(--border)}.tree li:last-child::before{bottom:calc(100% - 18px)}.tree .node-card{display:inline-flex;flex-direction:column;min-width:160px;max-width:320px;padding:7px 11px}.tree .node-detail{font-size:.58rem}.tree .node-name{font-size:.78rem}
.call-grid{display:grid;grid-template-columns:180px 1fr;gap:4px 10px;align-items:stretch}.grid-category{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.15em;color:var(--dim);border-bottom:1px solid var(--border);padding:3px 0}.call-grid .node-card{padding:3px 10px;border-radius:6px}.call-grid .node-name{font-size:.68rem}.call-grid .node-detail{display:none}.call-grid+.callout{margin-top:8px}
.timeline{position:relative;width:100%;padding-left:48px}.timeline::before{content:'';position:absolute;left:20px;top:0;bottom:0;width:2px;background:linear-gradient(to bottom,var(--blue),var(--cyan),transparent)}.timeline-step{position:relative;margin-bottom:9px;padding:8px 12px;background:var(--panel);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:12px}.timeline-step .node-name{font-size:.77rem}.timeline-step .node-detail{font-size:.62rem;margin-top:2px}.step-number{position:absolute;left:-39px;top:11px;width:24px;height:24px;background:var(--panel);border:2px solid var(--accent);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.65rem;font-weight:700;color:var(--accent)}
.legend{display:flex;gap:20px;flex-wrap:wrap;justify-content:center;margin-top:14px}.legend-item{display:flex;align-items:center;gap:6px;font-size:.65rem;color:var(--dim);letter-spacing:.05em}.legend-dot{width:8px;height:8px;border-radius:50%;flex-shrink:0;background:var(--accent);box-shadow:0 0 6px var(--accent)}.explanation{margin:12px 0 0;padding:0 0 0 22px;font-size:.67rem;line-height:1.5;color:var(--text)}.explanation li{margin-bottom:3px}.source-note{font-size:.6rem;color:var(--dim);text-align:center;margin:9px 0 0}.source-note a{color:var(--cyan)}
.canvas-controls{position:fixed;bottom:20px;right:20px;display:flex;gap:4px;z-index:10}.canvas-controls button{min-width:36px;height:36px;border:1px solid var(--border);background:var(--panel);color:var(--text);border-radius:8px;font-family:'JetBrains Mono',monospace;font-size:.85rem;font-weight:700;cursor:pointer}.canvas-controls button:hover{border-color:var(--cyan);background:rgba(0,212,255,.08)}#zoom-reset{padding:0 12px;font-size:.6rem;text-transform:uppercase;letter-spacing:.08em}
@media(max-width:600px){.wrapper{border-radius:0}.node-row{flex-wrap:wrap}}
@keyframes fadeUp{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}.artboard>*{animation:fadeUp .5s ease both}@media(prefers-reduced-motion:reduce){.artboard>*{animation:none}}
"""


JS = r"""
(function(){
const container=document.getElementById('canvas-container');
const canvas=document.getElementById('canvas');
let scale=1,x=0,y=0,panning=false,startX=0,startY=0;
const min=.2,max=3,step=.1;
function apply(){canvas.style.transform=`translate(${x}px, ${y}px) scale(${scale})`}
function fit(){const w=canvas.scrollWidth,h=canvas.scrollHeight;scale=Math.max(min,Math.min(1,(container.clientWidth-40)/w,(container.clientHeight-40)/h));x=(container.clientWidth-w*scale)/2;y=Math.max(20,(container.clientHeight-h*scale)/2);apply()}
requestAnimationFrame(()=>requestAnimationFrame(fit));window.addEventListener('resize',fit);
container.addEventListener('pointerdown',e=>{if(e.button!==0)return;panning=true;startX=e.clientX-x;startY=e.clientY-y;container.classList.add('grabbing');container.setPointerCapture(e.pointerId)});
container.addEventListener('pointermove',e=>{if(!panning)return;x=e.clientX-startX;y=e.clientY-startY;apply()});
container.addEventListener('pointerup',()=>{panning=false;container.classList.remove('grabbing')});
container.addEventListener('wheel',e=>{e.preventDefault();const prior=scale;scale=Math.max(min,Math.min(max,scale+(e.deltaY<0?step:-step)));const ratio=scale/prior;x=e.clientX-ratio*(e.clientX-x);y=e.clientY-ratio*(e.clientY-y);apply()},{passive:false});
document.getElementById('zoom-in').onclick=()=>{scale=Math.min(max,scale+step);apply()};
document.getElementById('zoom-out').onclick=()=>{scale=Math.max(min,scale-step);apply()};
document.getElementById('zoom-reset').onclick=fit;
window.addEventListener('keydown',e=>{if(e.key==='0')fit();else if(e.key==='+'||e.key==='='){scale=Math.min(max,scale+step);apply()}else if(e.key==='-'){scale=Math.max(min,scale-step);apply()}});
})();
"""


def render(stem, spec):
    title, subtitle, topology, make_content, legend, explanation = spec
    portrait = stem.startswith("03")
    legend_html = ''.join(f'<span class="legend-item"><span class="legend-dot accent-{color}"></span>{escape(label)}</span>' for color, label in legend)
    explanation_html = ''.join(f'<li>{escape(item)}</li>' for item in explanation)
    page = (f'<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)} · Fencing Video Analysis</title><style>{CSS}</style></head><body>'
            f'<div id="canvas-container"><main id="canvas" class="wrapper{" portrait" if portrait else ""}" data-topology="{topology}">'
            f'<header><h1>Fencing Video Analysis · <span class="highlight">{escape(title)}</span></h1><p class="subtitle">{escape(subtitle)}</p></header>'
            f'<section class="artboard" aria-label="{escape(title)} diagram">{make_content()}</section>'
            f'<div class="legend" aria-label="Color legend">{legend_html}</div><ol class="explanation">{explanation_html}</ol>'
            f'<p class="source-note">Source-traced MVP review · <a href="../README.md">Detailed analysis and source links</a>'
            f' · <a href="../CALL_INDEX.md">Function index</a></p></main></div>'
            f'<div class="canvas-controls"><button id="zoom-in" aria-label="Zoom in">+</button>'
            f'<button id="zoom-reset">Reset</button><button id="zoom-out" aria-label="Zoom out">−</button></div>'
            f'<script>{JS}</script></body></html>\n')
    path = OUT / f"diagram-{stem}.html"
    path.write_text(page)
    print(path.relative_to(ROOT))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for name, specification in SPECS.items():
        render(name, specification)
