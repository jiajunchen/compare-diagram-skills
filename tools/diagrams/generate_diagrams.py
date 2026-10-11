"""Render source-traced MVP diagrams with Graphviz.

Run from the repository root: .venv/bin/python figures/tools/diagrams/generate_diagrams.py
The diagrams describe production paths, not simulator fakes or test fixtures.
"""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime


from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from graphviz import Digraph

OUT = FIGURES / 'graphviz'
NAVY = "#17324D"
BLUE = "#DCEAF5"
GREEN = "#DDF0E5"
ORANGE = "#FFF0D6"
PURPLE = "#ECE4F5"
GRAY = "#EFF2F4"
RED = "#FBE4E1"
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")


def graph(name, direction="LR"):
    g = Digraph(name, format="svg")
    g.attr(
        rankdir=direction, bgcolor="white", pad="0.28", nodesep="0.43",
        ranksep="0.74", splines="polyline", compound="true",
        fontname="Helvetica", fontsize="18", fontcolor=NAVY,
        labeljust="l", labelloc="t",
    )
    g.attr("node", shape="box", style="rounded,filled", color=NAVY,
           penwidth="1.1", fillcolor=BLUE, fontname="Helvetica",
           fontcolor=NAVY, fontsize="11", margin="0.15,0.11")
    g.attr("edge", color="#526779", fontname="Helvetica", fontsize="9",
           fontcolor=NAVY, arrowsize="0.7", penwidth="1.2")
    return g


def node(g, key, label, fill=BLUE, shape="box"):
    g.node(key, label, fillcolor=fill, shape=shape)


def cluster(g, key, label, color="#8AA4B8"):
    sg = Digraph(name=f"cluster_{key}")
    sg.attr(label=label, color=color, style="rounded", penwidth="1.4",
            fontname="Helvetica-Bold", fontsize="13", fontcolor=NAVY,
            margin="16")
    return sg


def svg_element(name, **attributes):
    return ET.Element(f"{{{SVG_NS}}}{name}", attributes)


def add_text(parent, x, y, value, size=19, weight="normal"):
    label = ET.SubElement(parent, f"{{{SVG_NS}}}text", {
        "x": str(x), "y": str(y), "fill": NAVY,
        "font-family": "Helvetica, Arial, sans-serif",
        "font-size": str(size), "font-weight": weight,
    })
    label.text = value


def save(g, stem, legend, portrait=False):
    """Fit the Graphviz art in a fixed-ratio canvas and add an in-page legend."""
    (OUT / f"{stem}.gv").write_text(g.source)
    art = ET.fromstring(g.pipe(format="svg"))
    _, _, art_width, art_height = map(float, art.attrib["viewBox"].split())
    width, height = (1080, 1920) if portrait else (1920, 1080)
    legend_top = 1680 if portrait else 900
    margin = 42
    content_width = width - 2 * margin
    content_height = legend_top - 2 * margin
    scale = min(content_width / art_width, content_height / art_height)
    offset_x = (width - art_width * scale) / 2
    offset_y = margin + (content_height - art_height * scale) / 2

    page = svg_element("svg", width=str(width), height=str(height),
                       viewBox=f"0 0 {width} {height}", version="1.1")
    page.append(svg_element("rect", x="0", y="0", width=str(width),
                            height=str(height), fill="white"))
    artwork = ET.SubElement(page, f"{{{SVG_NS}}}g", {
        "transform": f"translate({offset_x:.3f} {offset_y:.3f}) scale({scale:.6f})",
        "aria-label": f"{stem} diagram",
    })
    artwork.extend(list(art))
    page.append(svg_element("line", x1="42", y1=str(legend_top),
                            x2=str(width - 42), y2=str(legend_top),
                            stroke="#8AA4B8", **{"stroke-width": "2"}))
    add_text(page, 52, legend_top + 35, "Color legend", size=22, weight="bold")
    columns = 2 if portrait else 3
    column_width = (width - 100) / columns
    row_height = 57 if portrait else 48
    first_y = legend_top + 73
    for index, (color, label) in enumerate(legend):
        column = index % columns
        row = index // columns
        x = 52 + column * column_width
        y = first_y + row * row_height
        page.append(svg_element("rect", x=f"{x:.1f}", y=str(y - 22),
                                width="31", height="27", rx="5", fill=color,
                                stroke=NAVY, **{"stroke-width": "1.5"}))
        add_text(page, x + 44, y, label, size=18)

    svg_path = OUT / f"{stem}.svg"
    ET.ElementTree(page).write(svg_path, encoding="utf-8", xml_declaration=True)
    subprocess.run(["rsvg-convert", "-f", "pdf", "-o",
                    str(OUT / f"{stem}.pdf"), str(svg_path)], check=True)
    subprocess.run(["rsvg-convert", "-f", "png", "-o",
                    str(OUT / f"{stem}.png"), str(svg_path)], check=True)


