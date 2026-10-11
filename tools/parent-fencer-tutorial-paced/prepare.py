"""Build one master clock for titles, silent transitions, speech and reading pauses."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,math,wave,copy,html
from playwright.sync_api import sync_playwright
H=(FIGURES / 'parent-fencer-tutorial-paced');OLD=H.parent/'parent-fencer-tutorial';C=runtime('parent-fencer-tutorial-paced');C.mkdir(exist_ok=True)
original=json.loads((OLD/'timeline.json').read_text());titles=json.loads((H/'title-timeline.json').read_text());actions={e['label'] for e in json.loads((OLD/'capture-events.json').read_text()) if e['kind'] in ['tap','drag']}
def readwav(p):
 with wave.open(str(p)) as w:
  assert (w.getframerate(),w.getnchannels(),w.getsampwidth())==(44100,1,2)
  return w.readframes(w.getnframes())
old_audio=readwav(OLD/'narration.wav');title_audio=readwav(H/'title-narration.wav')
units=[];chapters=[];cursor=0;index=0;chunks=[]
results={'tournament-ready','schedule-ready','manual-ready','recordings-ready','clip-star-meaning','bout-star-meaning','delete-warning','one-clip-remains','bout-no-favorite','storage-counters','storage-warning','storage-result','finish','review-schedule','review-video-import'}
def add(kind,duration,ci,pcm=b'',**extra):
 global cursor
 frames=round(duration*30);samples=frames*1470
 assert len(pcm)//2<=samples
 unit={'kind':kind,'chapter':ci,'start':cursor/30,'duration':frames/30,**extra};units.append(unit);chunks.append(pcm+bytes(samples*2-len(pcm)));cursor+=frames;return unit
for ci,ch in enumerate(original['chapters']):
 chapter={'title':titles['chapters'][ci]['title'],'start':cursor/30,'beats':[]}
 if ci:add('transition',.5,ci,label=f'to-title-{ci+1}')
 title=titles['chapters'][ci];pcm=title_audio[round(title['start']*44100)*2:round(title['end']*44100)*2]
 unit=add('title',math.ceil((.6+len(pcm)/88200+.6)*30)/30,ci,bytes(round(.6*44100)*2)+pcm,label=f'title-{ci+1}',text=title['beats'][0]['text'])
 chapter['titleCard']=unit
 add('transition',.5,ci,label=f'to-demo-{ci+1}')
 for old in ch['beats']:
  speech=math.ceil((old['end']-old['start'])*30)/30;freeze=1 if old['label'] in actions else 0;pause=2 if old['label'] in results else 1
  pcm=old_audio[round(old['start']*44100)*2:round(old['end']*44100)*2]
  unit=add('step',speech+freeze+pause,ci,pcm,index=index,label=old['label'])
  b=copy.deepcopy(old);shift=unit['start']-old['start'];b.update(start=unit['start'],end=unit['start']+unit['duration'],speechDuration=speech,freezeDuration=freeze,readingPause=pause)
  for word in b['words']:word['start']+=shift;word['end']+=shift
  chapter['beats'].append(b);index+=1
 chapter['end']=cursor/30;chapter['duration']=chapter['end']-chapter['start'];chapters.append(chapter)
with wave.open(str(H/'narration.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(44100)
 for chunk in chunks:w.writeframes(chunk)
(H/'timeline.json').write_text(json.dumps({'title':original['title'],'duration':cursor/30,'chapters':chapters},indent=2)+'\n')
(H/'sequence.json').write_text(json.dumps(units,indent=2)+'\n')
(H/'narration.md').write_text('# Parent and fencer guide — paced edition\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+c['titleCard']['text']+'\n\n'+'\n\n'.join(b['text'] for b in c['beats']) for c in chapters)+'\n')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);page=browser.new_page(viewport={'width':1920,'height':1080})
 for ci,ch in enumerate(chapters):
  page.set_content('''<html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Geist+Mono&display=swap" rel="stylesheet"><style>*{box-sizing:border-box}body{margin:0;background:#f9f9f9;color:#131313}header{position:absolute;left:80px;right:80px;top:55px;border-bottom:1px solid #b8b8b5;padding-bottom:25px;display:flex;justify-content:space-between;font:16px 'Geist Mono',monospace;letter-spacing:.1em}.number{position:absolute;left:100px;top:275px;color:#d53535;font:38px 'Geist Mono',monospace}h1{position:absolute;left:100px;top:350px;width:1650px;margin:0;font:118px/1.06 'Instrument Serif',Georgia,serif;letter-spacing:-.02em}footer{position:absolute;left:100px;right:100px;bottom:75px;border-top:1px solid #b8b8b5;padding-top:24px;font:20px 'Geist Mono',monospace;color:#585858}</style><header><span>FENCING REVIEW / PARENT + FENCER GUIDE</span><span>'''+f'DEMONSTRATION {ci+1:02} / 07'+'''</span></header><div class="number">'''+f'No. {ci+1:02}'+'''</div><h1>'''+html.escape(ch['title'])+'''</h1><footer>Fictional names · Demo media · iPad walkthrough</footer></html>''')
  page.evaluate('document.fonts.ready');page.screenshot(path=str(assets('parent-fencer-tutorial-paced') / f'title-{ci:02}.png'))
 browser.close()
print(f'Prepared {cursor/30:.2f}s, seven titles, {len(actions)} one-second tap holds, and 63 reading pauses.')
