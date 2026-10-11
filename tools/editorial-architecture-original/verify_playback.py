"""Check encoded chapter frames against the authored images and play the result in Chrome."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess,tempfile
import re
from playwright.sync_api import sync_playwright
p=(FIGURES / 'editorial-architecture-original');d=json.loads((p/'timeline.json').read_text());index=0;checks=[]
with tempfile.TemporaryDirectory() as tmp:
 for ci,c in enumerate(d['chapters']):
  b=c['beats'][min(2,len(c['beats'])-1)];n=index+min(2,len(c['beats'])-1)
  target=Path(tmp)/f'{ci}.png';time=(b['start']+b['end'])/2
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(time),'-i',str(p/'architecture-video.mp4'),'-frames:v','1',str(target)],check=True)
  expected=runtime('editorial-architecture-original') / 'frames'/f'{n:03}.png'
  comparison=subprocess.run(['ffmpeg','-hide_banner','-i',str(expected),'-i',str(target),'-lavfi','ssim','-f','null','-'],capture_output=True,text=True,check=True)
  score=float(re.search(r'All:([0-9.]+)',comparison.stderr).group(1))
  assert score>.98,(ci,score)
  checks.append({'chapter':ci+1,'sampleTime':round(time,3),'structuralSimilarity':score})
  index+=len(c['beats'])
with sync_playwright() as pw:
 browser=pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 page=browser.new_page();page.goto((p/'index.html').as_uri())
 page.wait_for_function('document.querySelector("video").readyState>=1')
 page.locator('video').evaluate('(v)=>{v.muted=true;return v.play()}');page.wait_for_timeout(500)
 play=page.locator('video').evaluate('(v)=>({playing:!v.paused,time:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight})')
 assert play['playing'] and play['time']>0 and play['width']==1920
 browser.close()
(p/'playback-validation.json').write_text(json.dumps({'encodedFramesMatch':checks,'browserPlayback':play},indent=2)+'\n')
print('Thirteen encoded chapter samples match the source frames; browser playback passed.')
