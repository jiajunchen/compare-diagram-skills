# Visual results catalog

Visit the [live catalog](https://jiajunchen.github.io/compare-diagram-skills/) to browse all diagrams, architecture videos, instruction videos, narration experiments, and references. Individual HTML pages open directly in your browser.

For offline use, download the repository and open [index.html](index.html) or [README.html](README.html).

Each collection has a screenshot or labeled source preview, links to its finished files, and the skill or package repositories used to create it. Search, category filters, and enlarged previews help you find a result. The catalog works offline; video and audio links require the files retained in this workspace.

The complete file and reference index is also included in the HTML catalog. Production sources remain in [tools/](tools/README.md); the [catalog guide](tools/catalog/README.md) explains how to rebuild its previews and page.

## Publishing

GitHub Pages serves the `main` branch from the repository root. Rebuild both catalog entry pages with `python3 -B tools/catalog/build.py`, then check their links with `python3 -B -m unittest discover -s tools/catalog -p test_publishing.py` before committing and pushing updates.

Finished media is included. Raw recordings, production assets, temporary files, and local speech segments remain outside Git. Some diagram source references point to the original application code, which is not included in this results repository.
