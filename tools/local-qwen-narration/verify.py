"""Check local narration files and preserve the existing videos."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request
import wave
import numpy as np

HERE = (FIGURES / 'local-qwen-narration')
ROOT = HERE.parent.parent
report = {'audio': [], 'videosUnchanged': True}
for path in sorted(HERE.glob('*.wav')):
    with wave.open(str(path)) as audio:
        assert audio.getnchannels() == 1
        assert audio.getsampwidth() == 2
        assert audio.getframerate() == 24000
        samples = np.frombuffer(audio.readframes(audio.getnframes()), dtype='<i2').astype(float) / 32768
    assert len(samples) > 24000 and np.max(np.abs(samples)) > .01
    silence = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(path), '-af', 'silencedetect=noise=-45dB:d=2', '-f', 'null', '-'], capture_output=True, text=True, check=True)
    report['audio'].append({
        'file': path.name,
        'longSilenceEvents': [line.split('] ', 1)[-1] for line in silence.stderr.splitlines() if 'silence_' in line],
        'durationSeconds': len(samples) / 24000,
        'peakAmplitude': float(np.max(np.abs(samples))),
        'rmsAmplitude': float(np.sqrt(np.mean(samples ** 2))),
        'clippedSamples': int(np.sum(np.abs(samples) >= 32767 / 32768)),
    })
for filename, expected in json.loads((HERE / 'preserved-videos.json').read_text()).items():
    with (ROOT / filename).open('rb') as source:
        assert hashlib.file_digest(source, 'sha256').hexdigest() == expected, filename
subprocess.run(['ffmpeg', '-v', 'error', '-i', str(HERE / 'qwen-narration.mp3'), '-f', 'null', '-'], check=True)
with urllib.request.urlopen('http://127.0.0.1:8765/v1/models') as response:
    report['serverModels'] = json.load(response)
pid = json.loads((runtime('local-qwen-narration') /'server.json').read_text())['pid']
summary = subprocess.run(['vmmap', '-summary', str(pid)], capture_output=True, text=True, check=True).stdout
report['memoryFootprint'] = [line for line in summary.splitlines() if line.startswith('Physical footprint')]
report['limitations'] = ['Signal and decode checks do not establish pronunciation quality.', 'Process RSS omits much of the Metal memory; use macOS physical footprint for memory assessment.']
(HERE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
