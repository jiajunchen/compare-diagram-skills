
import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
from playwright.sync_api import sync_playwright
import subprocess
HERE=(FIGURES / 'parent-fencer-tutorial');media=assets('parent-fencer-tutorial') / 'media';media.mkdir(exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless=True)
 page=b.new_page(viewport={'width':1280,'height':720},device_scale_factor=1)
 page.set_content('''<style>body{margin:0;padding:64px;font-family:Arial;background:white;color:#172630}h1{font-size:44px}p{font-size:24px}table{border-collapse:collapse;width:100%;font-size:26px}th,td{padding:22px;border:2px solid #b0b8bb;text-align:left}th{background:#eee}</style><p>DEMO SCHEDULE · FICTIONAL NAMES</p><h1>Autumn Practice Open</h1><p>POOL #3 ON STRIP 12 — BOUT ORDER</p><table><tr><th>Bout Number</th><th>Right Fencer</th><th>Left Fencer</th></tr><tr><td>1</td><td>Alex Rivera</td><td>Jamie Lee</td></tr><tr><td>2</td><td>Sam Taylor</td><td>Morgan Chen</td></tr><tr><td>3</td><td>Taylor Park</td><td>Alex Rivera</td></tr></table>''')
 page.screenshot(path=str(media/'demo-schedule.png'))
 page.set_content('''<canvas width="1280" height="720"></canvas><script>let c=document.querySelector('canvas').getContext('2d');function person(x,dir,color,t){c.strokeStyle=color;c.fillStyle=color;c.lineWidth=13;c.lineCap='round';c.beginPath();c.arc(x,260,27,0,7);c.fill();c.beginPath();c.moveTo(x,296);c.lineTo(x-dir*14,407);c.lineTo(x-dir*58,485);c.moveTo(x-dir*14,407);c.lineTo(x+dir*66,485);c.moveTo(x,324);c.lineTo(x+dir*68,340);c.lineTo(x+dir*123,322);c.stroke();c.lineWidth=4;c.beginPath();c.moveTo(x+dir*123,322);c.lineTo(x+dir*258,303+Math.sin(t*2)*18);c.stroke()}window.draw=t=>{c.fillStyle='#e9eeed';c.fillRect(0,0,1280,720);c.fillStyle='#273638';c.font='22px Arial';c.fillText('DEMO RECORDING  /  FICTIONAL PRACTICE',56,64);c.font='36px Arial';c.fillText('Alex Rivera  —  Jamie Lee',56,119);c.fillStyle='#c7d0ce';c.fillRect(64,500,1152,72);c.fillStyle='#9eadaa';for(let x=64;x<1200;x+=96)c.fillRect(x,500,2,72);person(390+Math.sin(t*1.1)*65,1,'#254653',t);person(855+Math.sin(t*1.1+1)*65,-1,'#aa5342',t);c.fillStyle='#273638';c.font='24px Arial';c.fillText('Practice moment  '+t.toFixed(1)+' seconds',56,660);c.font='18px Arial';c.fillText('Illustrated sample footage for app instructions',770,660)}</script>''')
 frames=runtime('parent-fencer-tutorial')/'demo-frames';frames.mkdir(parents=True, exist_ok=True)
 for i in range(120):
  page.evaluate('draw('+str(i/10)+')');page.screenshot(path=str(frames/f'{i:03}.png'))
 b.close()
for n in (1,2):
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','10','-i',str(frames/'%03d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-r','30','-metadata','creation_time='+f'2026-10-01T10:{30+n*2}:00Z','-movflags','+faststart',str(media/f'Demo-Recording-{n}.mp4')],check=True)
print('Demo schedule and two 12-second recordings prepared.')
