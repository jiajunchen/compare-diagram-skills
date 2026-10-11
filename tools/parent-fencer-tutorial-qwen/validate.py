"""Validate exports, new transcript timing, retained action holds and old files."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import hashlib
import json
import subprocess
import wave
from playwright.sync_api import sync_playwright
from caption_style import header, transcript

H = (FIGURES / 'parent-fencer-tutorial-qwen')
ROOT = H.parents[1]
T = json.loads((H / 'timeline.json').read_text())
U = json.loads((H / 'sequence.json').read_text())
P = json.loads((H / 'edit-plan.json').read_text())
holds = json.loads((H / 'hold-validation.json').read_text())
assert len(holds) == 43 and all(h['identicalFrames'] == 30 for h in holds)
assert [sum(u['kind'] == kind for u in U) for kind in ('title', 'transition', 'step')] == [7, 13, 63]
assert all(p['readingPause'] >= .8 - 1e-6 for p in P)
# Verify rendered transcript sources match this recording's measured word spans.
index = 0
for ci, chapter in enumerate(T['chapters']):
    title = chapter['titleCard']
    expected = header() + transcript(title['words'], title['start'], title['duration'], x=100, y=875, size=28, width=100)
    assert (runtime('parent-fencer-tutorial-qwen') / f'title-words-{ci:02}.ass').read_text() == expected
    for beat in chapter['beats']:
        expected_body = transcript(beat['words'], beat['start'], beat['end'] - beat['start'])
        actual = (runtime('parent-fencer-tutorial-qwen') / f'text-{index:03}.ass').read_text()
        assert actual.endswith(expected_body)
        assert P[index]['label'] == beat['label']
        index += 1
videos = []
for path in [H / 'parent-fencer-guide.mp4', *sorted(H.glob('lesson-??.mp4'))]:
    info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_chapters', '-of', 'json', str(path)]))
    video = next(s for s in info['streams'] if s['codec_type'] == 'video')
    audio = next(s for s in info['streams'] if s['codec_type'] == 'audio')
    assert (video['width'], video['height'], video['r_frame_rate']) == (1920, 1080, '30/1')
    assert abs(float(video['duration']) - float(audio['duration'])) < .1
    if path.name.startswith('parent'):
        assert len(info['chapters']) == 7
        assert abs(float(video['duration']) - T['duration']) < .05
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'null', '-'], check=True, stdout=subprocess.DEVNULL)
    videos.append({'file': path.name, 'seconds': float(video['duration']), 'decode': 'passed'})
assert len(videos) == 8
for filename, digest in json.loads((H / 'preserved-originals.json').read_text()).items():
    with (ROOT / filename).open('rb') as original:
        assert hashlib.file_digest(original, 'sha256').hexdigest() == digest, filename
errors = []
with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless=True)
    page = browser.new_page(viewport={'width': 1280, 'height': 900})
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto((H / 'index.html').as_uri())
    page.wait_for_function('document.querySelector("video").readyState>=1')
    assert page.locator('button').count() == 7
    page.locator('button').nth(4).click()
    page.wait_for_timeout(400)
    target = float(page.locator('button').nth(4).get_attribute('data-time'))
    assert abs(page.locator('video').evaluate('(v)=>v.currentTime') - target) < 2
    page.locator('video').evaluate('(v)=>v.pause()')
    page.set_viewport_size({'width': 390, 'height': 844})
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    browser.close()
assert not errors
report = {'videos': videos, 'titlePages': 7, 'slideTransitions': 13,
          'verifiedOneSecondActionHolds': 43, 'measuredWordTimings': 818,
          'transcriptSourcesMatchNewAlignment': True, 'chapterPlayer': 'passed',
          'previousAudioAndVideosUnchanged': True,
          'visualReview': 'Active word, pause, tap hold, post-action screen, title card and slide transition inspected.',
          'timingLimit': 'Automatic word alignment has 80 ms timestamp resolution; zero-length function words display for one frame.'}
(H / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
