"""Check exact speech preservation, timeline continuity, and measured word bounds."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json
import wave
from caption_style import transcript

H = (FIGURES / 'parent-fencer-tutorial-qwen')
T = json.loads((H / 'timeline.json').read_text())
U = json.loads((H / 'sequence.json').read_text())
with wave.open(str(H / 'narration.wav')) as w:
    assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (24000, 1, 2)
    combined = w.readframes(w.getnframes())
assert len(combined) / 48000 == T['duration']
cursor = 0
passages = 0
for u in U:
    assert abs(u['start'] - cursor) < 1e-6
    if 'audioFile' in u:
        with wave.open(u['audioFile']) as w:
            source = w.readframes(w.getnframes())
        start = round((u['start'] + u.get('speechOffset', 0)) * 24000) * 2
        assert combined[start:start + len(source)] == source
        passages += 1
    cursor += u['duration']
words = 0
for chapter in T['chapters']:
    for passage in [chapter['titleCard'], *chapter['beats']]:
        speech_start = passage['start'] + passage.get('speechOffset', 0)
        for word in passage['words']:
            assert speech_start <= word['start'] < word['end'] <= speech_start + passage['speechDuration']
            words += 1
# A real silent gap must have no red active word, unlike a continuous karaoke sweep.
sample = transcript([{'word': 'Tap', 'start': .2, 'end': .4}, {'word': 'Save.', 'start': .7, 'end': 1.1}], 0, 2)
gap = next(line for line in sample.splitlines() if ',0:00:00.40,0:00:00.70,' in line)
assert '2626B3' not in gap and '\\u1' not in gap
assert passages == 70
report = {'passages': passages, 'alignedWords': words, 'durationSeconds': T['duration'],
          'exactSpeechSamplesPreserved': True, 'continuousFrameClock': True,
          'highlightClearsDuringPauses': True,
          'alignmentResolutionSeconds': .08, 'zeroLengthFunctionWordDisplaySeconds': 1 / 30}
(H / 'timing-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
