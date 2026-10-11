"""Measure word times from the approved audio with a local forced aligner."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json
import os
import dataclasses

HERE = (FIGURES / 'parent-fencer-tutorial-qwen')
AUDIO = HERE.parent / 'local-qwen-narration/instructional'
os.environ['HF_HOME'] = str((QWEN / 'huggingface'))
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
from mlx_audio.stt.utils import load_model
import mlx.core as mx

model_id = 'mlx-community/Qwen3-ForcedAligner-0.6B-8bit'
model = load_model(model_id)
results = []
for lesson in json.loads((AUDIO / 'generation-report.json').read_text()):
    for segment in lesson['segments']:
        path = AUDIO / segment['file']
        cache = runtime('parent-fencer-tutorial-qwen') / (path.stem + '-alignment.json')
        if cache.exists():
            item = json.loads(cache.read_text())
        else:
            result = model.generate(audio=str(path), text=segment['text'], language='English')
            item = {'file': segment['file'], 'text': segment['text'],
                    'audioSeconds': segment['audioSeconds'], 'model': model_id,
                    'words': [{'word': w.text, 'start': w.start_time, 'end': w.end_time} for w in result.items]}
            assert item['words']
            cache.write_text(json.dumps(item, indent=2) + '\n')
            mx.clear_cache()
        results.append(item)
        print(f'Aligned {len(results)}/70: {path.stem}', flush=True)
(HERE / 'alignment.json').write_text(json.dumps(results, indent=2) + '\n')
