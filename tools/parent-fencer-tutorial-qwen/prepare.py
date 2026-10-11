"""Build a frame-aligned video clock without changing the approved speech."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import copy
import json
import math
import re
import wave

H = (FIGURES / 'parent-fencer-tutorial-qwen')
A = H.parent / 'local-qwen-narration/instructional'
old = json.loads((H.parent / 'parent-fencer-tutorial-paced/timeline.json').read_text())
audio = json.loads((A / 'generation-report.json').read_text())
aligned = {a['file']: a for a in json.loads((H / 'alignment.json').read_text())}
actions = {e['label'] for e in json.loads((H.parent / 'parent-fencer-tutorial/capture-events.json').read_text()) if e['kind'] in ('tap', 'drag')}
RATE = 24000
units, chapters, chunks = [], [], []
cursor = 0
index = 0

def read(path):
    with wave.open(str(path)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (RATE, 1, 2)
        return w.readframes(w.getnframes())

def add(kind, ci, duration, pcm=b'', **extra):
    global cursor
    frames = math.ceil(duration * 30 - 1e-7)
    samples = frames * 800
    assert len(pcm) // 2 <= samples
    u = {'kind': kind, 'chapter': ci, 'start': cursor / 30, 'duration': frames / 30, **extra}
    units.append(u)
    chunks.append(pcm + bytes(samples * 2 - len(pcm)))
    cursor += frames
    return u

def words(segment, offset):
    source = aligned[segment['file']]['words']
    tokens = segment['text'].split()
    norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
    assert ''.join(map(norm, tokens)) == ''.join(norm(w['word']) for w in source)
    spans = []
    char = 0
    for w in source:
        end = char + len(norm(w['word']))
        spans.append((char, end, w))
        char = end
    result = []
    char = 0
    for token in tokens:
        end = char + len(norm(token))
        matches = [w for a, b, w in spans if a < end and b > char]
        start, stop = matches[0]['start'], matches[-1]['end']
        # Aligner has 80 ms resolution. Show zero-length function words for
        # one frame, centred as closely as possible on the measured boundary.
        if stop <= start:
            start = max(0, start - 1 / 60)
            stop = start + 1 / 30
        result.append({'word': token, 'start': offset + start, 'end': offset + stop})
        char = end
    return result

for ci, (chapter, lesson) in enumerate(zip(old['chapters'], audio)):
    ch = {'title': chapter['title'], 'start': cursor / 30, 'beats': []}
    if ci:
        add('transition', ci, .5, label=f'to-title-{ci + 1}')
    title = lesson['segments'][0]
    pcm = read(A / title['file'])
    u = add('title', ci, .3 + title['audioSeconds'] + title['addedPauseSeconds'],
            bytes(round(.3 * RATE) * 2) + pcm, label=f'title-{ci + 1}', text=title['text'],
            audioFile=str(A / title['file']), speechOffset=.3, speechDuration=title['audioSeconds'])
    u['words'] = words(title, u['start'] + .3)
    ch['titleCard'] = u
    add('transition', ci, .5, label=f'to-demo-{ci + 1}')
    assert len(chapter['beats']) == len(lesson['segments']) - 1
    for prior, segment in zip(chapter['beats'], lesson['segments'][1:]):
        assert prior['text'] == segment['text']
        pcm = read(A / segment['file'])
        u = add('step', ci, segment['audioSeconds'] + segment['addedPauseSeconds'], pcm,
                index=index, label=prior['label'], audioFile=str(A / segment['file']))
        b = copy.deepcopy(prior)
        b.update(start=u['start'], end=u['start'] + u['duration'],
                 speechDuration=segment['audioSeconds'],
                 freezeDuration=1 if b['label'] in actions else 0,
                 readingPause=u['duration'] - segment['audioSeconds'],
                 words=words(segment, u['start']))
        ch['beats'].append(b)
        index += 1
    ch.update(end=cursor / 30, duration=cursor / 30 - ch['start'])
    chapters.append(ch)
with wave.open(str(H / 'narration.wav'), 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(RATE)
    for chunk in chunks:
        w.writeframes(chunk)
(H / 'timeline.json').write_text(json.dumps({'title': old['title'], 'duration': cursor / 30, 'chapters': chapters}, indent=2) + '\n')
(H / 'sequence.json').write_text(json.dumps(units, indent=2) + '\n')
(H / 'narration.md').write_text('# Parent and fencer guide — Qwen instructional edition\n\n' + '\n\n'.join('## ' + c['title'] + '\n\n' + c['titleCard']['text'] + '\n\n' + '\n\n'.join(b['text'] for b in c['beats']) for c in chapters) + '\n')
print(f'Prepared {cursor / 30:.2f}s. Speech samples unchanged; silence added only for transitions and frame boundaries.')
