"""Small rendering helpers for the local result catalog."""
import base64
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parents[1]
REPO = FIGURES.parent


def data_uri(path: Path) -> str:
    types = {'.jpg': 'image/jpeg', '.png': 'image/png', '.ttf': 'font/ttf'}
    return f"data:{types[path.suffix]};base64," + base64.b64encode(path.read_bytes()).decode()


def fonts() -> str:
    return '\n'.join(
        f"@font-face{{font-family:'{family}';src:url('{data_uri(HERE / 'fonts' / file)}') format('truetype');font-weight:{weight};font-display:swap;}}"
        for family, file, weight in [('Geist', 'Geist.ttf', '100 900'),
                                     ('Instrument Serif', 'InstrumentSerif-Regular.ttf', '400')]
    )


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',
                  r'<a href="\2">\1</a>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)


def markdown(source: str) -> str:
    """Render the paragraphs, lists, and tables used by this catalog's index."""
    lines = source.strip().splitlines()
    output = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            output.append('<div class="table-scroll"><table><thead><tr>' +
                          ''.join('<th scope="col">' + inline(c) + '</th>' for c in rows[0]) +
                          '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(
                              '<td>' + inline(c) + '</td>' for c in row) + '</tr>'
                              for row in rows[1:]) + '</tbody></table></div>')
        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append('<li>' + inline(lines[i].strip()[2:]) + '</li>')
                i += 1
            output.append('<ul>' + ''.join(items) + '</ul>')
        elif line.startswith('#'):
            level = min(4, max(3, len(line) - len(line.lstrip('#'))))
            output.append(f'<h{level}>' + inline(line.lstrip('#').strip()) + f'</h{level}>')
            i += 1
        else:
            paragraph = []
            while i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('|', '#', '- ')):
                paragraph.append(lines[i].strip())
                i += 1
            output.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    return '\n'.join(output)
