"""Generate tutorial narration only through the local MLX Audio HTTP server."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,urllib.request,urllib.error,time,wave,io,subprocess,threading,sys,hashlib
H=(FIGURES / 'local-qwen-narration');C=runtime('local-qwen-narration');MODEL='mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit';URL='http://127.0.0.1:8765/v1/audio/speech'
voice='Ryan';mode=sys.argv[1] if len(sys.argv)>1 else 'sample'
def generate(text,name):
 payload={'model':MODEL,'input':text,'voice':voice,'lang_code':'English','response_format':'wav','temperature':.6,'repetition_penalty':1.05,'max_tokens':2048,'verbose':True}
 digest=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest();out=H/(name+'.wav');meta=C/(name+'.json')
 if out.exists() and meta.exists() and json.loads(meta.read_text()).get('hash')==digest:return json.loads(meta.read_text())
 peak=[0];done=threading.Event();pid=json.loads((C/'server.json').read_text())['pid']
 def sample_memory():
  while not done.wait(.5):
   raw=subprocess.run(['ps','-p',str(pid),'-o','rss='],capture_output=True,text=True).stdout.strip()
   if raw:peak[0]=max(peak[0],int(raw)*1024)
 watcher=threading.Thread(target=sample_memory,daemon=True);watcher.start();start=time.perf_counter()
 try:
  req=urllib.request.Request(URL,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=1200) as r:data=r.read()
 finally:done.set();watcher.join()
 elapsed=time.perf_counter()-start
 with wave.open(io.BytesIO(data)) as w:duration=w.getnframes()/w.getframerate();rate=w.getframerate();assert duration>1
 out.write_bytes(data)
 result={'file':out.name,'text':text,'model':MODEL,'voice':voice,'generationSeconds':elapsed,'audioSeconds':duration,'realTimeFactor':elapsed/duration,'sampleRate':rate,'peakProcessRSSBytes':peak[0],'hash':digest}
 meta.write_text(json.dumps(result,indent=2)+'\n');print(f'{name}: {duration:.1f}s audio in {elapsed:.1f}s, peak process RSS {peak[0]/1e9:.2f} GB',flush=True);return result
if mode=='sample':
 result=generate("Number one. Add a fencer and add a tournament. First, enter the fencer's name. Here, we use Alex Rivera.",'sample-ryan');(H/'sample-report.json').write_text(json.dumps(result,indent=2)+'\n')
elif mode=='all':
 original=json.loads((H.parent/'parent-fencer-tutorial-paced/timeline.json').read_text());results=[]
 for i,c in enumerate(original['chapters']):
  text=c['titleCard']['text']+'\n\n'+'\n\n'.join(b['text'] for b in c['beats'])
  results.append(generate(text,f'lesson-{i+1:02}'))
 (H/'generation-report.json').write_text(json.dumps(results,indent=2)+'\n')
 with wave.open(str(H/'qwen-narration.wav'),'wb') as out:
  out.setnchannels(1);out.setsampwidth(2);out.setframerate(results[0]['sampleRate'])
  for r in results:
   with wave.open(str(H/r['file'])) as w:
    assert (w.getnchannels(),w.getsampwidth(),w.getframerate())==(1,2,results[0]['sampleRate'])
    out.writeframes(w.readframes(w.getnframes()));out.writeframes(bytes(results[0]['sampleRate']*2*2))
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(H/'qwen-narration.wav'),'-c:a','libmp3lame','-b:a','192k',str(H/'qwen-narration.mp3')],check=True)
else:raise SystemExit('Use sample or all.')
