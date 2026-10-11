"""Add MP4 chapters and validate the completed video without re-encoding it."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import json
import subprocess
import tempfile

HERE = (FIGURES / 'architecture-video')
video = HERE / 'architecture-video.mp4'
chapters = json.loads((HERE / 'chapters.json').read_text())
validation = json.loads((HERE / 'validation.json').read_text())

def escaped(s):
    for c in ('\\', '=', ';', '#', '\n'):
        s = s.replace(c, '\\' + c)
    return s

with tempfile.TemporaryDirectory(prefix='sports-video-') as tmp:
    metadata = Path(tmp) / 'chapters.ffmeta'
    rows = [';FFMETADATA1', 'title=' + escaped(chapters[0]['title']),
            'comment=Architecture explainer with ElevenLabs narration; generated October 7 2026']
    for chapter in chapters:
        rows.extend(['[CHAPTER]', 'TIMEBASE=1/1000',
                     f'START={round(chapter["startSeconds"] * 1000)}',
                     f'END={round(chapter["endSeconds"] * 1000)}',
                     'title=' + escaped(chapter['title'])])
    metadata.write_text('\n'.join(rows) + '\n')
    staging = HERE / 'architecture-video.chapters.mp4'
    try:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(video),
                        '-i', str(metadata), '-map', '0:v:0', '-map', '0:a:0',
                        '-map_metadata', '1', '-map_chapters', '1', '-c', 'copy',
                        '-movflags', '+faststart', str(staging)], check=True)
        staging.replace(video)
    finally:
        staging.unlink(missing_ok=True)

probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error',
    '-show_streams', '-show_format', '-show_chapters', '-of', 'json', str(video)]))
v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
assert (v['width'], v['height']) == (1920, 1080)
assert v['codec_name'] == 'h264' and a['codec_name'] == 'aac'
assert abs(float(probe['format']['duration']) - validation['durationSeconds']) < .15
assert len(probe['chapters']) == len(chapters)
subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-map', '0:v:0',
                '-map', '0:a:0', '-f', 'null', '-'], check=True)
validation['mp4'] = {'width':v['width'], 'height':v['height'],
    'videoCodec':v['codec_name'], 'audioCodec':a['codec_name'],
    'frameRate':v['avg_frame_rate'], 'durationSeconds':float(probe['format']['duration']),
    'chaptersIncludingIntro':len(probe['chapters']), 'bytes':video.stat().st_size,
    'fullDecode':'passed'}
(HERE / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
print(json.dumps(validation['mp4'], indent=2))
