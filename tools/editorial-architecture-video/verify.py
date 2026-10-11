"""Verify video, speech timing, chapter markers, and preservation of prior artifacts."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib,json,re,statistics,subprocess
HERE=(FIGURES / 'editorial-architecture-video');ROOT=HERE.parent.parent
story=json.loads((HERE/'storyboard.json').read_text());timeline=json.loads((HERE/'timeline.json').read_text())
beats=[b for c in timeline['chapters'] for b in c['beats']]
assert [b['text'] for b in beats]==[b['text'] for c in story['chapters'] for b in c['beats']]
assert all(b['start']<b['end'] for b in beats)
assert all(abs(a['end']-b['start'])<.001 for a,b in zip(beats,beats[1:]))
sentences=[s for b in beats for s in re.split(r'(?<=[.!?])\s+',b['text'])]
counts=[len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b",s)) for s in sentences]
assert max(counts)<=20
language={'profile':'STE-inspired practical 80% target, not formal conformity','chapters':len(story['chapters']),'beats':len(beats),'words':sum(counts),'sentences':len(sentences),'averageWordsPerSentence':round(statistics.mean(counts),1),'maximumWordsPerSentence':max(counts)}
assert language==json.loads((HERE/'language-validation.json').read_text())
preserved={}
for name,digest in json.loads((HERE/'previous-artifacts.json').read_text()).items():
 preserved[name]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
assert all(preserved.values())
file=HERE/'architecture-video.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(file)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1920,1080)
assert v['codec_name']=='h264' and a['codec_name']=='aac'
assert len(probe['chapters'])==len(story['chapters'])
assert abs(float(probe['format']['duration'])-timeline['duration'])<.1
for expected,actual in zip(timeline['chapters'],probe['chapters']):
 assert expected['title']==actual['tags']['title']
 assert abs(expected['start']-float(actual['start_time']))<.05
subprocess.run(['ffmpeg','-v','error','-i',str(file),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
report={'durationSeconds':float(probe['format']['duration']),'width':1920,'height':1080,'frameRate':v['avg_frame_rate'],'videoCodec':v['codec_name'],'audioCodec':a['codec_name'],'bytes':file.stat().st_size,'chapters':len(probe['chapters']),'alignedNarrationBeats':len(beats),'fullDecode':'passed','previousArtifactsUnchanged':preserved,'language':language}
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
