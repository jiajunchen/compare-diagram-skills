"""Pair recovered technical narration with the approved editorial diagrams."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
from html import escape
import ast
import copy
import json
import re

H = (FIGURES / 'editorial-architecture-original')
atlas = (H.parent / 'diagram-design/architecture.html').read_text()
# Reuse only the existing SVG drawing function; do not execute the atlas build.
tree = ast.parse((TOOLS / 'diagram-design/build.py').read_text())
function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'diagram')
env = {'e': escape, 'PAPER': '#f9f9f9', 'INK': '#131313', 'MUTED': '#585858', 'SURFACE': '#eeeeec', 'RULE': '#b8b8b5'}
exec(compile(ast.Module(body=[function], type_ignores=[]), '<atlas-drawing-function>', 'exec'), env)
def n(title, code, detail, kind='service'):
    return [title, code, detail, kind]
custom = [
 {'id':'records-detail','title':'One bout, many recordings','intro':'Stable identifiers connect tournaments, bouts, original recordings and independently exported review clips.',
  'nodes':[n('Tournament','Tournament.id','The parent event','store'),n('Bout','tournamentID','Opponent + full-order bout number','focus'),n('Original recording link','SourceRecording.boutID','A reference to the original in Photos','store'),n('One fencer profile','AppSettings.fencerName','Global setting; not a media parent','store'),n('Independent review clip','sourceRecordingID + boutID','One time range from one source','store'),n('Ordered playback','reviewClips()','Capture time, clip start, identifier')],
  'edges':[(0,1,'OWNS'),(1,2,'CONTAINS'),(2,4,'TIME RANGE'),(4,5,'SORT')]},
 {'id':'upload-detail','title':'Metadata first, video second','intro':'A durable local export is queued before metadata synchronization and a separate CloudKit asset upload.',
  'nodes':[n('Durable pending queue','pendingUpload / resumePending()','Local export survives interruption','store'),n('Upload coordinator','upload() + in-flight set','Temporary failure returns to queue','focus'),n('Metadata record','synchronize()','Create destination before asset','store'),n('Needs attention','needsAttention / Retry Upload','Other failures require explicit retry','optional'),n('Available clip','available','Deletion waits for active upload','store'),n('Edited movie asset','saveExportedClip()','Direct CloudKit database save','external')],
  'edges':[(0,1,'RESUME'),(1,2,'METADATA',True),(2,5,'ATTACH FILE',True),(5,4,'SUCCESS',True),(1,3,'OTHER FAILURE',True)]},
 {'id':'scrub-detail','title':'Scrubbing follows the newest intent','intro':'A single in-flight seek and a replaceable pending target keep the picture aligned with the newest drag intent.',
  'nodes':[n('Timeline slider','scrub(to:) / finishScrub()','Drag to preview; release to finalize','input'),n('Player model','Clamp time; pause playhead updates','Retains half, normal or double speed'),n('Scrub coordinator','drag(to:)','At most one seek in flight','focus'),n('Lifetime checks','Generation + cancellation','Ignore old completions after switching'),n('AVPlayer seek','Preview 0.15s / final zero','Exact final target on release','external'),n('Newest pending target','Replace obsolete positions','No backlog of old drag requests','store')],
  'edges':[(0,1,'DRAG / RELEASE'),(1,2,'CLAMP'),(2,5,'REPLACE'),(5,4,'SEEK'),(4,3,'COMPLETION')]},
 {'id':'favorites-detail','title':'Keep meaning, release local bytes','intro':'Favorite metadata stays separate from media exports, while safe cleanup removes local copies and retains cloud assets.',
  'nodes':[n('Clip star','toggleClipFavorite()','No second movie export','input'),n('Favorite metadata','ReviewClip.isFavorite','Save and synchronize the flag','focus'),n('Bout star','Derived from favorite clips','Indicator; not a separate toggle','store'),n('Cloud clip remains','Download again on demand','Photos originals remain unchanged','external'),n('Offload checks','Available cloud asset required','Protect pending uploads and paths'),n('Local media copies','Uploaded exports + downloads','Global cleanup or bout unloading','store')],
  'edges':[(0,1,'TOGGLE'),(1,2,'DERIVE'),(5,4,'CHECK'),(4,3,'RETAIN')]}
]
for c in custom:
    atlas += '<section id="' + c['id'] + '">' + env['diagram'](c) + '</section>'
(runtime('editorial-architecture-original') /'atlas.html').write_text(atlas)
(H / 'additional-diagrams.json').write_text(json.dumps(custom, indent=2) + '\n')
chapters = json.loads((H / 'original-chapters.json').read_text())
passages = json.loads((H / 'recovered-passages.json').read_text())
diagrams = ['intro','records-detail','overview','startup','schedule','schedule','recordings','clips','upload-detail','playback','scrub-detail','sync','favorites-detail']
focuses = [[None,None],[1,2,4,5,3],[0,1,4,2,5],[1,2,3,3,4],[1,2,5,4,3],[3,3,3,3,3],[0,1,2,4,3],[0,1,2,5,1],[0,2,5,4,1],[1,2,2,5,4],[0,2,4,1,1],[0,1,1,3,4],[0,4,5,3,3]]
result = []
for i,c in enumerate(chapters):
    beats = [copy.deepcopy(b) for b in passages if c['startSeconds'] <= b['speechStart'] < c['endSeconds']]
    assert len(beats) == len(focuses[i]), (i, len(beats))
    for j,b in enumerate(beats):
        b.update(start=c['startSeconds'] if j==0 else b['speechStart'],
                 end=beats[j+1]['speechStart'] if j+1<len(beats) else c['endSeconds'], focus=focuses[i][j])
    result.append({'title':c['title'], 'diagram':diagrams[i], 'start':c['startSeconds'], 'end':c['endSeconds'], 'beats':beats})
story = {'title':'From Fencing Footage to Review — original narration, editorial diagrams', 'chapters':result,
         'sourceCommit':'7179657', 'narration':'Recovered original ElevenLabs audio; no new speech requests',
         'duration': json.loads((H / 'recovery-validation.json').read_text())['durationSeconds']}
(H / 'storyboard.json').write_text(json.dumps(story, indent=2) + '\n')
(H / 'timeline.json').write_text(json.dumps(story, indent=2) + '\n')
(H / 'narration.md').write_text('# Original technical narration\n\nRestored from commit 7179657, before the ASD-STE100 revision.\n\n' + '\n\n'.join('## ' + c['title'] + '\n\n' + '\n\n'.join(b['text'] for b in c['beats']) for c in result) + '\n')
print('Prepared 13 chapters and 62 original narration passages with editorial diagram mappings.')
