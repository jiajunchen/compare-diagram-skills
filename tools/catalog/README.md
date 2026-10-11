# Visual result catalog

Open [README.html](../../README.html). It is the primary result index, with previews for every collection, complete file links, source repositories, search, category filters, and an enlarged preview viewer.

The HTML embeds its fonts and screenshots. It needs no server or network connection. Links to videos, audio, and other results use the existing local files. Finished media is included in the public repository; raw production assets remain local. The builder writes identical `index.html` and `README.html` entry pages for GitHub Pages and offline use.

## Source and preview files

- [catalog.json](catalog.json) contains the collection descriptions, result links, repository links, preview sources, and the complete original file index.
- [capture_previews.py](capture_previews.py) captures the existing results. Video previews come from finished exports. Audio previews use their real waveforms. Canvas and documentation previews render the actual source data in a browser and are labeled as such.
- [previews/](previews/) retains the captured JPEG images so ordinary rebuilds do not need to recapture results.
- [template.html](template.html) defines the editorial layout, navigation, search, preview dialog, and responsive styles.
- [build.py](build.py) embeds the screenshots and fonts into the finished HTML.
- [verify.py](verify.py) checks complete link coverage, embedded previews, offline display, search, filters, keyboard controls, and desktop/mobile layout.

## Rebuild

Run from the repository root with the existing Python and Playwright environment:

```sh
python3 -B tools/catalog/build.py
python3 -B tools/catalog/verify.py
python3 -B -m unittest discover -s tools/catalog -p test_publishing.py
```

To refresh screenshots from the saved results first:

```sh
python3 -B tools/catalog/capture_previews.py
python3 -B tools/catalog/build.py
```

Capture uses Chrome and FFmpeg. It does not synthesize speech, read API keys, or modify existing results. Temporary extracted frames and waveforms go to `.runtime/figures/catalog/`. The approved fonts are bundled under [fonts/](fonts/), with their Open Font Licenses. The initial capture downloads a missing font from Google Fonts; ordinary builds and checks work offline.

## Design sources

The catalog applies [Visual Explainer](https://github.com/nicobailon/visual-explainer) using the existing [Diagram Design editorial style](../../diagram-design/style-guide.md). Its font and screenshot helpers use the Python standard library. Browser capture and verification use [Playwright for Python](https://github.com/microsoft/playwright-python); frame and waveform extraction use [FFmpeg](https://github.com/FFmpeg/FFmpeg).
