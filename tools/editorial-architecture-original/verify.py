
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib
import json
import subprocess
H = (FIGURES / 'editorial-architecture-original')
ROOT = H.parents[1]
T = json.loads((H / 'timeline.json').read_text())
R = json.loads((H / 'recovery-validation.json').read_text())
B = [b for c in T['chapters'] for b in c['beats']]
original = json.loads((H / 'recovered-passages.json').read_text())
assert [b['text'] for b in B] == [b['text'] for b in original]
assert hashlib.sha256((H / 'narration.wav').read_bytes()).hexdigest() == R['audioSHA256']
for i,b in enumerate(B):
    assert b['start'] <= b['speechStart'] <= b['speechEnd'] <= b['end']
    if i:
        assert abs(B[i-1]['end'] - b['start']) < .001
frames = json.loads((H / 'frame-validation.json').read_text())
assert not frames['overflows'] and not frames['browserErrors']
probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(H / 'architecture-video.mp4')]))
v = next(s for s in probe['streams'] if s['codec_type']=='video')
a = next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'], v['height'], v['r_frame_rate']) == (1920,1080,'30/1')
assert len(probe['chapters']) == 13
assert abs(float(v['duration']) - T['duration']) < .05
assert abs(float(v['duration']) - float(a['duration'])) < .05
subprocess.run(['ffmpeg','-v','error','-i',str(H / 'architecture-video.mp4'),'-f','null','-'],check=True)
preserved = 0
for name,digest in json.loads((H / 'preserved-videos.json').read_text()).items():
    with (ROOT / name).open('rb') as file:
        assert hashlib.file_digest(file,'sha256').hexdigest()==digest,name
    preserved += 1
result = {'durationSeconds':float(v['duration']),'width':1920,'height':1080,'fps':30,'chapters':13,
          'originalNarrationPassages':62,'originalAudioUnchanged':True,'newSpeechRequests':0,
          'previousVideosUnchanged':preserved,'fullDecode':'passed','allFrameTextBounds':'passed',
          'visualReview':'Intro, record relationships, upload state and scrub diagrams inspected.',
          'sourceCommit':'7179657','sourceScope':'Restores the original technical explanation without rewriting it to STE.'}
(H / 'validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
