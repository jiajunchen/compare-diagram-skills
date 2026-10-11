"""Build the visual README with embedded fonts and captured preview images."""
import html
import json
from pathlib import Path

from support import FIGURES, HERE, data_uri, fonts, markdown


def anchor(item: dict, css: str = '') -> str:
    return f'<a class="{css}" href="{html.escape(item["href"], quote=True)}">{html.escape(item["label"])}</a>'


def render_card(card: dict, section: dict, index: int) -> str:
    image = data_uri(HERE / card['preview']['image'])
    search = ' '.join([card['title'], card['description'], card['badge'], card['details'],
                       *[r['label'] for r in card['repositories']]])
    repositories = ''.join('<li>' + anchor(r) + '<span>' + html.escape(r['role']) + '</span></li>'
                           for r in card['repositories'])
    details = ''
    if card['details']:
        label = {'diagram-sets': 'All diagrams and export formats', 'tutorial-videos': 'Open an individual lesson',
                 'audio': 'Listen to an individual lesson'}.get(section['id'], 'More files')
        details = '<details class="files"><summary>' + label + '</summary>' + markdown(card['details']) + '</details>'
    audio = ''
    if card['preview']['kind'] == 'audio':
        audio = '<audio controls preload="none" aria-label="' + html.escape(card['title']) + '" src="' + card['primary']['href'] + '"></audio>'
    return f'''<article class="result" id="result-{card['id']}" data-search="{html.escape(search, quote=True)}">
      <figure><button class="preview" type="button" aria-label="Enlarge preview: {html.escape(card['title'])}" data-preview-title="{html.escape(card['title'], quote=True)}">
        <img src="{image}" width="1440" height="900" loading="lazy" alt="{html.escape(card['imageCaption'], quote=True)}"></button>
        <figcaption><span class="figure-label">Fig. {index}</span> {html.escape(card['imageCaption'])}</figcaption></figure>
      <div class="result-content"><p class="eyebrow">{html.escape(card['badge'])}</p><h3>{html.escape(card['title'])}</h3>
        <p class="description">{html.escape(card['description'])}</p><div class="open-row">{anchor(card['primary'], 'primary')}<span aria-hidden="true">↗</span></div>
        {audio}<div class="file-links">{''.join(anchor(a) for a in card['links'])}</div>{details}
        {('<div class="provenance"><h4>Used to make this</h4><ul>' + repositories + '</ul></div>') if repositories else ''}
      </div></article>'''


def main() -> None:
    catalog = json.loads((HERE / 'catalog.json').read_text())
    sections = []
    index = 0
    for section in catalog['sections']:
        cards = []
        for card in section['cards']:
            index += 1
            cards.append(render_card(card, section, index))
        sections.append(f'''<section class="collection" id="{section['id']}" aria-labelledby="heading-{section['id']}">
          <header class="section-head"><h2 id="heading-{section['id']}">{html.escape(section['title'])}</h2><p>{html.escape(section['intro'])}</p></header>
          <div class="results-grid">{''.join(cards)}</div></section>''')
    choices = [('all', 'All results'), ('architecture-videos', 'Architecture videos'), ('tutorial-videos', 'Instruction videos'),
               ('html-guides', 'HTML guides'), ('diagram-sets', 'Diagram sets'), ('audio', 'Audio'), ('references', 'References & tools')]
    filters = ''.join(f'<button type="button" data-filter="{id}" aria-pressed="{str(id=="all").lower()}">{label}</button>' for id, label in choices)
    featured = next(card for section in catalog['sections'] for card in section['cards'] if card['id'] == 'diagram-design')
    replacements = {'{{FONTS}}': fonts(), '{{FILTERS}}': filters, '{{SECTIONS}}': ''.join(sections),
                    '{{FEATURED}}': data_uri(HERE / featured['preview']['image']),
                    '{{COMPLETE_INDEX}}': markdown(catalog['completeIndexMarkdown'])}
    page = (HERE / 'template.html').read_text()
    for token, value in replacements.items():
        page = page.replace(token, value)
    assert '{{' not in page, 'Unfilled template token'
    output = FIGURES / 'README.html'
    output.write_text('\n'.join(line.rstrip() for line in page.splitlines()) + '\n')
    (FIGURES / 'index.html').write_bytes(output.read_bytes())
    print(f'Built {output.name}: {index} preview collections, {output.stat().st_size / 1024 / 1024:.1f} MiB; no external rendering dependencies.')


if __name__ == '__main__':
    main()
