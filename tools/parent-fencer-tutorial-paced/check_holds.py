"""Verify a full second of identical captured frames for every marked action."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess
from concurrent.futures import ThreadPoolExecutor
H=(FIGURES / 'parent-fencer-tutorial-paced');C=runtime('parent-fencer-tutorial-paced');OLD=H.parent/'parent-fencer-tutorial';P=json.loads((H/'edit-plan.json').read_text())
def check(p):
 assert p['freezeDuration']==1
 target=p['outputAction'];assert target+.90 < target+p['freezeDuration']
 filters=(C/f'filter-{p["index"]:03}.txt').read_text().split(';\n[timed]ass=')[0]
 filters+=f';[timed]trim=start={target:.6f}:end={target+1:.6f},setpts=PTS-STARTPTS[check]'
 result=subprocess.run(['ffmpeg','-v','error','-ss',str(p['rawStart']),'-t',str(p['rawDuration']),'-i',str(runtime('parent-fencer-tutorial') /'capture-landscape-30fps.mp4'),'-filter_complex',filters,'-map','[check]','-an','-f','framemd5','-'],capture_output=True,text=True,check=True)
 frames=[line for line in result.stdout.splitlines() if line and not line.startswith('#')]
 hashes=[line.rsplit(',',1)[1].strip() for line in frames]
 assert len(hashes)==30,(p['label'],len(hashes))
 assert len(set(hashes))==1,(p['label'],'screen changes inside freeze')
 return {'label':p['label'],'identicalFrames':30,'freezeSeconds':1,'highlightEndsBeforeResume':True}
with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(check,[p for p in P if p['rawAction'] is not None]))
(H/'hold-validation.json').write_text(json.dumps(results,indent=2)+'\n');print(f'Passed: all {len(results)} marked actions hold 30 identical background frames.')
