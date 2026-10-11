"""Synthesize chapter speech with character timing; never log credentials."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import base64,hashlib,json,os,re,subprocess,urllib.request,urllib.error,wave
from concurrent.futures import ThreadPoolExecutor
HERE=(FIGURES / 'parent-fencer-tutorial')
ROOT=HERE.parent.parent
story=json.loads((HERE/'storyboard.json').read_text())
cache=runtime('parent-fencer-tutorial');cache.mkdir(exist_ok=True)
key=os.environ.get('ELEVENLABS_API_KEY') or os.environ.get('ElevenLab_API')
if not key:
 for line in (ROOT/'.env').read_text().splitlines():
  m=re.match(r'\s*(?:export\s+)?(ELEVENLABS_API_KEY|ElevenLab_API)\s*=\s*(.*)',line)
  if m:key=m.group(2).strip().strip('\"\x27');break
if not key:raise SystemExit('No ElevenLabs key found in the configured environment.')
def generate(item):
 i,c=item
 text='\n\n'.join(b['text'] for b in c['beats'])
 payload={'text':text,'model_id':story['model'],'voice_settings':{'stability':0.65,'similarity_boost':0.75,'style':0.0,'use_speaker_boost':True,'speed':0.95}}
 digest=hashlib.sha256(json.dumps([story['voice'],payload],sort_keys=True).encode()).hexdigest()
 response=cache/(digest+'.json')
 if not response.exists():
  req=urllib.request.Request('https://api.elevenlabs.io/v1/text-to-speech/'+story['voice']+'/with-timestamps?output_format=mp3_44100_128',data=json.dumps(payload).encode(),headers={'xi-api-key':key,'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=180) as r:data=json.load(r)
  except urllib.error.HTTPError as exc:raise RuntimeError(f'TTS chapter {i+1} failed with HTTP {exc.code}; response body omitted.') from None
  response.write_text(json.dumps(data))
 else:data=json.loads(response.read_text())
 alignment=data['alignment'];recognized=''.join(alignment['characters'])
 assert recognized==text, f'Chapter {i+1}: original text alignment differs; review before rendering.'
 mp3=cache/f'chapter-{i:02}.mp3';mp3.write_bytes(base64.b64decode(data['audio_base64']))
 wav=cache/f'chapter-{i:02}.wav'
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(mp3),'-af','apad=pad_dur=0.8','-ar','44100','-ac','1',str(wav)],check=True)
 with wave.open(str(wav)) as w:duration=w.getnframes()/w.getframerate()
 cursor=0;beats=[]
 for j,b in enumerate(c['beats']):
  start=0 if j==0 else alignment['character_start_times_seconds'][cursor]
  words=[]
  for match in re.finditer(r'\S+',b['text']):
   words.append({'word':match.group(),'start':alignment['character_start_times_seconds'][cursor+match.start()], 'end':alignment['character_end_times_seconds'][cursor+match.end()-1]})
  beats.append({**b,'start':start,'words':words})
  cursor+=len(b['text'])+2
 for j,b in enumerate(beats):b['end']=beats[j+1]['start'] if j+1<len(beats) else duration
 print(f'Chapter {i+1}: {duration:.1f}s, {len(beats)} aligned beats',flush=True)
 return {**c,'duration':duration,'beats':beats,'wav':str(wav)}
with ThreadPoolExecutor(max_workers=2) as pool:chapters=list(pool.map(generate,enumerate(story['chapters'])))
time=0
with wave.open(str(HERE/'narration.wav'),'wb') as output:
 output.setnchannels(1);output.setsampwidth(2);output.setframerate(44100)
 for c in chapters:
  c['start']=time
  for b in c['beats']:
   b['start']+=time;b['end']+=time
   for word in b['words']:word['start']+=time;word['end']+=time
  with wave.open(c.pop('wav')) as wav:output.writeframes(wav.readframes(wav.getnframes()))
  time+=c['duration'];c['end']=time
(HERE/'timeline.json').write_text(json.dumps({'title':story['title'],'duration':time,'chapters':chapters},indent=2)+'\n')
print(f'Finished: {time:.2f} seconds')
