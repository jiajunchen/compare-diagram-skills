"""Verify pauses, unchanged speech samples, and preservation of earlier outputs."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib
import json
import subprocess
import wave
from generate import RATE, pcm, silence

HERE = (FIGURES / 'local-qwen-narration/instructional')
ROOT = HERE.parents[2]
report = json.loads((HERE / 'generation-report.json').read_text())
checks = []
full = bytearray()
for lesson in report:
    expected = bytearray(silence(.3))
    for segment in lesson['segments']:
        assert abs(segment['startSeconds'] - len(expected) / (RATE * 2)) < 1 / RATE
        assert segment['request']['speed'] == 1.0
        expected.extend(pcm(HERE / segment['file']))
        expected.extend(silence(segment['addedPauseSeconds']))
    actual = pcm(HERE / lesson['file'])
    assert actual == expected, 'Speech samples or pauses changed during assembly'
    full.extend(actual)
    checks.append({'lesson': lesson['lesson'], 'segments': len(lesson['segments']),
                   'seconds': len(actual) / (RATE * 2), 'speechSamplesUnchanged': True,
                   'pausesVerified': True})
for filename, digest in json.loads((HERE / 'preserved-originals.json').read_text()).items():
    with (ROOT / filename).open('rb') as original:
        assert hashlib.file_digest(original, 'sha256').hexdigest() == digest, filename
if len(report) == 7:
    assert pcm(HERE / 'instructional-narration.wav') == full
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(HERE / 'instructional-narration.mp3'), '-f', 'null', '-'], check=True)
result = {'lessons': checks, 'originalAudioAndVideosUnchanged': True,
          'timeStretching': False, 'pitchShifting': False,
          'note': 'Checks establish assembly correctness, not subjective voice suitability.'}
(HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
