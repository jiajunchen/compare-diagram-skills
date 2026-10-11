# Fencing Video Analysis architecture guide

Open [architecture.html](architecture.html). It is a standalone, offline HTML explainer generated with the user-requested [answer-me-with-html skill](https://github.com/QingYunA/answer-me-with-html/blob/main/skills/answer-me-with-html/SKILL.md).

The eight chapters cover structure and storage, launch and organization, schedule extraction, Photos import and source reopening, clip export/upload, playback/cache/favorites, cloud recovery/deletion, and a complete named Swift-function declaration index. The guide contains 11 diagrams, a directory tree, action-to-function tables, and source references for all 35 Swift files (276 named function declarations, including overloads, protocols, and fakes).

## Provenance

- App source inspected: `8a8c101` on 2026-10-03.
- Renderer repository: `QingYunA/answer-me-with-html`.
- Renderer commit: `b3c796e30b516584ea39b52ebf6544699be1dc7a` (CLI 0.3.0).
- Authoring source: [architecture.md](architecture.md).
- No skill installation or application-source changes were required.
- This is a static code walkthrough, not a runtime trace.

## Regenerate

With a checkout of that renderer revision, run from the app repository root:

```sh
node /path/to/answer-me-with-html/skills/answer-me-with-html/scripts/am.mjs render \
  figures/answer-me-with-html/architecture.md \
  -o figures/answer-me-with-html/architecture.html --no-open
```

The Markdown is the source of truth for the artifact; do not manually edit generated HTML. When updating it for another app revision, refresh the source index and revision metadata too.

## Validation

Run the existing repository Playwright environment:

```sh
.venv/bin/python figures/tools/answer-me-with-html/verify.py
```

[validation.json](validation.json) records checks at 1440×1000, 1024×768, and 390×844: chapter navigation, theme/mode controls, 11 rendered diagrams, 40 local links, no document horizontal overflow, no browser errors, and no external resource requests. Desktop overview and export diagrams were also visually inspected. The renderer reported zero writing warnings.

No app simulator or physical-device suites were rerun for this documentation-only work. Source links require the repository; the standalone HTML's content, navigation, diagrams, and themes work without it.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/answer-me-with-html](../tools/answer-me-with-html). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