def architecture():
    g = graph("architecture", "TB")
    g.attr(label="01  Overall codebase architecture | one native iPhone / iPad app")
    node(g, "user", "Parent / fencer\nSwiftUI actions", GRAY)

    ui = cluster(g, "ui", "Presentation")
    node(ui, "root", "AppRootView\nlaunch + scene activation")
    node(ui, "views", "Tournament, schedule, bout,\ntimeline, player, settings views")
    node(ui, "vm", "AppViewModel\nUI state + workflow orchestration", PURPLE)
    node(ui, "review", "ScheduleReviewViewModel\neditable, unconfirmed drafts", PURPLE)
    g.subgraph(ui)

    services = cluster(g, "services", "On-device application services")
    node(services, "schedule", "Schedule source -> Vision recognition\n-> deterministic parser -> Foundation Model\n-> proposal validator", GREEN)
    node(services, "import", "BoutImportCoordinator\nPhotoLibraryService", GREEN)
    node(services, "editing", "ClipWorkflow -> VideoEditingService\nAVFoundation export", GREEN)
    node(services, "upload", "ClipUploadQueue\nCloudMetadataService + CloudAssetService", GREEN)
    node(services, "play", "BoutPlaybackQueue + MediaPlayerModel\nClipDownloadCoordinator + cache", GREEN)
    g.subgraph(services)

    local = cluster(g, "local", "Device-local state")
    node(local, "repo", "LocalRepository / SwiftData\nsettings, tournaments, bouts, source links, clips", ORANGE)
    node(local, "files", "App support files\npending exports + downloaded clips", ORANGE)
    node(local, "drafts", "Screenshot bytes + OCR/proposal\nin memory until confirmation", ORANGE)
    g.subgraph(local)

    external = cluster(g, "external", "Apple-managed services")
    node(external, "photos", "Photos / iCloud Photos\noriginal videos; read on explicit import/open", GRAY)
    node(external, "cloud", "Private CloudKit\nconfirmed metadata + edited CKAssets", GRAY)
    g.subgraph(external)

    g.edge("user", "views", label="tap / select / edit")
    g.edge("root", "vm", label="load, refresh")
    g.edge("views", "vm", label="commands / observed state")
    g.edge("views", "review", label="schedule review")
    g.edge("review", "schedule", label="extract")
    g.edge("review", "drafts", label="temporary proposal")
    g.edge("review", "vm", label="confirm drafts")
    g.edge("vm", "repo", label="CRUD")
    g.edge("vm", "import", label="prepare / confirm / open")
    g.edge("import", "photos", label="read video + IDs")
    g.edge("import", "repo", label="source links")
    g.edge("vm", "editing", label="trim / export")
    g.edge("editing", "files", label="local clip")
    g.edge("editing", "repo", label="clip status")
    g.edge("vm", "upload", label="sync / retry")
    g.edge("upload", "cloud", label="metadata + CKAsset", dir="both")
    g.edge("upload", "repo", label="sync state", dir="both")
    g.edge("views", "play", label="player controls")
    g.edge("vm", "play", label="clip URL / unload")
    g.edge("play", "cloud", label="download clip")
    g.edge("play", "files", label="cache / replay", dir="both")
    save(g, "01_architecture", [
        (BLUE, "SwiftUI views"), (PURPLE, "View models"),
        (GREEN, "On-device services"), (ORANGE, "Device-local state"),
        (GRAY, "Person / Apple services"),
    ])


