# Parent and fencer guide — paced edition

Open `index.html` for the chapter player and lesson downloads, or play `parent-fencer-guide.mp4` directly. The first edition in `../parent-fencer-tutorial/` remains unchanged.

This edition runs approximately **7 minutes 45 seconds** at 1920 × 1080, 30 fps. It includes:

- Seven numbered title pages, each with a short spoken introduction in the same voice.
- Half-second slide transitions into each demonstration and between demonstrations.
- One second of frozen captured video at every marked tap or slider action. The red rectangle and pointer retain their original durations. The remark ends before the underlying recording resumes.
- A one-second reading pause after each instruction, increased to two seconds at review screens, results, and important explanations.
- Speech-aligned script highlighting and the original control magnification.

The original seven workflows, fictional demo media, and real iPad simulator recording are reused. Cloud services in that capture were simulated; this does not verify live iCloud synchronization. Only title narration required new speech generation. Existing instructional speech is unchanged and repositioned on the revised timeline.

## Files

- `parent-fencer-guide.mp4`: complete revised guide with seven chapter markers.
- `lesson-01.mp4` through `lesson-07.mp4`: standalone lessons, each starting on its own title page.
- `narration.md` and `captions.srt`: complete script and timed captions.
- `validation.json`: export, alignment, chapter-player and preservation results.
- `hold-validation.json`: all 43 marked actions verified to contain 30 identical background frames during the one-second hold.

## Reproduction

Use the same Python environment, Chrome, Playwright, ffmpeg, and `.env` ElevenLabs configuration as the original production. Keep the original tutorial folder: its captured footage, instruction audio, fonts, and slide backgrounds are reused.

Run in this order:

1. `synthesize_titles.py` — generate/cache only the seven spoken titles, without logging the key.
2. `prepare.py` — construct the master timeline, silent pauses, combined audio, script, and title images.
3. `compose.py` — render the instructional segments with the one-second action holds.
4. `check_holds.py` — verify all frozen backgrounds and remark timing.
5. `transitions.py` — render the title cards and slide transitions.
6. `export.py` — assemble the full video, standalone lessons, captions, and chapter player.
7. `validate.py` — check all eight exports, narration alignment, navigation, and preservation of the first edition.

The title cards, transition, and before/during/after tap samples were visually inspected. The application and its simulator capture were not modified for this revision.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/parent-fencer-tutorial-paced](../tools/parent-fencer-tutorial-paced). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
