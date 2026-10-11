"""Recover the original technical narration from Git and the retained audio cache."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import wave

H = (FIGURES / 'editorial-architecture-original')
ROOT = H.parents[1]
REV = '7179657'
def historical(name):
    return subprocess.check_output(['git', 'show', f'{REV}:figures/architecture-video/{name}'], cwd=ROOT).decode()

source = historical('architecture-video.md')
srt = historical('architecture-video.srt')
chapters = json.loads(historical('chapters.json'))
(H / 'original-script.md').write_text(source)
(H / 'original-captions.srt').write_text(srt)
(H / 'original-chapters.json').write_text(json.dumps(chapters, indent=2) + '\n')

def seconds(value):
    h, m, s = value.replace(',', '.').split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)

captions = []
for block in srt.strip().split('\n\n'):
    _, times, text = block.split('\n', 2)
    a, b = times.split(' --> ')
    captions.append({'text': text, 'speechStart': seconds(a), 'speechEnd': seconds(b)})
quoted = [re.sub(r'\[([^]]+)\]', r'\1', line[2:]) for line in source.splitlines() if line.startswith('> ')]
assert quoted == [b['text'] for b in captions]
assert len(captions) == 62 and len(chapters) == 13
wav = Path('/tmp/sports-architecture-narration.wav')
with wave.open(str(wav)) as w:
    assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (22050, 1, 2)
    pcm = w.readframes(w.getnframes())
    duration = w.getnframes() / w.getframerate()
assert abs(duration - json.loads(historical('validation.json'))['durationSeconds']) < .001
provider = 'elevenlabs:JBFqnCBsd6RMkjVDRZzb:eleven_multilingual_v2'
checked = 0
for b in captions:
    key = hashlib.sha1((provider + '\n' + b['text']).encode()).hexdigest()
    file = Path.home() / '.answer-me-with-html/cache/tts' / (key + '.pcm')
    assert file.exists(), file
    voice = file.read_bytes()
    estimated = round(b['speechStart'] * 22050) * 2
    # Subtitle precision is 1 ms. Search a +/-2 ms window around that boundary.
    start = max(0, estimated - 100)
    found = pcm.find(voice, start, estimated + 100 + len(voice))
    assert found >= 0, b['text']
    b['exactSpeechStart'] = found / 44100
    b['exactSpeechEnd'] = (found + len(voice)) / 44100
    checked += 1
shutil.copy2(wav, H / 'narration.wav')
(H / 'recovered-passages.json').write_text(json.dumps(captions, indent=2) + '\n')
(H / 'recovery-validation.json').write_text(json.dumps({'sourceCommit': REV, 'chapters': 13, 'passages': 62,
    'durationSeconds': duration, 'originalTextMatches': True, 'speechCacheMatches': checked,
    'audioSHA256': hashlib.sha256(wav.read_bytes()).hexdigest(), 'newSpeechRequests': 0}, indent=2) + '\n')
prior = {}
for parent in ['architecture-video', 'editorial-architecture-video', 'parent-fencer-tutorial', 'parent-fencer-tutorial-paced', 'parent-fencer-tutorial-qwen']:
    for file in (H.parent / parent).glob('*.mp4'):
        prior[str(file.relative_to(ROOT))] = hashlib.file_digest(file.open('rb'), 'sha256').hexdigest()
(H / 'preserved-videos.json').write_text(json.dumps(prior, indent=2) + '\n')
print(f'Recovered {duration:.3f}s. All {checked} original speech passages match cached PCM exactly.')