def entities():
    g = graph("entities", "TB")
    g.attr(label="02A  Persisted entities | UUID references, not SwiftData @Relationship")
    node(g, "settings", "AppSettings\nPK id (stable cloudID)\nfencerName, syncState", PURPLE)
    node(g, "tournament", "Tournament\nPK id\nname, venue, startDate, timezone\nscheduleImportStatus, syncState")
    node(g, "bout", "Bout\nPK id | FK tournamentID\nphase, opponent, sequenceNumber\npool, strip, scheduledAt, syncState")
    node(g, "source", "SourceRecording\nPK id | FK tournamentID, boutID\nimportBatchID, Photos IDs\nrecordedAt, duration, localWorkingFilePath", GREEN)
    node(g, "clip", "ReviewClip\nPK id | FK boutID, sourceRecordingID\ntrim range, localExportPath\ncloudAssetRecordName, mediaSyncStatus\nisFavorite", GREEN)
    node(g, "run", "ScheduleExtractionRun\nPK id | FK tournamentID\nstatus, warnings, modelAssistanceUsed\n(schema only; no production inserts)", ORANGE)
    node(g, "photo", "PHAsset (Photos)\noriginal recording", GRAY)
    node(g, "asset", "CKRecord + CKAsset\nReviewClip-{UUID}", GRAY)
    g.edge("settings", "tournament", label="one fencer name\nused by all tournaments", style="dashed", arrowhead="none")
    g.edge("tournament", "bout", label="1 -> 0..*", arrowhead="crow")
    g.edge("tournament", "source", label="1 -> 0..* direct ID", style="dashed")
    g.edge("bout", "source", label="1 -> 0..*", arrowhead="crow")
    g.edge("bout", "clip", label="1 -> 0..* direct ID", style="dashed")
    g.edge("source", "clip", label="1 -> 0..*", arrowhead="crow")
    g.edge("tournament", "run", label="1 -> 0..* schema", style="dotted")
    g.edge("source", "photo", label="deviceLocalAssetID /\ncloudPhotoAssetID", style="dashed", dir="both")
    g.edge("clip", "asset", label="cloudAssetRecordName", style="dashed", dir="both")
    save(g, "02a_entities", [
        (PURPLE, "App settings"), (BLUE, "Tournament / bout"),
        (GREEN, "Media records"), (ORANGE, "Schema-only run"),
        (GRAY, "Apple media assets"),
    ])


