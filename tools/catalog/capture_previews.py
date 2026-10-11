"""Capture existing outputs; render source-data previews for audio and Canvas."""
import base64
import html
import json
import shutil
import subprocess
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

from support import FIGURES, HERE, REPO, data_uri, fonts, markdown

SCRATCH = REPO / '.runtime/figures/catalog'
PREVIEWS = HERE / 'previews'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def prepare_fonts() -> None:
    directory = HERE / 'fonts'
    directory.mkdir(exist_ok=True)
    if not (directory / 'Geist.ttf').exists():
        shutil.copyfile(FIGURES / 'tools/assets/parent-fencer-tutorial/fonts/Geist.ttf', directory / 'Geist.ttf')
    base = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
    files = {'InstrumentSerif-Regular.ttf': 'instrumentserif/InstrumentSerif-Regular.ttf',
             'InstrumentSerif-OFL.txt': 'instrumentserif/OFL.txt', 'Geist-OFL.txt': 'geist/OFL.txt'}
    for name, source in files.items():
        if not (directory / name).exists():
            urllib.request.urlretrieve(base + source, directory / name)


def document(body: str) -> str:
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><style>''' + fonts() + '''
    *{box-sizing:border-box}body{margin:0;padding:48px 64px;background:#f9f9f9;color:#131313;font:20px/1.5 Geist,sans-serif}
    h1,h2,h3{font-family:'Instrument Serif',Georgia,serif;font-weight:400;font-size:48px;line-height:1.1;margin:0 0 24px}
    h4{font-size:24px}p{max-width:65ch}a{color:inherit;text-underline-offset:4px}code{font-size:.85em}table{width:100%;border-collapse:collapse;font-size:18px}td,th{padding:12px;text-align:left;border-bottom:1px solid #b8b8b5}img{max-width:100%;display:block}.wave{margin-top:48px}small{color:#585858}ul{padding-left:24px}
    </style><body>''' + body + '</body></html>'


def canvas_preview(source: Path) -> str:
    data = json.loads(source.read_text())
    nodes = {n['id']: n for n in data['nodes']}
    board = data['nodes'][0]
    shapes = []
    for n in data['nodes']:
        if n['type'] == 'group':
            shapes.append(f'<rect x="{n["x"]}" y="{n["y"]}" width="{n["width"]}" height="{n["height"]}" rx="8" fill="none" stroke="{n.get("color", "#4a6080")}" stroke-width="2"/>')
            if n is not board:
                shapes.append(f'<text x="{n["x"]+12}" y="{n["y"]+24}" fill="#d9dfec" font-size="16">{html.escape(n.get("label", ""))}</text>')
    def endpoint(node, side):
        x, y, w, h = (node[k] for k in ['x', 'y', 'width', 'height'])
        return {'left': (x, y+h/2), 'right': (x+w, y+h/2), 'top': (x+w/2, y), 'bottom': (x+w/2, y+h)}[side]
    for edge in data['edges']:
        x, y = endpoint(nodes[edge['fromNode']], edge.get('fromSide', 'right'))
        a, b = endpoint(nodes[edge['toNode']], edge.get('toSide', 'left'))
        shapes.append(f'<path d="M{x},{y} L{a},{b}" fill="none" stroke="{edge.get("color", "#8c9bb7")}" stroke-width="2" marker-end="url(#arrow)"/>')
        if edge.get('label'):
            shapes.append(f'<text x="{(x+a)/2}" y="{(y+b)/2-8}" text-anchor="middle" fill="#d9dfec" font-size="13" paint-order="stroke" stroke="#111827" stroke-width="5">{html.escape(edge["label"])}</text>')
    for n in data['nodes']:
        if n['type'] != 'text':
            continue
        text = html.escape(n['text']).replace('\n', '<br>').replace('**', '').lstrip('# ')
        shapes.append(f'<foreignObject x="{n["x"]}" y="{n["y"]}" width="{n["width"]}" height="{n["height"]}"><div xmlns="http://www.w3.org/1999/xhtml" style="height:100%;border:2px solid {n.get("color", "#63738e")};border-radius:8px;padding:12px;background:#1b2435;color:#e7edf7;font:16px/1.35 Geist,sans-serif;overflow:hidden">{text}</div></foreignObject>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {board["width"]} {board["height"]}" style="width:100%;background:#111827"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="#8c9bb7"/></marker></defs>' + ''.join(shapes) + '</svg>'
    return document('<h1>Obsidian Canvas · Architecture</h1>' + svg + '<small>Preview rendered from the actual JSON Canvas file.</small>')


def main() -> None:
    prepare_fonts()
    SCRATCH.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(exist_ok=True)
    catalog = json.loads((HERE / 'catalog.json').read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
        page.route('**/*', lambda route: route.abort() if route.request.url.startswith(('http:', 'https:')) else route.continue_())
        for section in catalog['sections']:
            for card in section['cards']:
                spec = card['preview']
                source = FIGURES / spec['source']
                kind = spec['kind']
                target = PREVIEWS / (card['id'] + '.jpg')
                if kind == 'page':
                    page.goto(source.as_uri(), wait_until='load')
                    page.add_style_tag(content=fonts())
                    page.evaluate('document.fonts.ready')
                    region = page.locator(spec['selector']).first
                    region.wait_for(state='visible')
                    region.screenshot(path=str(target), type='jpeg', quality=84, animations='disabled')
                else:
                    if kind == 'video':
                        frame = SCRATCH / (card['id'] + '.png')
                        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(spec['time']), '-i', str(source), '-frames:v', '1', '-vf', 'scale=1440:-1', str(frame)], check=True)
                        body = '<img src="' + data_uri(frame) + '" style="width:100%;height:100vh;object-fit:contain">'
                        page.set_content(document(body).replace('padding:48px 64px', 'padding:0'))
                    elif kind == 'image':
                        mime = 'image/svg+xml' if source.suffix == '.svg' else 'image/png'
                        uri = f'data:{mime};base64,' + base64.b64encode(source.read_bytes()).decode()
                        page.set_content(document('<img src="' + uri + '" style="width:100%;height:100vh;object-fit:contain">').replace('padding:48px 64px', 'padding:0'))
                    elif kind == 'canvas':
                        page.set_content(canvas_preview(source))
                    elif kind == 'document':
                        page.set_content(document(markdown(source.read_text())))
                    elif kind == 'audio':
                        waveform = SCRATCH / (card['id'] + '.png')
                        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source), '-filter_complex', 'showwavespic=s=1312x450:colors=0x131313', '-frames:v', '1', str(waveform)], check=True)
                        page.set_content(document('<small>QWEN / LOCAL NARRATION</small><h1>' + html.escape(card['title']) + '</h1><p>' + html.escape(card['description']) + '</p><img class="wave" src="' + data_uri(waveform) + '"><p>Actual recording · Native speech speed · Added reading pauses</p>'))
                    else:
                        raise ValueError(kind)
                    page.evaluate('document.fonts.ready')
                    page.locator('img').evaluate_all('(images)=>Promise.all(images.map(i=>i.decode()))')
                    page.screenshot(path=str(target), type='jpeg', quality=84, animations='disabled')
                spec['image'] = str(target.relative_to(HERE))
                print('Captured ' + card['title'], flush=True)
        browser.close()
    (HERE / 'catalog.json').write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
