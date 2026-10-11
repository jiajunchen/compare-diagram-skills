"""Encode the chaptered video from validated frames and aligned narration."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess
HERE=(FIGURES / 'editorial-architecture-original')
data=json.loads((HERE/'timeline.json').read_text())
checks=json.loads((HERE/'frame-validation.json').read_text())
assert not checks['overflows'] and not checks['browserErrors']
output=HERE/'architecture-video.mp4'
subprocess.run(['ffmpeg','-hide_banner','-loglevel','warning','-y',
 '-safe','0','-f','concat','-i',str(runtime('editorial-architecture-original')/'frames.ffconcat'),
 '-i',str(HERE/'narration.wav'),'-i',str(runtime('editorial-architecture-original')/'chapters.ffmeta'),
 '-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2',
 '-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','18',
 '-pix_fmt','yuv420p','-r','30','-threads','6','-c:a','aac','-b:a','160k',
 '-t',str(data['duration']),'-movflags','+faststart','-progress',str(runtime('editorial-architecture-original')/'encode-progress.txt'),str(output)],check=True)
print(f'Encoded {output.name}: {output.stat().st_size:,} bytes')