def calls():
    g = graph("calls", "TB")
    g.attr(label="02B  Object calls | production cross-component methods")
    node(g, "entry", "FencingVideoAnalysisApp\nAppDependencies.make -> AppRootView", GRAY)
    node(g, "ui", "SwiftUI views\nforms, schedule, bout, timeline, player, settings")
    node(g, "vm", "AppViewModel\nload / refreshCloud\nsaveTournament / confirmSchedule / addBout*\nprepare/confirmRecordings / createClip\nplayableURL / delete / offload", PURPLE)
    node(g, "review", "ScheduleReviewViewModel\nextract / addDraft / removeDraft / moveDraft")
    node(g, "schedule", "Schedule services\nrecognize -> parse -> propose -> reconcile", GREEN)
    node(g, "bout", "BoutImportCoordinator\nprepareSelections / confirm / linkPendingCloudPhotos\nsourceAsset / move / remove", GREEN)
    node(g, "clip", "ClipWorkflow\ncreateClip / retry / delete / clips\nunloadUploadedClips / clearLocalClipCopies", GREEN)
    node(g, "queue", "ClipUploadQueue\nresumePending / upload / retry / deleteCloudCopyIfNeeded", GREEN)
    node(g, "cloud", "CloudMetadataService\nsynchronize / synchronizeDeletions / queueDeletion\nmapper pendingRecords / apply", GREEN)
    node(g, "assets", "CloudAssetService\nsaveExportedClip / downloadClip / deleteClip", GREEN)
    node(g, "download", "ClipDownloadCoordinator\nresolve / clearCache / removeCachedCopies", GREEN)
    node(g, "player", "BoutPlaybackQueue + MediaPlayerModel\nnext / previous / finish / play / seek / scrub", GREEN)
    node(g, "repo", "LocalRepository\ninsert / fetch / delete / saveChanges\ntournaments / bouts / sourceRecordings / reviewClips", ORANGE)
    node(g, "photos", "PhotoLibraryService\nimportSelections / cloudIdentifiers / videoAsset", GRAY)
    node(g, "editor", "VideoEditingService.export", GRAY)
    node(g, "ck", "Private CloudKit + Photos\nframework boundaries", GRAY)
    g.edge("entry", "ui")
    g.edge("ui", "vm", label="commands")
    g.edge("ui", "review", label="schedule")
    g.edge("ui", "player", label="playback controls")
    g.edge("review", "schedule")
    g.edge("review", "vm", label="confirmed drafts")
    g.edge("vm", "bout")
    g.edge("vm", "clip")
    g.edge("vm", "queue")
    g.edge("vm", "cloud")
    g.edge("vm", "download")
    g.edge("vm", "repo")
    g.edge("bout", "photos")
    g.edge("bout", "repo")
    g.edge("clip", "editor")
    g.edge("clip", "repo")
    g.edge("queue", "cloud")
    g.edge("queue", "assets")
    g.edge("download", "assets")
    g.edge("cloud", "repo")
    g.edge("photos", "ck", label="Photos")
    g.edge("assets", "ck", label="CKAsset")
    g.edge("cloud", "ck", label="CKSyncEngine")
    save(g, "02b_object_calls", [
        (GRAY, "Entry / Apple frameworks"), (BLUE, "UI and review state"),
        (PURPLE, "Workflow orchestration"), (GREEN, "Application services"),
        (ORANGE, "Local repository"),
    ])


def pathways_organization():
    g = graph("organization", "TB")
    g.attr(label="03A  User pathways | launch, tournament, and schedule")
    node(g, "launch", "Open app", GRAY, "oval")
    node(g, "boot", "AppDependencies.make\nopen SwiftData; wire live services")
    node(g, "load", "AppViewModel.load\ncheck iCloud; fetch local settings/tournaments")
    node(g, "settings", "Settings found?", ORANGE, "diamond")
    node(g, "first", "FirstRunSetupView\nsaveFencerName -> SwiftData", BLUE)
    node(g, "nav", "TournamentNavigationView\nselect / refreshCloud", BLUE)
    node(g, "new", "New Tournament\nTournamentFormView.save", BLUE)
    node(g, "save", "AppViewModel.saveTournament\nvalidate name; insert/update Tournament\nSwiftData save -> schedule CloudKit sync", GREEN)
    node(g, "detail", "TournamentDetailView\nshow bouts / open selected bout", BLUE)
    node(g, "import", "Import Schedule\nscreenshot(s) or Manual Entry", BLUE)
    node(g, "manual", "Manual drafts\nadd opponent + full-order bout number", GREEN)
    node(g, "ocr", "Vision recognize each screenshot\ndeterministic parse + optional on-device model\nvalidator reconciles source-backed proposal", GREEN)
    node(g, "review", "Review/edit drafts\nconfirm or discard", BLUE)
    node(g, "confirm", "AppViewModel.confirmSchedule\nvalidate nonempty, opponent, positive/unique number\ninsert new Bouts; mark tournament confirmed", GREEN)
    node(g, "bout", "BoutDetailView\nedit/delete confirmed bout; import recordings", BLUE)
    g.edge("launch", "boot")
    g.edge("boot", "load")
    g.edge("load", "settings")
    g.edge("settings", "first", label="no")
    g.edge("first", "nav")
    g.edge("settings", "nav", label="yes")
    g.edge("nav", "new")
    g.edge("new", "save")
    g.edge("save", "detail")
    g.edge("detail", "import")
    g.edge("import", "manual", label="manual")
    g.edge("import", "ocr", label="screenshots")
    g.edge("manual", "review")
    g.edge("ocr", "review")
    g.edge("review", "confirm", label="confirm")
    g.edge("confirm", "bout")
    g.edge("review", "detail", label="discard", style="dashed", constraint="false")
    save(g, "03a_organization_pathways", [
        (GRAY, "User entry"), (BLUE, "UI action / screen"),
        (GREEN, "On-device processing"), (ORANGE, "Decision"),
    ], portrait=True)


