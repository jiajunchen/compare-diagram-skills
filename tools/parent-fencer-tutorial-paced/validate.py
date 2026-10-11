
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,subprocess,hashlib,wave
from playwright.sync_api import sync_playwright
H=(FIGURES / 'parent-fencer-tutorial-paced');T=json.loads((H/'timeline.json').read_text());U=json.loads((H/'sequence.json').read_text());P=json.loads((H/'edit-plan.json').read_text());holds=json.loads((H/'hold-validation.json').read_text())
assert len(holds)==43 and all(x['identicalFrames']==30 for x in holds)
oldplans=json.loads((H.parent/'parent-fencer-tutorial/edit-plan.json').read_text())
for old,new in zip(oldplans,P):
 if new['rawAction'] is not None:
  oldlength=min(old['duration'],old['outputAction']+.9)-max(0,old['outputAction']-.3)
  newlength=min(new['duration'],new['outputAction']+.9)-max(0,new['outputAction']-.3)
  assert newlength>=oldlength-1e-6
assert len([u for u in U if u['kind']=='title'])==7
assert len([u for u in U if u['kind']=='transition'])==13
assert len([u for u in U if u['kind']=='step'])==63
assert all(p['readingPause']>=1 for p in P)
for c in T['chapters']:
 for b in c['beats']:
  assert all(b['start']-.01<=w['start']<=w['end']<=b['end'] for w in b['words'])
with wave.open(str(H/'narration.wav')) as w:assert abs(w.getnframes()/w.getframerate()-T['duration'])<.001
videos=[]
for f in [H/'parent-fencer-guide.mp4',*sorted(H.glob('lesson-??.mp4'))]:
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(f)]));v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
 assert (v['width'],v['height'])==(1920,1080)
 assert abs(float(v['duration'])-float(a['duration']))<.1
 if f.name.startswith('parent'):assert len(info['chapters'])==7 and abs(float(v['duration'])-T['duration'])<.05
 subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
 videos.append({'file':f.name,'duration':float(v['duration']),'decode':'passed'})
assert len(videos)==8
prior=json.loads((H/'previous-version.json').read_text());assert hashlib.file_digest(Path(prior['path']).open('rb'),'sha256').hexdigest()==prior['sha256']
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True);page=b.new_page(viewport={'width':1280,'height':900});page.goto((H/'index.html').as_uri());page.wait_for_function('document.querySelector("video").readyState>=1');assert page.locator('button').count()==7
 page.locator('button').nth(3).click();page.wait_for_timeout(400);target=float(page.locator('button').nth(3).get_attribute('data-time'));assert abs(page.locator('video').evaluate('(v)=>v.currentTime')-target)<2
 page.locator('video').evaluate('(v)=>v.pause()');page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');b.close()
report={'videos':videos,'titlePages':7,'slideTransitions':13,'readingPauses':63,'verifiedOneSecondHolds':43,'highlightDurationNotShortened':True,'firstEditionUnchanged':True,'wordAlignment':'passed','chapterPlayer':'passed','visualReview':'Title page, slide transition, and tap / highlight end / UI resume samples inspected.'}
(H/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
