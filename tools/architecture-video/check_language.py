"""Measure the revision's plain-language targets; this is not a full STE dictionary audit."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json
import re
import statistics

HERE = (FIGURES / 'architecture-video')
source = (HERE / 'architecture-video.md').read_text()
beats = [line[2:].replace('[', '').replace(']', '') for line in source.splitlines() if line.startswith('> ')]
sentences = [s for beat in beats for s in re.split(r'(?<=[.!?])\s+', beat) if s]
counts = [len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", sentence)) for sentence in sentences]
assert 'style: 80' in source
assert max(counts) <= 20, [(n,s) for n,s in zip(counts,sentences) if n > 20]
assert not any(';' in beat for beat in beats)
assert max(len(re.split(r'(?<=[.!?])\s+', beat)) for beat in beats) <= 6
report = {
    'profile': 'Practical STE-inspired 80% target; no formal conformity percentage',
    'narrationBeats': len(beats), 'sentences': len(sentences), 'words': sum(counts),
    'averageWordsPerSentence': round(statistics.mean(counts), 1),
    'maximumWordsPerSentence': max(counts), 'sentencesOver20Words': sum(n > 20 for n in counts),
    'formalDictionaryAudit': False,
    'editorialChecks': ['App purpose and audience before code', 'One main idea per sentence',
        'Active voice', 'Roles before code names', 'Stable terms for original recording, recording link, and review clip',
        'Define record, identifier, draft, export, downloaded copy, and seek',
        'Use action order and clear conditions', 'Keep most function names in the diagrams']
}
(HERE / 'language-validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))

# A reading copy omits diagram syntax and focus markers.
title = re.search(r'^title: (.+)$', source, re.M).group(1)
reading = ['# ' + title, '']
for line in source.splitlines():
    if line.startswith('## '):
        reading.extend(['## ' + re.sub(r'^[A-Z] ', '', line[3:]), ''])
    elif line.startswith('> '):
        reading.extend([line[2:].replace('[', '').replace(']', ''), ''])
(HERE / 'narration.md').write_text('\n'.join(reading))
