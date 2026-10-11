# Parent and fencer instruction videos

Open `index.html` to watch the full guide, jump to a lesson, or download one of the seven individual videos. The full guide is `parent-fencer-guide.mp4`. `narration.md` contains the complete spoken script; `captions.srt` contains timed captions.

## What this demonstrates

1. Create Alex Rivera’s fencer profile and the fictional Autumn Practice Open tournament.
2. Select a demo schedule screenshot from Photos, read it with the app’s actual recognition pipeline, review it, and confirm the bouts.
3. Add Casey Jordan as an opponent through manual schedule entry.
4. Select two illustrated demo recordings from Photos and attach them to a bout.
5. Export two review clips from one recording, mark a clip as a favorite, and show the derived bout favorite indicator.
6. Delete the favorite clip, show the remaining clip, and show the now-empty bout star.
7. Clear uploaded local clip copies from the Fencer page.

The recordings come from a dedicated iPad Air simulator, in landscape. All names and practice media are fictional. The original app and its project are unchanged. `CaptureTests.swift` is compiled only through a temporary copy of the Xcode project.

The simulator uses the app’s existing fake CloudKit services. Photos selection, schedule recognition, local clip export, and user interfaces are real. Cloud upload, recovery, and removal are simulated; this production does not validate live iCloud behavior. The script describes the behavior implemented by the app. The demonstration includes the system Photos permission prompt and the Allow Full Access action.

## Presentation and timing

The film uses the previous editorial presentation’s paper, ink, fine rules, serif headings, and Geist text. Actual screen recordings are on the left; the spoken script is on the right. Word highlighting uses ElevenLabs character alignment. The recording is retimed per instruction so red tap marks and slider remarks match the spoken action. Small controls receive animated magnification. Each instruction occupies one timed segment inside its lesson slide.

The language uses short sentences, direct verbs, and consistent app labels. It follows the requested simplified-English approach; it is not certified ASD-STE100 compliance.

## Reproduction

Use the repository Python environment with Playwright, Chrome, ffmpeg with libass, and Xcode. The scripts contain the dedicated simulator identifier and Xcode location used for this production. Create/boot a compatible simulator and update those values if needed.

- `prepare_media.py`: generate non-private schedule and video fixtures. Add them to the simulator Photos library.
- `capture.py`: capture the seven lessons with the isolated UI test harness. Requires a successful `complete` event before composition.
- `synthesize.py`: produce audio and word alignment. Reads the ElevenLabs key privately from the repository `.env`; does not store it in outputs.
- `prepare_slides.py`: render editorial backgrounds.
- `compose.py`: render speech-aligned footage, control magnification, tap remarks, and script highlighting.
- `export.py`: assemble the full guide and seven lessons, captions, and the chapter player.

`capture-events.json` records actual action times and control bounds. `timeline.json` records narration alignment. `edit-plan.json` joins those clocks. Large recordings, generated media, audio, video exports, and caches are ignored by Git but remain in this folder locally.

## Verified result

The finished guide is 5 minutes 3.5 seconds at 1920 × 1080, 30 fps, with seven embedded chapters. It contains 63 spoken steps, 43 marked tap/slider actions, and 49 magnified segments. The final iPad UI capture passed. All eight exports decode successfully; video/audio lengths differ by less than 0.1 seconds. Chapter navigation passed at desktop and phone viewport sizes. Representative frames were inspected for control visibility and text layout. Both prior architecture videos retain their original SHA-256 hashes. See `validation.json` for export details.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/parent-fencer-tutorial](../tools/parent-fencer-tutorial). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
