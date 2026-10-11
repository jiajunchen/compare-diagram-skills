# Fencing Review — architecture atlas

Open [architecture.html](architecture.html). This is a separate diagram treatment from the earlier video and HTML guide.

Seven static SVG diagrams cover system boundaries, startup, schedule extraction, recording import, clip export/upload, playback/scrubbing, and synchronization/deletion. Each has a table of triggers, source declarations and behavior. A separate record/storage table describes data ownership. The document uses short explanatory sentences while keeping precise technical names visible.

## Skill and design

- Requested skill: [Cathryn Lavery's Diagram Design](https://github.com/cathrynlavery/diagram-design), revision `75f47bbae5db21d2269a0c5134b22ce342686db4`, skill metadata version 2.6.
- Reference: [Maria Vasilyeva Awwwards entry](https://www.awwwards.com/sites/maria-vasilyeva-portfolio), with tokens sampled from [the linked portfolio](https://www.mariavasilyeva.com/).
- [Style guide and font receipt](style-guide.md) document observed colors and disclosed font substitutes.
- Architecture type, full-editorial treatment, doc-wide canvas, six nodes per figure. Details split across figures to respect the skill complexity budget.
- Source snapshot: `92ab000`. App implementation was unchanged during this documentation task.

The skill's single-file checker rejects external navigation links as well as remote assets. Citations therefore appear as visible source text in the HTML and clickable links here. Google Fonts is its permitted remote rendering dependency. The HTML uses no scripts and remains readable with fallback fonts offline.

## Regenerate and check

```sh
python3 figures/tools/diagram-design/build.py
.venv/bin/python figures/tools/diagram-design/verify.py /path/to/diagram-design
```

The checker verifies accessible SVG, skill geometry rules, declaration references, loaded typography, text bounds, desktop overflow and mobile scrolling. The upstream geometry tool treats multiple SVG roots as one coordinate space, so it is run separately on each unchanged figure. No geometry rules are skipped.

The build verifies all function references against the Swift source and writes [source-index.json](source-index.json). Source links use relative paths and line fragments; not every file viewer understands the line fragment. [validation.json](validation.json) records the results.

No application code changed. App simulator suites are outside the scope of this documentation-only work.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/diagram-design](../tools/diagram-design). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
