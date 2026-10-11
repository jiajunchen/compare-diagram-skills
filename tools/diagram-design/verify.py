"""Check the actual HTML in Chrome, plus skill geometry and accessibility rules."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,re,subprocess,tempfile,sys
from playwright.sync_api import sync_playwright
HERE=(FIGURES / 'diagram-design')
HTML=HERE/'architecture.html'
skill=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/tmp/sports-diagram-design')
report={'skillSelfCheck':None,'geometry':[],'browserErrors':[],'nodeTextOverflows':[],'desktop':{},'mobile':{}}
r=subprocess.run(['python3',str(skill/'skills/diagram-design/scripts/self_check.py'),str(HTML)],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
report['skillSelfCheck']='passed'
# Upstream geometry checker combines coordinate spaces across SVG roots.
# Each figure is independently checked in its own SVG coordinate space.
with tempfile.TemporaryDirectory() as tmp:
 for i,svg in enumerate(re.findall(r'<svg.*?</svg>',HTML.read_text(),re.S)):
  f=Path(tmp)/f'figure-{i}.html';f.write_text(svg.replace('><','>\n<'))
  r=subprocess.run(['python3',str(skill/'scripts/verify-geometry.py'),str(f)],capture_output=True,text=True)
  assert r.returncode==0,r.stdout+r.stderr
  report['geometry'].append({'figure':i+1,'result':'passed'})
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 page=browser.new_page(viewport={'width':1440,'height':1100},device_scale_factor=1)
 page.on('pageerror',lambda err:report['browserErrors'].append(str(err)))
 page.goto(HTML.as_uri());page.evaluate('document.fonts.ready')
 report['fonts']=page.evaluate('''()=>({title:getComputedStyle(document.querySelector('h1')).fontFamily,body:getComputedStyle(document.body).fontFamily,loaded:[...document.fonts].filter(f=>f.status==='loaded').map(f=>f.family)})''')
 report['nodeTextOverflows']=page.evaluate('''()=>[...document.querySelectorAll('.node')].flatMap(n=>{const b=n.querySelector('rect').getBBox();return [...n.querySelectorAll('text')].filter(t=>{const r=t.getBBox();return r.x<b.x+12 || r.x+r.width>b.x+b.width-12 || r.y+r.height>b.y+b.height-8}).map(t=>({text:t.textContent,section:n.closest('section').id,width:t.getBBox().width}))})''')
 ids=page.locator('[id]').evaluate_all('(els)=>els.map(e=>e.id)');assert len(ids)==len(set(ids))
 for a in page.locator('a[href^="#"]').evaluate_all('(els)=>els.map(e=>e.getAttribute("href").slice(1))'):assert a in ids,a
 report['desktop']['pageOverflow']=page.evaluate('document.documentElement.scrollWidth>innerWidth')
 page.screenshot(path='/tmp/diagram-atlas-top.png')
 for id in ['overview','schedule','clips','sync']:
  page.locator(f'#{id} .diagram-container').screenshot(path=f'/tmp/diagram-atlas-{id}.png')
 page.set_viewport_size({'width':390,'height':844})
 page.evaluate('scrollTo(0,0)');page.wait_for_timeout(200)
 report['mobile']['pageOverflow']=page.evaluate('document.documentElement.scrollWidth>innerWidth')
 report['mobile']['localScrollers']=page.locator('.diagram-container').evaluate_all('(els)=>els.filter(e=>e.scrollWidth>e.clientWidth&&getComputedStyle(e).overflowX==="auto").length')
 page.screenshot(path='/tmp/diagram-atlas-mobile.png')
 browser.close()
for ref in json.loads((HERE/'source-index.json').read_text()):
 path=HERE.parent.parent/ref['file'];assert path.exists()
 assert ref['symbol'] in path.read_text().splitlines()[ref['line']-1]
report['sourceReferences']=len(json.loads((HERE/'source-index.json').read_text()))
(HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert not report['nodeTextOverflows'],report['nodeTextOverflows']
assert not report['desktop']['pageOverflow'] and not report['mobile']['pageOverflow']
assert report['mobile']['localScrollers']==7
assert not report['browserErrors']
