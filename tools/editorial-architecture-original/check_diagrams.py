
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json
import re
import subprocess
import tempfile
H = (FIGURES / 'editorial-architecture-original')
skill = Path('/tmp/sports-diagram-design')
subprocess.run(['python3', str(skill / 'skills/diagram-design/scripts/self_check.py'), str(H / 'presentation.html')], check=True)
checks = []
source = (runtime('editorial-architecture-original') /'atlas.html').read_text()
with tempfile.TemporaryDirectory() as tmp:
    for slug in sorted(set(c['diagram'] for c in json.loads((H / 'storyboard.json').read_text())['chapters']) - {'intro'}):
        section = re.search(r'<section id="' + slug + r'">(.*?)</section>', source, re.S).group(1)
        svg = re.search(r'<svg.*?</svg>', section, re.S).group(0)
        file = Path(tmp) / (slug + '.html')
        file.write_text(svg.replace('><', '>\n<'))
        result = subprocess.run(['python3', str(skill / 'scripts/verify-geometry.py'), str(file)], capture_output=True, text=True)
        assert result.returncode == 0, result.stdout + result.stderr
        checks.append({'diagram': slug, 'geometry': 'passed'})
(H / 'diagram-validation.json').write_text(json.dumps({'skillSelfCheck': 'passed', 'figures': checks}, indent=2) + '\n')
print(f'{len(checks)} diagrams passed geometry checks.')
