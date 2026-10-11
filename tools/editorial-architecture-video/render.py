"""Render the existing editorial SVGs as timed 1080p presentation frames."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
from html import escape
import json,re,subprocess,math
from playwright.sync_api import sync_playwright
HERE=(FIGURES / 'editorial-architecture-video')
ATLAS=HERE.parent/'diagram-design'/'architecture.html'
source=ATLAS.read_text();story=json.loads((HERE/'storyboard.json').read_text())
timeline=json.loads((HERE/'timeline.json').read_text())
frames=runtime('editorial-architecture-video') / 'frames';frames.mkdir(parents=True, exist_ok=True)
FONT='https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500&display=swap'
css='''*{box-sizing:border-box}body{margin:0;background:#f9f9f9;color:#131313;font-family:Geist,Arial,sans-serif}.slide{width:1920px;height:1080px;position:relative;overflow:hidden;background:#f9f9f9;break-after:page}.top{position:absolute;top:44px;left:112px;right:112px;display:flex;justify-content:space-between;font:14px "Geist Mono",monospace;letter-spacing:.13em;border-bottom:1px solid #b8b8b5;padding-bottom:20px;text-transform:uppercase}h1{font:64px "Instrument Serif",Georgia,serif;line-height:1.04;letter-spacing:-.025em;position:absolute;left:112px;top:100px;margin:0}.diagram{position:absolute;left:128px;top:202px;width:1664px;height:676px}.diagram svg{display:block;width:1664px;height:676px}.svg-eyebrow,.legend{display:none}.type-tag{font:10px "Geist Mono",monospace;letter-spacing:.1em}.node-title{font:600 20px Geist,Arial,sans-serif}.node-code{font:12px "Geist Mono",monospace}.node-detail{font:13px Geist,Arial,sans-serif}.arrow-label{font:11px "Geist Mono",monospace;fill:#585858}.spotlight{fill:none;stroke:#131313;stroke-width:2;rx:10}.focus-label{position:absolute;left:116px;top:180px;font:14px "Geist Mono",monospace;color:#585858}.caption{position:absolute;left:144px;right:144px;top:920px;margin:0;text-align:center;font-size:31px;line-height:1.35;font-weight:400}.caption-rule{position:absolute;left:112px;right:112px;top:896px;border-top:1px solid #b8b8b5}.page{position:absolute;right:112px;bottom:24px;font:12px "Geist Mono",monospace;color:#585858}.hero{position:absolute;left:112px;top:228px;font:114px "Instrument Serif",Georgia,serif;line-height:.98;letter-spacing:-.04em;max-width:970px}.hero small{display:block;font:24px Geist,Arial,sans-serif;line-height:1.5;letter-spacing:0;margin-top:40px;max-width:760px}.storage{position:absolute;left:1216px;right:112px;top:228px}.storage div{padding:32px 0;border-top:1px solid #b8b8b5}.storage span{font:13px "Geist Mono",monospace;letter-spacing:.12em;color:#585858}.storage h2{font:44px "Instrument Serif",Georgia,serif;margin:12px 0}.storage p{font:20px Geist,Arial,sans-serif;margin:0;color:#585858}.complete-script{width:1100px;padding:80px;margin:auto;line-height:1.7}.complete-script h2{font:44px "Instrument Serif",Georgia,serif}@media print{.complete-script{break-before:page}}'''
slides=[]
for i,c in enumerate(story['chapters']):
 if c['diagram']=='intro':
  content='<div class="hero">From the piste<br>to the replay.<small>A parent’s recordings become a focused review session.<br>One fencer. Two devices. One private iCloud account.</small></div><div class="storage"><div><span>01 / ORIGINALS</span><h2>Photos</h2><p>The recordings stay unchanged.</p></div><div><span>02 / LOCAL WORK</span><h2>The device</h2><p>Drafts, records and pending files.</p></div><div><span>03 / SHARED REVIEW</span><h2>Private CloudKit</h2><p>Confirmed records and edited clips.</p></div></div>'
 else:
  section=re.search(r'<section id="'+c['diagram']+r'">(.*?)</section>',source,re.S).group(1)
  svg=re.search(r'<svg.*?</svg>',section,re.S).group(0)
  svg=svg.replace('viewBox="0 0 1280 720"','viewBox="0 72 1280 520"')
  # Repeated overview keeps isolated accessible IDs and marker URLs.
  slug=c['diagram'];new=f'chapter-{i}-{slug}'
  svg=svg.replace(slug+'-',new+'-')
  svg=svg.replace('</svg>','<rect class="spotlight" x="0" y="0" width="332" height="172" style="display:none" aria-hidden="true"/></svg>')
  content='<div class="diagram">'+svg+'</div>'
 slides.append(f'<article class="slide" id="slide-{i}"><div class="top"><span>Fencing Review / Architecture</span><span>Editorial edition · {i+1:02} / 09</span></div><h1>{escape(c["title"])}</h1><div class="focus-label"></div>{content}<div class="caption-rule"></div><p class="caption">{escape(c["beats"][0]["text"])}</p><div class="page">{i+1:02} / 09</div></article>')
script='<section class="complete-script"><h2>Complete narration</h2>'+''.join('<h3>'+escape(c['title'])+'</h3>'+''.join('<p>'+escape(b['text'])+'</p>' for b in c['beats']) for c in story['chapters'])+'</section>'
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>From the piste to the replay — Editorial presentation</title><link rel="stylesheet" href="'+FONT+'"><style>'+css+'</style></head><body>'+''.join(slides)+script+'</body></html>'
(HERE/'presentation.html').write_text(html)
report={'slides':len(slides),'beats':0,'overflows':[],'browserErrors':[],'allDiagramIDs':sorted(set(c['diagram'] for c in story['chapters'] if c['diagram']!='intro'))}
beats=[]
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 page=browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
 page.on('pageerror',lambda err:report['browserErrors'].append(str(err)))
 page.goto((HERE/'presentation.html').as_uri());page.evaluate('document.fonts.ready')
 report['loadedFonts']=page.evaluate('()=>[...new Set([...document.fonts].filter(f=>f.status==="loaded").map(f=>f.family))]')
 page.add_style_tag(content='.slide,.complete-script{display:none}')
 for ci,c in enumerate(timeline['chapters']):
  for bi,b in enumerate(c['beats']):
   index=len(beats)
   page.evaluate('''({ci,beat})=>{
    document.querySelectorAll('.slide').forEach(s=>s.style.display='none');
    const slide=document.getElementById('slide-'+ci);slide.style.display='block';
    slide.querySelector('.caption').textContent=beat.text;
    const ring=slide.querySelector('.spotlight');
    if(ring){ring.style.display='none';}
    const label=slide.querySelector('.focus-label');label.textContent='';
    if(beat.focus!==null&&ring){
     const node=slide.querySelector('[data-node="'+beat.focus+'"]');const rect=node.querySelector('rect');
     ring.setAttribute('x',+rect.getAttribute('x')-6);ring.setAttribute('y',+rect.getAttribute('y')-6);ring.style.display='block';
     label.textContent='Explaining: '+node.querySelector('.node-title').textContent;
    }
   }''',{'ci':ci,'beat':b})
   problems=page.evaluate('''()=>{
     const s=[...document.querySelectorAll('.slide')].find(s=>s.style.display==='block');
     let bad=[];const caption=s.querySelector('.caption').getBoundingClientRect();
     if(caption.bottom>1024)bad.push('Caption below safe area');
     const title=s.querySelector('h1').getBoundingClientRect();if(title.right>1810)bad.push('Title too wide');
     for(const n of s.querySelectorAll('.node')){const r=n.querySelector('rect').getBBox();
      for(const t of n.querySelectorAll('text')){const b=t.getBBox();if(b.x+b.width>r.x+r.width-10||b.y+b.height>r.y+r.height-6)bad.push(t.textContent);}}
     return bad;
   }''')
   if problems:report['overflows'].append({'chapter':ci,'beat':bi,'problems':problems})
   file=frames/f'{index:03}.png';page.screenshot(path=str(file))
   beats.append({**b,'chapter':ci,'frame':str(file),'index':index})
  print(f'Captured chapter {ci+1}: {len(c["beats"])} frames',flush=True)
 browser.close()
report['beats']=len(beats)
(HERE/'frame-validation.json').write_text(json.dumps(report,indent=2)+'\n')
assert not report['overflows'],report['overflows']
assert not report['browserErrors']
# Quantize boundaries once to the 30fps clock so no per-beat rounding drift accumulates.
rows=['ffconcat version 1.0'];fps=30
for i,b in enumerate(beats):
 start=round(b['start']*fps);end=round(b['end']*fps)
 rows += [f"file '{b['frame']}'",'option framerate 30',f'duration {(end-start)/fps:.9f}']
rows.append(f"file '{beats[-1]['frame']}'")
(runtime('editorial-architecture-video')/'frames.ffconcat').write_text('\n'.join(rows)+'\n')
def srtstamp(seconds):
 ms=round(seconds*1000);hours,ms=divmod(ms,3600000);minutes,ms=divmod(ms,60000);seconds,ms=divmod(ms,1000)
 return f'{hours:02}:{minutes:02}:{seconds:02},{ms:03}'
(HERE/'architecture-video.srt').write_text('\n'.join(f'{i+1}\n{srtstamp(b["start"])} --> {srtstamp(b["end"])}\n{b["text"]}\n' for i,b in enumerate(beats)))
metadata=[';FFMETADATA1','title=From the piste to the replay - Editorial architecture','artist=Fencing Review architecture explainer']
for c in timeline['chapters']:
 metadata += ['[CHAPTER]','TIMEBASE=1/1000',f'START={round(c["start"]*1000)}',f'END={round(c["end"]*1000)}','title='+c['title']]
(runtime('editorial-architecture-video')/'chapters.ffmeta').write_text('\n'.join(metadata)+'\n')
(HERE/'poster.png').write_bytes((frames/'000.png').read_bytes())
print(json.dumps(report,indent=2))
