"""Align real simulator actions with speech, zooms, red tap marks and karaoke text."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json,math,re,subprocess,os
from concurrent.futures import ThreadPoolExecutor
HERE=(FIGURES / 'parent-fencer-tutorial');cache=runtime('parent-fencer-tutorial');segments=cache/'segments';segments.mkdir(exist_ok=True)
timeline=json.loads((HERE/'timeline.json').read_text())
events=json.loads((HERE/'capture-events.json').read_text())
clock=json.loads((assets('parent-fencer-tutorial') / 'recording-clock.json').read_text())['hostStart']
assert any(e['kind']=='complete' for e in events),'Capture must pass all seven lessons.'
groups={}
for e in events:
 if e['kind']!='complete':groups.setdefault(e['step'],[]).append(e)
steps=list(groups.values());bylabel={g[0]['label']:g for g in steps}
rawsource=assets('parent-fencer-tutorial') / 'recordings'/'capture.mov'
source=cache/'capture-landscape-30fps.mp4'
# simctl emits sparse frames for static screens. Fill those holds before seeking,
# or an input seek can skip a still confirmation and jump to the next UI change.
if not source.exists() or source.stat().st_mtime < rawsource.stat().st_mtime:
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(rawsource),'-vf','transpose=cclock,scale=1180:820,setsar=1,fps=30','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',str(source)],check=True)
def stamp(t):
 cs=round(max(t,0)*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
 return f'{h}:{m:02}:{s:02}.{cs:02}'
def header(w,h,font='Geist',size=34):
 return f'''[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,{font},{size},&H00131313,&H006F6F6F,&H00131313,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''
def dialogue(start,end,text,layer=0):return f'Dialogue: {layer},{stamp(start)},{stamp(end)},Default,,0,0,0,,{text}\n'
plans=[];index=0
for ci,c in enumerate(timeline['chapters']):
 for bi,b in enumerate(c['beats']):
  group=bylabel[b['label']];begin=group[0];next_groups=[g for g in steps if g[0]['time']>begin['time']]
  finish=next_groups[0][0]['time']-.06 if next_groups else group[-1]['time']+.4
  # Speech is the master clock. Clip boundaries use its quantized 30fps timestamps.
  duration=(round(b['end']*30)-round(b['start']*30))/30
  rawstart=begin['time']-clock;rawduration=finish-begin['time']
  action=next((e for e in group if e['kind'] in ('tap','drag')),None)
  rect=(action or begin)['rect'];x,y,w,h=rect;cx=x+w/2;cy=y+h/2
  # Small controls get a smooth magnification; broad controls keep more context.
  zoom=1.0 if w==0 or w>700 else 1.7 if w>350 else 2.0
  if action and action['kind']=='drag':zoom=1.15
  if b['label']=='enter-fencer':cx=300;zoom=1.8
  target=None
  if action:
   word=next((word for word in b['words'] if re.sub(r'[^a-z]','',word['word'].lower()) in ('tap','select','enter','move','pause','scroll','open','confirm')),b['words'][0])
   target=max(.55,min(word['start']-b['start']+.65,duration-1.0))
   actual=action['time']-begin['time']
  else:actual=None
  # Karaoke sweeps each word from gray to black at its measured speech time.
  lines=[];line=[];letters=0
  words=b['words']
  leading=max(0,words[0]['start']-b['start'])
  karaoke='{\\an7\\pos(1270,370)\\fs34\\fad(160,0)}'+f'{{\\k{round(leading*100)}}}'
  for wi,word in enumerate(words):
   token=word['word']
   if letters+len(token)+1>28:
    karaoke+='\\N';letters=0
   end=words[wi+1]['start'] if wi+1<len(words) else word['end']
   karaoke+=f'{{\\kf{max(1,round((end-word["start"])*100))}}}'+token+' '
   letters+=len(token)+1
  ass=cache/f'text-{index:03}.ass';ass.write_text(header(1920,1080)+dialogue(0,duration,karaoke))
  tapass=cache/f'tap-{index:03}.ass';taptext=header(1180,820,size=20)
  if action:
   # The remark starts shortly before the recorded action and gently pulses.
   start=max(0,target-.30);end=min(duration,target+.90)
   x1=max(2,x-5);y1=max(2,y-5);x2=min(1178,x+w+5);y2=min(818,y+h+5)
   shape=f'm {x1:.1f} {y1:.1f} l {x2:.1f} {y1:.1f} {x2:.1f} {y2:.1f} {x1:.1f} {y2:.1f} {x1:.1f} {y1:.1f}'
   style='{\\an7\\pos(0,0)\\p1\\1a&HFF&\\3c&H003535DD&\\bord2\\shad0\\fad(80,220)\\t(0,250,\\bord4)\\t(250,650,\\bord2)}'
   taptext+=dialogue(start,end,style+shape)
   # A bright pointer dot pulses at the tapped control's center.
   dot='{\\an5\\pos('+f'{cx:.1f},{cy:.1f}'+' )\\fnArial\\fs36\\1c&H003535DD&\\bord0\\fad(50,350)\\fscx75\\fscy75\\t(0,350,\\fscx135\\fscy135)}●'
   dot=dot.replace(' )',')');taptext+=dialogue(target,min(duration,target+.7),dot,1)
  tapass.write_text(taptext)
  plan={'index':index,'chapter':ci,'label':b['label'],'duration':duration,'audioStart':b['start'],'rawStart':rawstart,'rawDuration':rawduration,'rawAction':actual,'outputAction':target,'rect':rect,'zoom':zoom,'focusX':cx,'focusY':cy,'textAss':str(ass),'tapAss':str(tapass)}
  plans.append(plan);index+=1
assert set(bylabel)==set(p['label'] for p in plans),(set(bylabel)-set(p['label'] for p in plans))
(HERE/'edit-plan.json').write_text(json.dumps(plans,indent=2)+'\n')
def render(plan):
 i=plan['index'];duration=plan['duration'];rawduration=plan['rawDuration'];output=segments/f'{i:03}.mp4'
 if output.exists() and not os.environ.get('TUTORIAL_RERENDER'):return
 start=plan['rawStart'];a=plan['rawAction'];target=plan['outputAction'];x,y,w,h=plan['rect'];cx=plan['focusX'];cy=plan['focusY'];zoom=plan['zoom']
 filters=['[0:v]setsar=1,setpts=PTS-STARTPTS[base]']
 if a is not None and a>.05:
  filters+=['[base]split=2[pre][post]',f'[pre]trim=end={a:.6f},setpts=(PTS-STARTPTS)*{target/a:.8f}[before]',f'[post]trim=start={a:.6f},setpts=(PTS-STARTPTS)*{(duration-target)/max(.1,rawduration-a):.8f}[after]','[before][after]concat=n=2:v=1:a=0,fps=30[timed]']
 else:filters+=[f'[base]setpts=(PTS-STARTPTS)*{duration/rawduration:.8f},fps=30[timed]']
 # Magnification moves smoothly to the current control, then holds steady.
 z=f'1+({zoom}-1)*min(on/15,1)'
 filters += [f"[timed]ass='{plan['tapAss']}',zoompan=z='{z}':x='max(0,min(iw-iw/zoom,{cx if w else 590}-iw/zoom/2))':y='max(0,min(ih-ih/zoom,{cy if h else 410}-ih/zoom/2))':d=1:s=1120x778:fps=30,tpad=stop_mode=clone:stop_duration=1,trim=duration={duration}[screen]",'[1:v]format=yuv420p[background]',f"[background][screen]overlay=x=64:y=210:shortest=1,ass='{plan['textAss']}':fontsdir='{assets('parent-fencer-tutorial') / 'fonts'}'[out]"]
 script=cache/f'filter-{i:03}.txt';script.write_text(';\n'.join(filters))
 cmd=['ffmpeg','-v','error','-y','-ss',str(start),'-t',str(rawduration),'-i',str(source),'-loop','1','-framerate','30','-i',str(assets('parent-fencer-tutorial') / 'backgrounds'/f'{i:03}.png'),'-filter_complex_script',str(script),'-map','[out]','-an','-t',str(duration),'-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-r','30','-threads','3',str(output)]
 result=subprocess.run(cmd,capture_output=True,text=True)
 if result.returncode:raise RuntimeError(f'Segment {i}: '+result.stderr[-2000:])
 print(f'Rendered {i+1}/{len(plans)}: {plan["label"]}',flush=True)
selected=os.environ.get('TUTORIAL_SEGMENTS')
if selected:
 picked={int(i) for i in selected.split(',')};plans=[p for p in plans if p['index'] in picked]
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,plans))
