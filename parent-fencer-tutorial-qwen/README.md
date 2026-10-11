# Parent and fencer guide — Qwen instructional edition

Play `parent-fencer-guide.mp4`, or open `index.html` to choose a lesson. This edition runs **6 minutes 56 seconds** at **1920 × 1080, 30 fps**. The full guide and seven standalone lesson videos are in this new folder. All earlier video editions and the approved Qwen audio files are preserved.

## What changed

The video uses the approved Aiden narration from `../local-qwen-narration/instructional/`. Each captured screen action is retimed around that recording. The speech is not regenerated, sped up, slowed down, or pitch shifted.

The existing editorial layout, seven numbered title pages, thirteen slide transitions, control magnification, and red click marks remain. Each marked action freezes the background for one second, and its red mark disappears before the captured screen advances.

The right-side transcript follows newly measured Qwen word timings. The current word is red and underlined, completed words are dark, and upcoming words are gray. During silent gaps, no word remains red. The title pages also show speech-aligned transcript highlighting. Exported captions use the measured speech boundaries.

## Timing

The approved audio has 70 passages: seven titles and 63 action paragraphs. The local Qwen3 ForcedAligner 0.6B, 8-bit model measured 818 words against those exact recordings. Its timestamp resolution is 80 ms. Twenty zero-length function-word predictions are displayed for one frame around their measured boundary. These are automatic estimates, not manually annotated phoneme timings.

The assembled narration preserves every source speech sample exactly. Original action pauses are retained. Half-second slide transitions and up to one video frame of silence at passage boundaries bring the video duration to **416.10 seconds**, compared with **408.74 seconds** for the standalone listening version. Audio remains at its natural playback speed.

## Files

- `parent-fencer-guide.mp4`: full guide with seven chapter markers.
- `lesson-01.mp4` through `lesson-07.mp4`: separate lessons beginning with their title pages.
- `index.html`: chapter player and downloads.
- `captions.srt`: timed captions.
- `narration.md`: complete narration text.
- `validation.json`: export, playback, transcript-source, and preservation checks.
- `timing-validation.json`: source speech sample identity, frame clock, and word bounds.
- `hold-validation.json`: 30 identical background frames at each of the 43 marked actions.

## Reproduction

Keep the original tutorial's simulator recording, cached slide backgrounds and fonts, the paced edition's title images, and the approved Qwen segment audio. No ElevenLabs key is needed.

From the repository root:

```sh
.runtime/qwen-tts/.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/align.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/prepare.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/check_timeline.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/compose.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/check_holds.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/transitions.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/export.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/validate.py
```

The shared title images are preserved in `figures/tools/assets/parent-fencer-tutorial-paced/`. The renderer reads them directly. Temporary render files are recreated under `.runtime/figures/parent-fencer-tutorial-qwen/`. Rendering uses the installed ffmpeg and Chrome/Playwright tools. The aligner runs locally; its weights are downloaded to the existing local model cache on first use. The speech server is not needed to render this edition.

The simulator footage uses fictional names and demo media. Its cloud services were simulated, as in the earlier videos. This edition does not verify live iCloud synchronization.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/parent-fencer-tutorial-qwen](../tools/parent-fencer-tutorial-qwen). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
