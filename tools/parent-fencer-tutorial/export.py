"""Package the validated segments as a full guide and seven individual lessons."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess,html
H=(FIGURES / 'parent-fencer-tutorial');C=runtime('parent-fencer-tutorial');T=json.loads((H/'timeline.json').read_text());P=json.loads((H/'edit-plan.json').read_text())
def run(args):subprocess.run(['ffmpeg','-v','error','-y',*args],check=True)
def stamp(t,sep=','):
 ms=round(t*1000);s,ms=divmod(ms,1000);m,s=divmod(s,60);h,m=divmod(m,60)
 return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
meta=';FFMETADATA1\n';cursor=0;links=[];captions=[];n=0
for ci,ch in enumerate(T['chapters']):
 plans=[p for p in P if p['chapter']==ci];duration=sum(p['duration'] for p in plans)
 meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(cursor*1000)}\nEND={round((cursor+duration)*1000)}\ntitle={ch["title"]}\n'
 listing=C/f'lesson-{ci+1}.txt';listing.write_text(''.join(f"file '{C/'segments'/f'{p['index']:03}.mp4'}'\n" for p in plans))
 name=f'lesson-{ci+1:02}.mp4'
 run(['-f','concat','-safe','0','-i',str(listing),'-ss',str(cursor),'-i',str(H/'narration.wav'),'-map','0:v','-map','1:a','-t',str(duration),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(H/name)])
 links.append(f'<li><button data-time="{cursor:.3f}"><span>{ci+1:02}</span>{html.escape(ch["title"])}</button><a href="{name}" download>Download lesson</a></li>')
 cursor+=duration
 for b in ch['beats']:
  n+=1;captions.append(f'{n}\n{stamp(b["start"])} --> {stamp(b["end"])}\n{b["text"]}\n')
(H/'captions.srt').write_text('\n'.join(captions));(C/'chapters.txt').write_text(meta)
listing=C/'full.txt';listing.write_text(''.join(f"file '{C/'segments'/f'{p['index']:03}.mp4'}'\n" for p in P))
run(['-f','concat','-safe','0','-i',str(listing),'-i',str(H/'narration.wav'),'-i',str(C/'chapters.txt'),'-map','0:v','-map','1:a','-map_metadata','2','-map_chapters','2','-t',str(cursor),'-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(H/'parent-fencer-guide.mp4')])
run(['-ss','12','-i',str(H/'parent-fencer-guide.mp4'),'-frames:v','1',str(H/'poster.png')])
(H/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fencing Review — Parent + Fencer Guide</title><style>*{box-sizing:border-box}body{margin:0;padding:40px;background:#f9f9f9;color:#131313;font:17px Georgia,serif}main{max-width:1400px;margin:auto}header{font:12px monospace;letter-spacing:.12em;border-bottom:1px solid #aaa;padding-bottom:20px}h1{font-size:clamp(36px,5vw,72px);font-weight:400;margin:30px 0 15px}p{color:#585858;line-height:1.6}video{width:100%;aspect-ratio:16/9;background:#131313}ol{list-style:none;padding:0}li{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #bbb;padding:16px 0;gap:20px}button{border:0;background:none;text-align:left;font:24px Georgia;cursor:pointer;color:#131313}button span{font:14px monospace;color:#777;margin-right:24px}a{color:#585858;font:14px sans-serif}button:hover,button:focus{color:#d53535}</style><main><header>FENCING REVIEW / PARENT + FENCER GUIDE</header><h1>Seven tasks. One clear guide.</h1><p>Real iPad simulator recordings, spoken instructions, red tap marks, and magnified controls. Fictional names and demo media.</p><video id="player" controls preload="metadata" poster="poster.png" src="parent-fencer-guide.mp4"></video><p><a href="parent-fencer-guide.mp4" download>Download the full guide</a> · <a href="narration.md">Read the script</a> · <a href="captions.srt" download>Download captions</a></p><ol>'''+''.join(links)+'''</ol><p>This demonstration uses simulated cloud services. It shows the app’s intended storage behavior; it does not verify live iCloud synchronization.</p></main><script>const v=document.querySelector('video');document.querySelectorAll('button').forEach(b=>b.onclick=()=>{v.currentTime=Number(b.dataset.time);v.play();v.scrollIntoView({behavior:'smooth',block:'center'});});</script></html>''')
print(f'Exported {cursor:.2f}s and seven lessons.')
