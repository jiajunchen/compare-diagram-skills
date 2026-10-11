# Original architecture narration — editorial rebuild

The original pre-ASD-STE100 architecture explanation is restored in the newer Diagram Design style. The video runs **10 minutes 14 seconds**, with **13 chapters**, **62 original narration passages**, **1920 × 1080** resolution and **30 fps**.

Play `architecture-video.mp4`, or open `index.html` for chapter navigation. `presentation.html` contains the self-contained slide source and complete script.

## Preserved content

The narration text, chapter order and timings come from Git revision `7179657`, before the STE revision. The retained original WAV was recovered from the local production cache. All 62 speech passages were compared byte-for-byte with their original cached PCM recordings; every passage matched. The recovered WAV is copied into this folder, and its hash is recorded in `recovery-validation.json`.

**No new speech generation, ElevenLabs requests or credits were used.** This version uses the original ElevenLabs recording, not the later Qwen tutorial voice. No simplification or rewrite was applied to the narration. The video represents the original technical explanation at that historical source revision; it is not a new audit of later app changes.

All previous architecture and instruction videos remain unchanged. Their hashes are recorded in `preserved-videos.json`.

## Design and fidelity

Skill: [Diagram Design](https://github.com/cathrynlavery/diagram-design), version 2.6, cached revision `75f47bbae5db21d2269a0c5134b22ce342686db4`.

The approved [atlas style receipt](../diagram-design/style-guide.md) supplies the Maria Vasilyeva-inspired palette and disclosed font substitutes: paper `#f9f9f9`, ink `#131313`, supporting gray `#585858`, Instrument Serif, Geist and Geist Mono. Focal elements use inverse black and white. No shadows or saturated highlights are introduced.

The rebuild reuses the seven atlas diagrams and adds four matching detail diagrams: record relationships, upload states, scrubbing and favorites/offload. Thirteen chapters use eleven unique diagrams plus the opening slide; schedule extraction and confirmation share one complete diagram with different focus outlines. Each diagram has at most six nodes, with orthogonal, labeled connectors.

The original narration is preserved in full. Diagram nodes summarize responsibilities so longer function-level detail can remain in the spoken explanation and captions. The upload diagram puts the temporary-failure return in its coordinator label rather than adding a crossing return arrow. The record diagram names both clip IDs inside the clip node rather than drawing an extra parent link. No narration is dropped.

Complete diagrams remain visible while a current-component outline changes with each narration passage. This uses the same quiet, static scene treatment as the newer editorial video. Captions retain the original technical terms. Original source diagrams and wording are also retained in `original-script.md`.

## Outputs and validation

- `architecture-video.mp4`: complete chaptered video with burned-in captions.
- `index.html`: responsive player with thirteen chapter buttons.
- `presentation.html`: inline SVG slides and complete narration.
- `narration.wav`: recovered original speech track.
- `narration.md`: plain reading script.
- `architecture-video.srt`: presentation captions; `original-captions.srt` preserves original speech boundaries.
- `recovery-validation.json`: original script, audio duration and cached speech matches.
- `diagram-validation.json`: skill self-check and all eleven diagram geometry checks.
- `frame-validation.json`: all 62 frames, loaded fonts, caption and node bounds.
- `validation.json`: full decode, format, timing, chapter count and prior-video preservation.
- `playback-validation.json`: encoded chapter images compared with source frames, plus browser playback.

Intro, records, upload states and scrubbing frames were visually inspected. Node and caption bounds were checked across every rendered frame.

## Reproduce

Keep the original diagram atlas in `../diagram-design/`, its drawing helper in `figures/tools/diagram-design/build.py`, and the recovered narration WAV in this folder. The original Git revision, retained speech cache and recovery metadata document its provenance.

```sh
.venv/bin/python figures/tools/editorial-architecture-original/prepare.py
.venv/bin/python figures/tools/editorial-architecture-original/render.py
.venv/bin/python figures/tools/editorial-architecture-original/check_diagrams.py
.venv/bin/python figures/tools/editorial-architecture-original/encode.py
.venv/bin/python figures/tools/editorial-architecture-original/package.py
.venv/bin/python figures/tools/editorial-architecture-original/verify.py
.venv/bin/python figures/tools/editorial-architecture-original/verify_playback.py
```

Tools: existing Python/Playwright, Google Chrome, ffmpeg and the cached Diagram Design checker under `/tmp/sports-diagram-design`. `recover.py` records the initial recovery from Git and the retained `/tmp/sports-architecture-narration.wav`; ordinary rerenders use the durable copy here and do not need that temporary file. No API key is read by this pipeline. Large media and temporary frames are ignored by Git.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/editorial-architecture-original](../tools/editorial-architecture-original). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
