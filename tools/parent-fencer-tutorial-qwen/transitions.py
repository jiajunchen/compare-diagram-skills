"""Render seven editorial title pages and thirteen half-second slide transitions."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess
from concurrent.futures import ThreadPoolExecutor
from caption_style import header, transcript
H=(FIGURES / 'parent-fencer-tutorial-qwen');C=runtime('parent-fencer-tutorial-qwen');units=json.loads((H/'sequence.json').read_text())
def run(args):subprocess.run(['ffmpeg','-v','error','-y',*args],check=True)
for i,u in enumerate(units):
 u['file']=str(C/'segments'/f'{u["index"]:03}.mp4') if u['kind']=='step' else str(C/f'part-{i:03}.mp4')
def title(u):
 ass=C/f'title-words-{u["chapter"]:02}.ass'
 ass.write_text(header()+transcript(u['words'],u['start'],u['duration'],x=100,y=875,size=28,width=100))
 run(['-loop','1','-framerate','30','-i',str(assets('parent-fencer-tutorial-paced') / f'title-{u["chapter"]:02}.png'),'-t',str(u['duration']),'-vf',f"ass='{ass}':fontsdir='{(assets('parent-fencer-tutorial') / 'fonts')}'",'-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','3',u['file']])
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(title,[u for u in units if u['kind']=='title']))
def transition(i):
 u=units[i];a=C/f'transition-{i:03}-from.png';b=C/f'transition-{i:03}-to.png'
 run(['-sseof','-0.1','-i',units[i-1]['file'],'-frames:v','1',str(a)])
 run(['-i',units[i+1]['file'],'-frames:v','1',str(b)])
 run(['-loop','1','-framerate','30','-i',str(a),'-loop','1','-framerate','30','-i',str(b),'-filter_complex','[0:v]settb=AVTB,format=yuv420p[a];[1:v]settb=AVTB,format=yuv420p[b];[a][b]xfade=transition=slideleft:duration=0.5:offset=0[out]','-map','[out]','-t','0.5','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-threads','3',u['file']])
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(transition,[i for i,u in enumerate(units) if u['kind']=='transition']))
(H/'sequence.json').write_text(json.dumps(units,indent=2)+'\n')
print('Seven title cards and thirteen slide transitions rendered.')
