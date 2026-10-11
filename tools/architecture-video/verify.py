"""Check the narrated HTML player and export chapter and caption sidecars."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import base64
import json
import re
import wave
from io import BytesIO
from playwright.sync_api import sync_playwright

HERE = (FIGURES / 'architecture-video')
HTML = HERE / 'architecture-video.html'
source = (HERE / 'architecture-video.md').read_text()
expected_beats = [line[2:].replace('[', '').replace(']', '') for line in source.splitlines() if line.startswith('> ')]
expected_chapters = sum(line.startswith('## ') for line in source.splitlines())
text = HTML.read_text()
data = json.loads(re.search(r'<script type="application/json" id="amv-data">(.*?)</script>', text, re.S).group(1))
audio = base64.b64decode(re.search(r'src="data:audio/wav;base64,([A-Za-z0-9+/=]+)"', text).group(1))
with wave.open(BytesIO(audio)) as wav:
    audio_info = {'channels': wav.getnchannels(), 'sampleRate': wav.getframerate(),
                  'duration': wav.getnframes() / wav.getframerate(), 'bytes': len(audio)}
assert abs(audio_info['duration'] - data['duration']) < .1
beats = [beat for segment in data['segments'] for beat in segment['beats']]
assert [beat['text'] for beat in beats] == expected_beats
assert len(data['segments']) == expected_chapters + 1
assert all(b['start'] < b['end'] <= data['duration'] for b in beats)
assert all(a['end'] <= b['start'] for a,b in zip(beats, beats[1:]))

def stamp(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

(HERE / 'architecture-video.srt').write_text('\n\n'.join(
    f'{i}\n{stamp(b["start"])} --> {stamp(b["end"])}\n{b["text"]}'
    for i,b in enumerate(beats,1)) + '\n')
chapters = [{'title': s['title'], 'startSeconds': s['start'], 'endSeconds': s['end']}
            for s in data['segments']]
(HERE / 'chapters.json').write_text(json.dumps(chapters, indent=2) + '\n')
report = {'chapters': expected_chapters, 'narrationBeats': len(beats), 'durationSeconds': data['duration'],
          'audio': audio_info, 'browserErrors': [], 'captionCollisions': [], 'externalRequests': [], 'outOfFrameLabels': []}
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
    page = browser.new_page(viewport={'width':1920,'height':1080})
    page.on('pageerror', lambda e: report['browserErrors'].append(str(e)))
    page.on('request', lambda req: report['externalRequests'].append(req.url) if req.url.startswith(('http:', 'https:')) else None)
    page.goto(HTML.as_uri())
    page.wait_for_function('window.__amv !== undefined')
    assert page.locator('#amv-audio').count() == 1
    assert page.locator('.amv-marks').locator('i').count() == expected_chapters
    page.locator('.amv-bigplay').click()
    page.wait_for_timeout(500)
    assert page.locator('#amv-audio').evaluate('(a)=>!a.paused && a.currentTime > 0')
    page.locator('[data-amv="toggle"]').click()
    page.evaluate('window.__amv.exportMode()')
    for i, segment in enumerate(data['segments'][1:],1):
        for j,beat in enumerate(segment['beats']):
            page.evaluate('(t)=>render(t)', min(beat['start'] + 1.0, beat['end'] - .05))
            result = page.evaluate('''(i) => {
                const cap=document.querySelector('.amv-caption span').getBoundingClientRect();
                const sc=document.querySelectorAll('.amv-scene')[i];
                const els=[...sc.querySelectorAll('[data-key],text')].filter(e=>{
                    let n=e; while(n && n!==sc) {if(Number(getComputedStyle(n).opacity)<.05)return false;n=n.parentElement;}return true;
                });
                return {collisions:els.filter(e=>{let r=e.getBoundingClientRect();return r.bottom>cap.top && r.top<cap.bottom && r.right>cap.left && r.left<cap.right;}).map(e=>e.textContent.trim()), outside:els.filter(e=>{let r=e.getBoundingClientRect();return r.left<0 || r.right>1920 || r.top<125 || r.bottom>1080;}).map(e=>e.textContent.trim())};
            }''', i)
            if result['collisions']: report['captionCollisions'].append({'chapter':i,'beat':j+1,'labels':result['collisions']})
            if result['outside']: report['outOfFrameLabels'].append({'chapter':i,'beat':j+1,'labels':result['outside']})
        page.screenshot(path=f'/tmp/sports-video-final-{i:02}.png')
    report['staticHoldsVerified'] = 0
    for segment in data['segments']:
        for beat in segment['beats']:
            if beat['end'] - beat['start'] < 3:
                continue
            page.evaluate('(t)=>render(t)', beat['start'] + 2.01)
            initial = page.screenshot()
            page.evaluate('(t)=>render(t)', beat['end'] - .1)
            assert initial == page.screenshot(), segment['title']
            report['staticHoldsVerified'] += 1
    page.evaluate('render(1)')
    page.screenshot(path=str(HERE / 'poster.png'))
    browser.close()
assert not report['browserErrors'], report['browserErrors']
assert not report['externalRequests'], report['externalRequests']
assert not report['captionCollisions'], report['captionCollisions']
assert not report['outOfFrameLabels'], report['outOfFrameLabels']
(HERE / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
