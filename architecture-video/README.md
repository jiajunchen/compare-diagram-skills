# Architecture video explainer

The revised video is about 9 minutes 8 seconds, with a plain-language narration and two opening chapters about the app.

Open [architecture-video.html](architecture-video.html) for the narrated offline player, or play [architecture-video.mp4](architecture-video.mp4).

The 1080p explainer uses the requested skill’s 3b1b dark theme, progressive diagrams, focus highlights, captions, and ElevenLabs narration. It explains implementation behavior, not a recorded app session.

## Chapters

- 00:00 — How the Fencing Review App Works
- 00:06 — Why this app exists
- 00:45 — Follow one bout through the app
- 01:21 — How the app connects the records
- 01:58 — Which part does each job
- 02:36 — What happens when the app opens
- 03:14 — How the app reads a schedule
- 03:53 — Why the parent must confirm the schedule
- 04:31 — How recordings enter a bout
- 05:10 — How the app creates a review clip
- 05:49 — How a review clip reaches iCloud
- 06:29 — How the app plays the review clips
- 07:06 — How the picture follows the slider
- 07:43 — How the app handles changes and deletions
- 08:22 — Favorites, storage, and the main idea

## Plain-language revision

The narration follows the requested practical 80% STE target. Sentences average 9.5 words; the longest has 18 words. The script defines unfamiliar terms before use and keeps most code names in diagrams. The renderer reports zero writing warnings. See the language review for the scope of these checks.

## Source and generation

- App executable source: unchanged from `8a8c101`; inspected checkout began at `9d02ca9`.
- Narration date: October 7, 2026.
- Skill: [answer-me-with-html](https://github.com/QingYunA/answer-me-with-html/blob/main/skills/answer-me-with-html/SKILL.md).
- Renderer revision: `b3c796e30b516584ea39b52ebf6544699be1dc7a`, CLI 0.3.0.
- Voice provider: ElevenLabs, `eleven_multilingual_v2`, renderer default stock voice `JBFqnCBsd6RMkjVDRZzb`.
- Plain reading copy: [narration.md](narration.md).
- Diagram and narration source: [architecture-video.md](architecture-video.md).
- Writing approach and glossary: [language-review.md](language-review.md).
- Sentence measurements: [language-validation.json](language-validation.json).
- Captions: [architecture-video.srt](architecture-video.srt).
- Exact chapter times: [chapters.json](chapters.json).
- Detailed written reference: [architecture guide](../answer-me-with-html/architecture.html).

The render wrapper applies two compatibility adjustments to the pinned skill bundle: it measures uncapped diagram width and reserves caption space; it reuses identical frames during static narration holds. All 71 holds were checked for pixel equality after their animation windows. The MP4 retains 30 frames per second.

The detailed scope uses fourteen short scenes so each mechanism remains legible. Diagrams group selected service calls; the written guide preserves the complete function declaration index.

## Regenerate

Use Node 22+, Chrome, ffmpeg, and a checkout of the renderer revision above. Run from the app repository root:

```sh
python3 figures/tools/architecture-video/check_language.py
node figures/tools/architecture-video/render.mjs /path/to/answer-me-with-html
.venv/bin/python figures/tools/architecture-video/verify.py
python3 figures/tools/architecture-video/finalize.py
```

For HTML and narration only, append `--html-only` to the rendering command. The renderer caches synthesized speech, so unchanged narration can be reused without another TTS request.

The wrapper reads the ignored repository `.env` or the process environment. It accepts `ELEVENLABS_API_KEY` and the existing `ElevenLab_API` name. Credentials are never included in the media.

Generated HTML, MP4, and poster remain local and are ignored by Git because they contain large media payloads. Authoring files, captions, chapter metadata, and validation are committed.

## Validation

Browser checks confirm fourteen chapter markers, successful audio playback, 71 ordered narration segments, no caption/diagram collisions, no out-of-frame diagram labels, no script errors, and no external resource requests. The audio and player timelines match within one tenth of a second.

Representative chapter frames were visually inspected. No app executable code changed; app simulator suites were not rerun.

The final MP4 contains the introduction and fourteen chapter markers. Its complete video and audio streams passed a full decode check; the final duration matches the player timeline.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/architecture-video](../tools/architecture-video). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