def pathways_media():
    g = graph("media", "TB")
    g.attr(label="03B  User pathways | recording, clip, playback, and cleanup")
    node(g, "bout", "Open confirmed bout", GRAY, "oval")
    node(g, "pick", "Import Recordings\nPhotosPicker: up to 20 videos", BLUE)
    node(g, "prepare", "BoutImportCoordinator.prepareSelections\nPhotoLibraryService reads metadata / Photos IDs\nshow batch, failures, cancellation", GREEN)
    node(g, "confirm", "Confirm batch\ninsert SourceRecording links in SwiftData\ntry linking iCloud Photos IDs", GREEN)
    node(g, "timeline", "Review and Trim Recordings\nload ordered sources + clips", BLUE)
    node(g, "asset", "Open source\nPhotoKit AVAsset; local fallback if needed", GREEN)
    node(g, "trim", "Select trim range\nClipWorkflow.createClip -> AVFoundation export\nReviewClip: exporting -> pendingUpload", GREEN)
    node(g, "upload", "ClipUploadQueue.upload\nsync metadata -> save CKAsset\nReviewClip: uploading -> available", PURPLE)
    node(g, "fail", "Failure path\nexportFailed / pendingUpload / needsAttention\nretry export or upload", RED)
    node(g, "play", "Play clip / Play Bout\nordered ReviewClips -> playableURL", BLUE)
    node(g, "local", "Local export or managed cache?", ORANGE, "diamond")
    node(g, "download", "ClipDownloadCoordinator.resolve\ncheck iCloud -> download CKAsset -> cache", GREEN)
    node(g, "player", "MediaPlayerModel + BoutPlaybackQueue\nseek, scrub, speed, next clip (continuous)", GREEN)
    node(g, "offload", "Unload / Clear Local Copies\nonly confirmed available exports; clear cache\nretain CloudKit records/assets", ORANGE)
    node(g, "delete", "Delete clip/source/bout/tournament\nasset first, then local records, queue metadata deletion\nPhotos original stays intact", RED)
    g.edge("bout", "pick")
    g.edge("pick", "prepare")
    g.edge("prepare", "confirm", label="Add to Bout")
    g.edge("confirm", "timeline")
    g.edge("timeline", "asset")
    g.edge("asset", "trim")
    g.edge("trim", "upload", label="export success")
    g.edge("trim", "fail", label="export failure")
    g.edge("upload", "fail", label="cloud failure")
    g.edge("upload", "play", label="available")
    g.edge("fail", "upload", label="retry", style="dashed")
    g.edge("play", "local")
    g.edge("local", "player", label="yes")
    g.edge("local", "download", label="no")
    g.edge("download", "player")
    g.edge("player", "offload", label="optional")
    g.edge("timeline", "delete", label="optional", style="dashed", constraint="false")
    save(g, "03b_media_pathways", [
        (GRAY, "User entry"), (BLUE, "UI action / screen"),
        (GREEN, "On-device processing"), (PURPLE, "Cloud upload"),
        (ORANGE, "Decision / local cleanup"), (RED, "Failure / deletion"),
    ], portrait=True)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for render in (architecture, entities, calls, pathways_organization, pathways_media):
        render()
