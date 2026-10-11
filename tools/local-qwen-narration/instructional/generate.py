"""Generate action-sized narration at native speed and add explicit pauses."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[2]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib
import io
import json
import subprocess
import sys
import time
import urllib.request
import wave

HERE = (FIGURES / 'local-qwen-narration/instructional')
CACHE = (FIGURES / 'local-qwen-narration/instructional/segments')
CACHE.mkdir(exist_ok=True)
MODEL = 'mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit'
RATE = 24000

def pcm(path):
    with wave.open(str(path)) as audio:
        assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) == (1, 2, RATE)
        return audio.readframes(audio.getnframes())

def save(path, data):
    with wave.open(str(path), 'wb') as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(RATE)
        audio.writeframes(data)

def silence(seconds):
    return bytes(round(seconds * RATE) * 2)

def synthesize(text, name):
    payload = {'model': MODEL, 'input': text, 'voice': 'Aiden',
               'lang_code': 'English', 'response_format': 'wav',
               'speed': 1.0, 'temperature': 0.3, 'repetition_penalty': 1.05,
               'max_tokens': 1024, 'verbose': False}
    # The small model's instruction control is not established. Use the preset
    # voice, complete sentences, and audio-level pauses rather than a style prompt.
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    out = CACHE / (name + '.wav')
    meta = CACHE / (name + '.json')
    if out.exists() and meta.exists():
        cached = json.loads(meta.read_text())
        if cached['hash'] == digest:
            return cached
    start = time.perf_counter()
    request = urllib.request.Request('http://127.0.0.1:8765/v1/audio/speech',
        data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=600) as response:
        data = response.read()
    with wave.open(io.BytesIO(data)) as audio:
        assert audio.getframerate() == RATE
        duration = audio.getnframes() / RATE
        assert 0.5 < duration < 70, (name, duration)
    out.write_bytes(data)
    result = {'file': str(out.relative_to(HERE)), 'hash': digest, 'text': text,
              'audioSeconds': duration, 'generationSeconds': time.perf_counter() - start,
              'request': payload}
    meta.write_text(json.dumps(result, indent=2) + '\n')
    print(f'{name}: {duration:.1f}s', flush=True)
    return result

def main():
    source = HERE.parent.parent / 'parent-fencer-tutorial-paced/timeline.json'
    chapters = json.loads(source.read_text())['chapters']
    limit = 1 if len(sys.argv) > 1 and sys.argv[1] == 'sample' else len(chapters)
    report = []
    full = bytearray()
    for i, chapter in enumerate(chapters[:limit], 1):
        parts = [chapter['titleCard']['text']] + [b['text'] for b in chapter['beats']]
        assembled = bytearray(silence(.3))
        segments = []
        for j, text in enumerate(parts):
            result = synthesize(text, f'lesson-{i:02}-part-{j:02}')
            result = dict(result)
            result['startSeconds'] = len(assembled) / (RATE * 2)
            assembled.extend(pcm(HERE / result['file']))
            # Added silence follows the model's natural sentence-end pause.
            pause = 1.2 if j == 0 else .8
            if any(word in text.lower() for word in ('check', 'confirm', 'delet', 'clears', 'favorite')):
                pause = 1.2
            if j == len(parts) - 1:
                pause = 2.0
            result['addedPauseSeconds'] = pause
            assembled.extend(silence(pause))
            segments.append(result)
        destination = HERE / f'lesson-{i:02}.wav'
        save(destination, assembled)
        report.append({'lesson': i, 'file': destination.name,
                       'audioSeconds': len(assembled) / (RATE * 2), 'segments': segments})
        full.extend(assembled)
        (HERE / 'generation-report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(f'Lesson {i} complete', flush=True)
    save(HERE / ('preview.wav' if limit == 1 else 'instructional-narration.wav'), full)
    if limit > 1:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(HERE / 'instructional-narration.wav'),
            '-c:a', 'libmp3lame', '-b:a', '192k', str(HERE / 'instructional-narration.mp3')], check=True)

if __name__ == '__main__':
    main()
