"""Build the source-backed, static architecture atlas using Diagram Design conventions."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
from html import escape as e
import re, json, subprocess
HERE = (FIGURES / 'diagram-design')
ROOT = HERE.parent.parent
PAPER='#f9f9f9'; INK='#131313'; MUTED='#585858'; SURFACE='#eeeeec'; RULE='#b8b8b5'
SOURCES = list((ROOT/'FencingVideoAnalysis').rglob('*.swift'))
refs=[]
def source(file, symbol):
    path=next(p for p in SOURCES if p.name == file+'.swift')
    lines=path.read_text().splitlines()
    matches=[i+1 for i,s in enumerate(lines) if re.search(r'\b'+re.escape(symbol)+r'\b',s)]
    assert matches, (file,symbol)
    # Prefer declaration over call sites.
    decl=[i+1 for i,s in enumerate(lines) if re.search(r'\b(?:func|class|struct|enum|actor)\s+'+re.escape(symbol)+r'\b',s)]
    line=(decl or matches)[0]
    rel=path.relative_to(ROOT)
    refs.append({'file':str(rel),'symbol':symbol,'line':line})
    return f'<a href="../../{rel}#L{line}"><code>{e(file)}.{e(symbol)}()</code></a><span class="location">{e(str(rel))}:{line}</span>'
def node(title,code,detail,kind='service'): return (title,code,detail,kind)
chapters=[]
def chapter(id,title,intro,nodes,edges,rows,aside):
    chapters.append(dict(id=id,title=title,intro=intro,nodes=nodes,edges=edges,rows=rows,aside=aside))
# Positions: 0..2 upper row, 3..5 lower row. Each figure has at most six nodes.
chapter('overview','One app. Three storage boundaries.',
'A parent records a fencing bout in Camera, selects recordings from Photos, and saves useful sections as review clips. The same private iCloud account connects the iPhone and iPad.',[
node('SwiftUI screens','AppRootView / feature views','Setup, tournaments, bouts and review','input'),
node('App controller','AppViewModel','Coordinates user actions and services','focus'),
node('Local metadata','SwiftDataRepository','Records, IDs and pending work','store'),
node('Schedule extraction','Vision + parser + local model','Screenshots become editable drafts'),
node('Media workflows','Import / export / playback','Photos sources and separate review clips'),
node('Private iCloud','CKSyncEngine + CKAsset','Confirmed records and edited clip files','external')],
[(0,1,'ACTIONS'),(1,2,'SAVE / READ'),(1,3,'EXTRACT'),(1,4,'MEDIA'),(2,5,'METADATA',True),(4,5,'CLIP ASSETS',True)],
[('Compose the app','AppDependencies','make','Constructs repository, live or fake services, media cache and download coordinator. The repository save hook schedules metadata sync.'),
('Handle actions','AppViewModel','load','Loads local data, checks the iCloud account and refreshes cloud data when available. Feature views call the controller for app-level work.')],
'Photos is a separate Apple-managed library. Source recording bytes never enter the app’s CloudKit database. Schedule screenshots, OCR text and unconfirmed proposals remain on-device. There is no app server or external AI service in this MVP.')
chapter('startup','Open locally. Reconcile with iCloud.',
'The app creates its service dependencies once. Local records remain the starting point for the interface; cloud work updates that state.',[
node('Application entry','FencingVideoAnalysisApp','Builds the dependency container','input'),
node('Dependency container','AppDependencies.make()','Injects services into the root view','focus'),
node('Initial load','AppViewModel.load()','Account check + local records'),
node('Visible collections','Settings / tournaments / bouts','Refetched after synchronization','store'),
node('Cloud refresh','AppViewModel.refreshCloud()','Discover records; link Photos; resume uploads'),
node('Local housekeeping','removeAbandonedFiles()','Runs during initial load')],
[(0,1,'CONSTRUCT'),(1,2,'LOAD'),(2,4,'IF AVAILABLE',True),(4,3,'REFETCH'),(2,5,'CLEAN UP')],
[('First launch or open','AppViewModel','load','Fetches AppSettings and tournaments, refreshes favorite bout IDs, then requests cloud refresh. The isLoaded flag prevents duplicate initial loads.'),
('Foreground / refresh','AppViewModel','refreshCloud','Calls synchronize(discoverNewRecords: true), linkPendingCloudPhotos(), resumePending(), then reloads the visible collections.'),
('Complete first-run setup','AppViewModel','saveFencerName','Saves the single fencer name. AppRootView shows setup when no settings record exists, then opens tournament navigation.'),
('Create or edit a tournament','AppViewModel','saveTournament','Validates the tournament fields and saves local metadata for later private CloudKit synchronization.'),
('Recover local files','ClipWorkflow','removeAbandonedFiles','Cleans abandoned files in managed source and clip directories using an age cutoff. Errors become a visible message.')],
'Production uses SwiftData with explicit CloudKit coordination. On the simulator, metadata and asset services are fakes. Test launch options can also substitute Photos, schedules and in-memory storage. These are injected service implementations, not separate product architectures.')
chapter('schedule','A screenshot is evidence, not a confirmed bout.',
'The local pipeline reads a schedule, proposes opponents and bout numbers, then waits for the parent to correct and confirm them.',[
node('Schedule screenshots','ScheduleSourceService','Or choose manual entry','input'),
node('Document recognition','recognize() → documents','Vision text, tables, bounds and warnings'),
node('Deterministic parser','parse(documents, fencerName:)','Find the fencer in the full bout order'),
node('Parent confirmation','confirmSchedule()','Save confirmed bouts to the local store','focus'),
node('Evidence validation','reconcile(documents:extraction:)','Trace fields; reject unsupported values'),
node('Optional model help','propose(from:fencerName:...)','Foundation Models; local fallback','optional')],
[(0,1,'SCREENSHOTS'),(1,2,'DOCUMENTS'),(2,5,'CANDIDATE'),(5,4,'RECONCILE'),(4,3,'REVIEW')],
[('Start extraction','ScheduleReviewViewModel','extract','Recognizes each screenshot, runs parse(), asks propose() for model assistance, then calls reconcile(). Manual entry immediately opens an empty editable draft.'),
('Read the screenshot','DocumentRecognitionService','recognize','Uses document recognition on supported systems, with accurate text recognition as the compatibility path. Results preserve layout and confidence.'),
('Find candidate bouts','ScheduleParsingService','parse','Matches the saved fencer and extracts opponent and full-order sequence information.'),
('Check model output','ScheduleProposalValidator','reconcile','Combines evidence and warnings. Unavailable model assistance keeps the deterministic result; it does not send the screenshot to a cloud model.'),
('Commit the schedule','AppViewModel','confirmSchedule','Validates opponent names and positive, unique bout numbers; skips already-saved identical bouts. The parent can discard the proposal without creating bouts.'),
('Correct a saved bout','AppViewModel','updateConfirmedBout','Edits opponent and full-order bout number after confirmation. deleteConfirmedBout() rejects removal while recordings or clips still refer to the bout.')],
'Read the upper row left to right, then the lower row right to left. The arrows show the extraction order. Only confirmed metadata can sync. Screenshot recognition is not video analysis, touch detection or coaching advice.')
chapter('recordings','Choose the bout before choosing the recordings.',
'Every selected recording belongs to the already-open bout. Capture time orders the recordings; the app does not infer which bout they belong to.',[
node('Selected bout','BoutDetailView / PhotosPicker','The parent chooses the destination','input'),
node('Prepare selection','prepareRecordings()','Reject known assets; collect per-file results'),
node('Review import','RecordingImportReviewView','Confirm successes or discard the batch','focus'),
node('Original Photos asset','PhotoLibraryService','Original file remains unchanged','external'),
node('Source recording record','SourceRecording','Bout ID + capture time + Photos link','store'),
node('Import coordinator','confirmRecordings() → confirm()','Save links and local working paths')],
[(0,1,'SELECT'),(1,2,'REVIEW'),(2,5,'CONFIRM'),(5,4,'INSERT'),(4,3,'RESOLVE')],
[('Prepare chosen videos','BoutImportCoordinator','prepareSelections','Calls importSelections() with the known asset identifiers. Partial import results can be reviewed before saving.'),
('Confirm attachment','BoutImportCoordinator','confirm','Inserts SourceRecording records for successful imports into the chosen bout and saves them.'),
('Discard a batch','BoutImportCoordinator','discard','Removes temporary working files for the unconfirmed batch.'),
('Resolve a source','BoutImportCoordinator','sourceAsset','Uses available Photos identifiers or local working media to obtain an AVAsset for editing.'),
('Move or remove','BoutImportCoordinator','move','Moves an eligible source to a different bout. remove() removes the app association and managed working file, not the original Photos asset.')],
'A cloud Photos identifier can link a recording across the shared Photos library. Local file paths and device-specific Photos IDs stay local. A missing Photos link may require reconnecting Photos; this is independent of downloading an edited review clip.')
chapter('clips','Save a clip locally, then upload it.',
'A review clip is a separate exported movie with its own ID and source time range. Saving several clips does not merge them into one movie.',[
node('Trim selection','AppViewModel.createClip()','Source recording + start/end times','input'),
node('Clip workflow','ClipWorkflow.createClip()','Validate range; insert the clip record','focus'),
node('Video export','VideoEditingService.export()','AVFoundation → standalone movie'),
node('Private clip asset','saveExportedClip(at:id:)','CKAsset attached to the clip record','external'),
node('Upload queue','ClipUploadQueue.upload()','Sync metadata before saving the asset'),
node('Durable pending work','ReviewClip.localExportPath','pendingUpload + retained export','store')],
[(0,1,'CREATE'),(1,2,'EXPORT'),(2,5,'FILE READY'),(5,4,'UPLOAD',True),(4,3,'ASSET SAVE',True)],
[('Save the trim','AppViewModel','createClip','Resolves the source AVAsset, calls ClipWorkflow.createClip(), and launches the upload task after export succeeds.'),
('Export the media','ClipWorkflow','createClip','Validates TrimRange, inserts ReviewClip, runs editor.export(), and stores the resulting path and duration. Failed exports remain exportFailed.'),
('Upload the file','ClipUploadQueue','upload','Marks uploading, calls metadata.synchronize(), saves the asset, and marks available only if the clip and export still match.'),
('Recover work','ClipUploadQueue','resumePending','Retries pendingUpload and uploading records. Temporary account or network failures return to pendingUpload; other failures become needsAttention.'),
('Retry explicitly','AppViewModel','retryClip','Re-exports a failed clip. retryUpload() retries an existing local export without creating a new clip ID.')],
'The metadata record can arrive on the other device before the video asset. The receiver must handle “Waiting for upload.” Pending export files are retained so an interrupted upload can recover.')
chapter('playback','A continuous bout is an ordered queue.',
'The player moves between independent clip files. It resolves each file on demand, while shared transport logic controls speed and scrubbing.',[
node('Saved bout player','BoutPlayerView.load()','Fetch clips in chronological order','input'),
node('Playback queue','BoutPlaybackQueue','Select, previous, next and completion'),
node('Resolve current clip','AppViewModel.playableURL()','Local export → cache → CloudKit','focus'),
node('Timeline gestures','VisualScrubCoordinator','drag() / finish() / cancel()'),
node('Transport state','MediaPlayerModel + PlaybackState','Speed, time and play/pause'),
node('Movie playback','AVPlayer','Open resolved URL; observe completion','external')],
[(0,1,'ORDER'),(1,2,'CURRENT CLIP'),(2,5,'FILE URL'),(4,5,'TRANSPORT'),(4,3,'SCRUB')],
[('Open the current clip','BoutPlayerView','openCurrent','Calls playableURL(), loads the result into the player session, and starts playback when requested.'),
('Resolve the file','ClipDownloadCoordinator','resolve','Prefers a local export, then the managed cache. Otherwise checks the account, downloads the asset, caches it and validates its video track.'),
('Advance the bout','BoutPlayerView','finishCurrentClip','Updates the logical queue when playback ends and opens the next clip. Clip files remain independent.'),
('Set playback speed','PlaybackState','setSpeed','Supports 0.25×, 0.5×, 1×, 1.5× and 2×. MediaPlayerModel applies the selected speed to AVPlayer.'),
('Follow the slider','VisualScrubCoordinator','drag','Keeps the newest target and starts a seek worker. Stale intermediate targets do not build an unbounded seek queue.'),
('Finish a drag','VisualScrubCoordinator','finish','Requests the final position with precise tolerance. Speed is player-session state and is reapplied across clip changes.')],
'The local-first resolver is a priority order, not three parallel downloads. A missing asset, unavailable account or network failure is surfaced for recovery. Playback speed is not synchronized to iCloud.')
chapter('sync','Metadata and media have separate recovery paths.',
'Both devices use the same private CloudKit account. Metadata synchronization discovers records; asset services transfer the edited movie bytes.',[
node('Local changes','SwiftDataRepository.saveChanges()','Persistent IDs and pending state','store'),
node('Metadata service','LiveCloudMetadataService','CKSyncEngine + saved system fields','focus'),
node('Private record zone','CloudKit metadata','Settings, tournaments, bouts and links','external'),
node('User deletes a clip','AppViewModel.deleteClip()','Remove clip; coordinate cloud deletion','input'),
node('Deletion coordination','queueDeletion()','Persist pending record deletions'),
node('Incoming changes','handleEvent()','Merge updates; reconcile deletions')],
[(0,1,'SAVE HOOK',True),(1,2,'SYNC',True),(2,5,'CHANGES',True),(3,4,'QUEUE DELETE'),(4,1,'DELETE',True)],
[('Queue routine sync','CloudMetadataService','scheduleSync','The repository save hook schedules metadata work. CKSyncEngine receives pending changes and builds outgoing records.'),
('Recover missed records','CloudMetadataService','synchronize','An explicit refresh can scan the full metadata zone to discover new records. Routine reconciliation also checks known records.'),
('Handle cloud events','CloudMetadataService','handleEvent','Applies fetched records/deletions, persists engine state and system fields, and handles outgoing results and conflicts.'),
('Delete a clip','AppViewModel','deleteClip','Waits for conflicting upload work, deletes a known cloud asset when needed, removes the local clip, queues metadata deletion and clears the cached file.'),
('Delete a tournament','AppViewModel','deleteTournament','Coordinates dependent clips, source links and bouts with cloud deletion. This does not delete original videos from Photos.'),
('Free local storage','AppViewModel','clearLocalClipCopies','Clears safe uploaded local copies through ClipWorkflow. This keeps cloud records and assets; pending uploads are protected.'),
('Save a favorite','AppViewModel','toggleClipFavorite','Updates the clip favorite field, saves pending favorite sync state, derives favorite bouts, then refreshes cloud data.')],
'This map groups two related recovery paths, not one universal call chain: incoming deletion handling removes local records, while user deletion first queues cloud work. Full cloud deletion and local-only offload have different effects.')
# Inline SVG grammar derived from the skill full-editorial template.
def diagram(c):
    ident=c['id']; x=[48,480,912]; ys=[112,400]; w=320; h=160
    boxes=[(x[i%3],ys[i//3],w,h) for i in range(6)]
    out=[f'<svg viewBox="0 0 1280 720" role="img" aria-labelledby="{ident}-title {ident}-desc"><title id="{ident}-title">{e(c["title"])}</title><desc id="{ident}-desc">{e(c["intro"])}</desc>',f'<defs><marker id="{ident}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{MUTED}"/></marker></defs>']
    out.append(f'<text x="48" y="48" class="svg-eyebrow">{e(ident.upper())} / IMPLEMENTATION MAP</text>')
    for edge in c['edges']:
        a,b,label,*opt=edge; dash=bool(opt and opt[0]); ax,ay,_,_=boxes[a]; bx,by,_,_=boxes[b]
        if ay==by:
            sx=ax+w if bx>ax else ax; ex=bx if bx>ax else bx+w; sy=ay+80
            d=f'M {sx} {sy} H {ex}'; lx=(sx+ex)/2; ly=sy-24
        elif ax==bx:
            sx=ax+w/2; sy=ay+h if by>ay else ay; ey=by if by>ay else by+h
            d=f'M {sx} {sy} V {ey}'; lx=sx+64; ly=(sy+ey)/2
        elif a==1 and b==3:
            # Dedicated left-side port and corridor, with rounded elbows.
            d='M 480 232 H 424 Q 416 232 416 240 V 328 Q 416 336 408 336 H 216 Q 208 336 208 344 V 400'; lx=310;ly=312
        elif a==2 and b==4:
            d='M 912 232 H 856 Q 848 232 848 240 V 328 Q 848 336 840 336 H 648 Q 640 336 640 344 V 400';lx=742;ly=312
        else: raise ValueError(edge)
        out.append(f'<path class="connector" d="{d}" fill="none" stroke="{MUTED}" stroke-width="1.5" {"stroke-dasharray=\"5,4\"" if dash else ""} marker-end="url(#{ident}-arrow)"/>')
        lw=len(label)*7+16
        # Vertical labels sit beside the line; all others above it.
        if ax==bx and ay!=by: lx=sx+10+lw/2
        out.append(f'<g class="edge-label"><rect x="{lx-lw/2}" y="{ly-13}" width="{lw}" height="20" fill="{PAPER}"/><text x="{lx}" y="{ly+1}" class="arrow-label" text-anchor="middle">{e(label)}</text></g>')
    for i,(title,code,detail,kind) in enumerate(c['nodes']):
        xx,yy,_,_=boxes[i]; focal=kind=='focus'; fill=INK if focal else SURFACE if kind=='store' else PAPER; color=PAPER if focal else INK
        dash='stroke-dasharray="5,4"' if kind in ('external','optional') else ''
        out.append(f'<g class="node" data-node="{i}"><rect x="{xx}" y="{yy}" width="320" height="160" rx="6" fill="{fill}" stroke="{INK if focal else RULE}" {dash}/><text x="{xx+20}" y="{yy+28}" class="type-tag" fill="{color}">{i+1:02} / {kind.upper()}</text><text x="{xx+20}" y="{yy+64}" class="node-title" fill="{color}">{e(title)}</text>')
        for j,line in enumerate(code.split(' / ') if len(code)>39 else [code]):
            out.append(f'<text x="{xx+20}" y="{yy+94+j*18}" class="node-code" fill="{color}">{e(line)}</text>')
        # Wrap human explanation into two lines if needed.
        words=detail.split(); lines=['']
        for word in words:
            if len(lines[-1])+len(word)>39: lines.append(word)
            else: lines[-1]+=(' ' if lines[-1] else '')+word
        for j,line in enumerate(lines): out.append(f'<text x="{xx+20}" y="{yy+126+j*18}" class="node-detail" fill="{color}">{e(line)}</text>')
        out.append('</g>')
    out.append(f'<line x1="48" y1="624" x2="1232" y2="624" stroke="{RULE}"/>')
    legend='Solid = direct call / dependency · Dashed connector = async cloud work · Filled = focal component · Gray = stored state · Dashed box = external or optional'
    out.append(f'<text x="48" y="656" class="legend">{e(legend)}</text></svg>')
    return ''.join(out)
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--paper);color:var(--ink);font-family:Geist,Arial,sans-serif}main{max-width:1440px;margin:auto;padding:40px 56px}a{color:inherit;text-underline-offset:4px}a:hover{color:#68685f}.eyebrow,.meta,.location,nav,.type-tag,.svg-eyebrow,.arrow-label{font-family:"Geist Mono",monospace}.eyebrow,.meta{font-size:11px;letter-spacing:.13em;text-transform:uppercase}.topline{display:flex;justify-content:space-between;border-bottom:1px solid var(--rule);padding-bottom:20px;gap:20px}header{padding:64px 0 40px}h1,h2{font-family:"Instrument Serif",Georgia,serif;font-weight:400;letter-spacing:-.035em;margin:0}h1{font-size:clamp(64px,7vw,104px);line-height:.96;max-width:950px}header .intro{font-size:20px;line-height:1.6;max-width:760px;margin:28px 0}.strap{display:flex;gap:32px;padding:24px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);font-size:13px}nav{display:flex;flex-wrap:wrap;gap:12px 24px;padding:28px 0;font-size:11px}section{padding:52px 0;border-top:1px solid var(--rule);scroll-margin-top:24px}.section-head{display:grid;grid-template-columns:100px 1fr;gap:16px}.num{font-family:"Instrument Serif",Georgia,serif;font-size:56px;color:var(--muted)}h2{font-size:52px;line-height:1.05}.section-intro{max-width:800px;font-size:17px;line-height:1.6;color:var(--muted);margin:20px 0 0}.diagram-container{width:100%;max-width:100%;min-width:0;overflow-x:auto}svg{width:100%;min-width:1280px;display:block}.svg-eyebrow{font-size:12px;letter-spacing:.1em;fill:var(--muted)}.type-tag{font-size:10px;letter-spacing:.1em}.node-title{font-size:20px;font-weight:600}.node-code{font:12px "Geist Mono",monospace}.node-detail{font:13px Geist,Arial,sans-serif}.arrow-label{font-size:11px;fill:var(--muted)}.legend{font:11px Geist,Arial,sans-serif;fill:var(--muted)}.note{display:grid;grid-template-columns:100px 1fr;gap:16px;border-top:1px solid var(--rule);padding:22px 0;font-size:15px;line-height:1.65}.note strong{font:italic 24px "Instrument Serif",Georgia,serif}.table-wrap{overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:14px;line-height:1.6;margin-top:20px}th{text-align:left;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:500}th,td{padding:18px 16px 18px 0;border-bottom:1px solid var(--rule);vertical-align:top}td:first-child{width:18%;font-weight:500}td:nth-child(2){width:34%}code{font:12px "Geist Mono",monospace;overflow-wrap:anywhere}.location{display:block;color:var(--muted);font-size:10px;overflow-wrap:anywhere;margin-top:8px}.citation{overflow-wrap:anywhere}.receipt{max-width:900px;font-size:14px;line-height:1.75}footer{padding:28px 0 48px;border-top:1px solid var(--rule);font-size:12px;line-height:1.8;color:var(--muted)}@media(max-width:700px){main{padding:24px 20px}header{padding:40px 0 24px}.topline,.strap{flex-direction:column;gap:12px}h1{font-size:62px}h2{font-size:38px}.section-head,.note{grid-template-columns:1fr}.num{font-size:32px}td,th{min-width:180px}section{padding:32px 0}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{main{padding:0;max-width:none}.diagram-container{overflow-x:visible}svg{min-width:0}nav{display:none}section{break-before:page}table{font-size:11px}.location{font-size:8px}a{text-decoration:none}}'''
fonts='https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap'
html=['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fencing Review — Architecture Atlas</title>',f'<link rel="stylesheet" href="{fonts}"><style>:root{{--paper:{PAPER};--ink:{INK};--muted:{MUTED};--rule:{RULE}}}{css}</style></head><body><main>',
'<div class="topline"><span class="eyebrow">Fencing Review / Architecture Atlas</span><span class="meta">Private MVP · iPhone + iPad · 09 October 2026</span></div><header><h1>From the piste<br>to the replay.</h1><p class="intro">A code-level map of the app that turns scattered tournament recordings into an ordered review session for a parent and fencer.</p><div class="strap"><span>01 parent · 01 fencer · 01 private iCloud account</span><span>Originals in Photos. Edited clips in CloudKit.</span><span>Local schedule extraction.</span></div></header><nav aria-label="Architecture sections">']
for i,c in enumerate(chapters): html.append(f'<a href="#{c["id"]}">{i+1:02} {e(c["id"].capitalize())}</a>')
html.append('<a href="#records">08 Records &amp; storage</a><a href="#design">09 Design &amp; provenance</a></nav>')
for i,c in enumerate(chapters):
    html.append(f'<section id="{c["id"]}"><div class="section-head"><span class="num">({i+1:02})</span><div><h2>{e(c["title"])}</h2><p class="section-intro">{e(c["intro"])}</p></div></div><div class="diagram-container" tabindex="0" aria-label="Scrollable {c["id"]} diagram">{diagram(c)}</div><div class="note"><strong>Read this</strong><div>{e(c["aside"])}</div></div><div class="table-wrap"><table><thead><tr><th>Trigger / role</th><th>Implementation entry</th><th>What happens</th></tr></thead><tbody>')
    for action,file,symbol,detail in c['rows']: html.append(f'<tr><td>{e(action)}</td><td>{source(file,symbol)}</td><td>{e(detail)}</td></tr>')
    html.append('</tbody></table></div></section>')
records=[
('AppSettings','One fixed cloud ID; fencerName','SwiftData + private CloudKit','One synchronized fencer profile; no app login or multi-fencer account model.'),
('Tournament','id; name; date; timezone','SwiftData + private CloudKit','Parent of bouts. Tournament deletion coordinates dependent records and media.'),
('Bout','tournamentID; opponentName; sequenceNumber','SwiftData + private CloudKit','Parent of source recordings and clips. Imported bout number is the full-order sequence, not only this fencer’s count.'),
('SourceRecording','boutID; recordedAt; duration; cloudPhotoAssetID','Metadata syncs; working path and device ID stay local','Original bytes remain in Photos. The cloud Photos identifier can reconnect the same asset across devices.'),
('ReviewClip','boutID; sourceRecordingID; start/end; favorite','Metadata + CKAsset; export path is local','Each saved trim is independent. Ordering follows source capture time and clip start time, with deterministic tie-breakers.'),
('ScheduleExtractionRun','run ID; status; warnings; timing','Local SwiftData','Diagnostic state. Screenshots, recognized text and unconfirmed proposals are not uploaded.'),
('Managed media files','SourceRecordings / PendingClips / DownloadedClips','Device filesystem','Source working files, durable pending exports and downloaded cache copies have different lifetimes.'),
('Sync bookkeeping','engine state; record system fields; deletion IDs','Local persistence','Supports resumed changes, conflict handling and deletion recovery.')]
html.append('<section id="records"><div class="section-head"><span class="num">(08)</span><div><h2>The records behind the screen.</h2><p class="section-intro">Links use stable IDs. The app enforces parent-child behavior through repository and workflow code.</p></div></div><div class="table-wrap"><table><thead><tr><th>Record / resource</th><th>Key links or fields</th><th>Storage</th><th>Meaning</th></tr></thead><tbody>')
for row in records: html.append('<tr>'+''.join('<td>'+e(v)+'</td>' for v in row)+'</tr>')
html.append('</tbody></table></div><div class="note"><strong>Scope</strong><div>Current private MVP only. Voice coaching notes, transcription, AI summaries, scores, labels, automatic action recognition, public accounts and a custom backend are future ideas, not running components. The detailed <a href="../answer-me-with-html/architecture.html">earlier code guide</a> provides a complete function declaration index.</div></div></section>')
html.append('''<section id="design"><div class="section-head"><span class="num">(09)</span><div><h2>Design &amp; provenance.</h2><div class="receipt"><p>Created with <a href="https://github.com/cathrynlavery/diagram-design">Cathryn Lavery’s Diagram Design skill</a>: full editorial treatment, static inline SVG, a doc-wide 1280 × 720 canvas, and six nodes per figure. Detailed behavior lives beside each figure so labels remain readable. The architectural maps show selected calls and responsibilities, not every method or callback.</p><p>Visual reference: <a href="https://www.awwwards.com/sites/maria-vasilyeva-portfolio">Maria Vasilyeva’s Awwwards entry</a>, sampled from <a href="https://www.mariavasilyeva.com/">the linked portfolio</a>. Detected paper <code>#f9f9f9</code>, ink <code>#131313</code> and supporting gray <code>#585858</code>. Surface <code>#eeeeec</code> and rule <code>#b8b8b5</code> are derived. The focal treatment uses inverse black and white to retain the reference’s restrained monochrome palette.</p><p>Font receipt: the portfolio uses custom-hosted <code>feat</code>, <code>synt</code> and <code>suo</code>, sampled at weight 400. This artifact uses disclosed fallbacks: Instrument Serif for editorial headings, Geist for node names, and Geist Mono for technical labels, supplied by Google Fonts. It does not copy the portfolio’s custom font files. The page remains readable with local fallback fonts when offline.</p><p>Verified against app source at <code>92ab000</code> and the repository’s architecture, requirements, journey and accepted-build documents. Source links identify the Swift file and declaration line; local viewers may open the file without jumping to its line. The app’s executable code was not changed.</p></div></div></div></section><footer>Fencing Review / Architecture Atlas · Created 09 October 2026<br>Static HTML + SVG. No scripts, media uploads, account calls or embedded credentials. Fonts are the only remote rendering dependency.</footer></main></body></html>''')
content='\n'.join(html)
# The skill single-file checker disallows even remote navigation anchors.
# Keep citations as visible text here and clickable links in the companion README.
content=re.sub(r'<a href="(https://[^"]+)">(.*?)</a>', r'\2 (<span class="citation">\1</span>)', content)
(HERE/'architecture.html').write_text(content)
(HERE/'source-index.json').write_text(json.dumps(refs,indent=2)+'\n')
print(f'Built {len(chapters)} diagrams and {len(refs)} verified declaration references.')
