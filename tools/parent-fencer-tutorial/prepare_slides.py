"""Create editorial slide backgrounds; speech text is added with timed karaoke subtitles."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,html,urllib.request
from playwright.sync_api import sync_playwright
HERE=(FIGURES / 'parent-fencer-tutorial');cache=runtime('parent-fencer-tutorial');bg=assets('parent-fencer-tutorial') / 'backgrounds';bg.mkdir(exist_ok=True)
fonts=assets('parent-fencer-tutorial') / 'fonts';fonts.mkdir(exist_ok=True)
if not (fonts/'Geist.ttf').exists():
 urllib.request.urlretrieve('https://raw.githubusercontent.com/google/fonts/main/ofl/geist/Geist%5Bwght%5D.ttf',fonts/'Geist.ttf')
data=json.loads((HERE/'timeline.json').read_text())
style='''*{box-sizing:border-box}body{margin:0;width:1920px;height:1080px;background:#f9f9f9;color:#131313;font-family:Geist,Arial,sans-serif}.mast{position:absolute;top:42px;left:64px;right:64px;display:flex;justify-content:space-between;font:14px "Geist Mono",monospace;letter-spacing:.13em;border-bottom:1px solid #b8b8b5;padding-bottom:22px}h1{position:absolute;left:64px;top:98px;font:64px "Instrument Serif",Georgia,serif;letter-spacing:-.02em;margin:0}.screen{position:absolute;left:64px;top:210px;width:1120px;height:778px;background:#eeeeec;border:1px solid #b8b8b5}.divider{position:absolute;left:1220px;top:210px;height:778px;border-left:1px solid #b8b8b5}.side{position:absolute;left:1270px;top:228px;width:562px}.side h2{font:italic 42px "Instrument Serif",Georgia,serif;margin:0 0 26px}.side p{font:14px "Geist Mono",monospace;letter-spacing:.06em;color:#585858}.rule{margin-top:25px;border-top:1px solid #b8b8b5}.foot{position:absolute;left:64px;right:64px;bottom:30px;display:flex;justify-content:space-between;color:#585858;font:12px "Geist Mono",monospace}.hint{position:absolute;left:1270px;top:850px;width:540px;font-size:20px;line-height:1.5;color:#585858}'''
font='https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400&display=swap'
hints=['One fencer profile. Add a separate tournament for each event.','Review the proposed schedule before confirming.','Use the number from the full bout order.','Choose the bout before selecting recordings.','Clip star: your choice. Bout star: a summary of its clips.','Delete removes a clip. The original stays in Photos.','Clear local copies frees device storage. Uploaded clips remain in iCloud.']
index=0
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 page=browser.new_page(viewport={'width':1920,'height':1080})
 for ci,c in enumerate(data['chapters']):
  for bi,b in enumerate(c['beats']):
   content=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><link href="{font}" rel="stylesheet"><style>{style}</style></head><body><div class="mast"><span>Fencing Review / Parent + Fencer Guide</span><span>Lesson {ci+1:02} / 07</span></div><h1>{html.escape(c['title'])}</h1><div class="screen"></div><div class="divider"></div><div class="side"><h2>Follow along.</h2><p>STEP {bi+1:02} / {len(c['beats']):02}</p><div class="rule"></div></div><p class="hint">{html.escape(hints[ci])}</p><div class="foot"><span>iPad simulator · Fictional demo media</span><span>Red marks show taps · Small controls are magnified</span></div></body></html>'''
   page.set_content(content);page.evaluate('document.fonts.ready');page.screenshot(path=str(bg/f'{index:03}.png'))
   index+=1
 browser.close()
print(f'{index} editorial backgrounds ready.')
