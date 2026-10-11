"""Render measured word spans with an active word and quiet completed text."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

def stamp(t):
    cs = round(max(t, 0) * 100)
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'

def header(w=1920, h=1080, size=34):
    return f'''[Script Info]\nScriptType: v4.00+\nPlayResX: {w}\nPlayResY: {h}\nWrapStyle: 2\nScaledBorderAndShadow: yes\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,Geist,{size},&H00131313,&H006F6F6F,&H00131313,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n'''

def transcript(words, offset, duration, x=1270, y=370, size=34, width=28):
    local = [{'word': w['word'], 'start': round((w['start'] - offset) * 100) / 100,
              'end': round((w['end'] - offset) * 100) / 100} for w in words]
    points = sorted({0, round(duration * 100) / 100, *[w[k] for w in local for k in ('start', 'end')]})
    events = []
    for start, end in zip(points, points[1:]):
        if end <= start:
            continue
        now = (start + end) / 2
        active = [i for i, w in enumerate(local) if w['start'] <= now < w['end']]
        active = active[-1] if active else -1
        text = f'{{\\an7\\pos({x},{y})\\fs{size}}}'
        count = 0
        for i, w in enumerate(local):
            if count + len(w['word']) + 1 > width:
                text += '\\N'
                count = 0
            color = '2626B3' if i == active else '131313' if now >= w['end'] else '6F6F6F'
            text += '{\\c&H' + color + '&\\u' + ('1' if i == active else '0') + '}' + w['word'] + ' '
            count += len(w['word']) + 1
        events.append(f'Dialogue: 0,{stamp(start)},{stamp(end)},Default,,0,0,0,,{text}\n')
    return ''.join(events)
