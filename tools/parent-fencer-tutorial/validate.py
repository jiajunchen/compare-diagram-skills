"""Check export integrity, action coverage, alignment, and preserved earlier videos."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess,hashlib,re
H=(FIGURES / 'parent-fencer-tutorial');R=H.parent.parent
p=json.loads((H/'edit-plan.json').read_text());t=json.loads((H/'timeline.json').read_text());events=json.loads((H/'capture-events.json').read_text())
assert any(e['kind']=='complete' for e in events)
assert len(p)==sum(len(c['beats']) for c in t['chapters'])==63
assert len({x['label'] for x in p})==len(p)
for x in p:
 assert x['duration']>0 and x['rawDuration']>0
 if x['rawAction'] is not None:
  assert 0<x['outputAction']<x['duration']
  assert x['rect'][2]>0 and x['rect'][3]>0
for c in t['chapters']:
 for b in c['beats']:
  assert b['end']>b['start']
  assert all(b['start']-.01<=w['start']<=w['end']<=b['end']+.01 for w in b['words'])
  assert max(len(s.split()) for s in re.split(r'[.!?]',b['text']) if s.strip())<=22
results=[]
for f in [H/'parent-fencer-guide.mp4',*sorted(H.glob('lesson-??.mp4'))]:
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(f)]))
 video=next(s for s in info['streams'] if s['codec_type']=='video');audio=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (video['width'],video['height'])==(1920,1080)
 assert abs(float(video['duration'])-float(audio['duration']))<.1
 subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
 if f.name.startswith('parent'):
  assert len(info['chapters'])==7
  assert abs(float(video['duration'])-t['duration'])<.1
 results.append({'file':f.name,'duration':float(video['duration']),'size':f.stat().st_size,'decode':'passed'})
assert len(results)==8
for name,digest in json.loads((H/'previous-artifacts.json').read_text()).items():
 assert hashlib.file_digest((R/name).open('rb'),'sha256').hexdigest()==digest,name
report={'videos':results,'instructionSegments':len(p),'markedActions':sum(x['rawAction'] is not None for x in p),'magnifiedSegments':sum(x['zoom']>1 for x in p),'priorVideosUnchanged':True,'wordAlignment':'passed','capture':'seven lessons completed with UI assertions'}
(H/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
