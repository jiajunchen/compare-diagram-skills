# Instructional narration: Aiden

This is a separate voice revision for the seven parent and fencer lessons. The previous Ryan audio and all videos are preserved.

## Listen

- `preview.wav`: first lesson, for a quick comparison.
- `instructional-narration.mp3`: all seven revised lessons.
- `instructional-narration.wav`: lossless combined narration.
- `lesson-01.wav` through `lesson-07.wav`: individual lessons.

## What changed

The English preset changes from Ryan to Aiden. Qwen describes Ryan as strongly rhythmic and Aiden as a clear American male voice. The intended result is a more restrained instructional delivery; suitability remains a listening judgment.

Each spoken title and each action paragraph is generated separately. The script wording stays unchanged. Complete sentences preserve useful phrasing, while short passages limit long stretches of changing delivery. Sampling temperature changes from 0.6 to 0.3; this reduces sampling variation but does not guarantee a particular emotion or tone.

The assembly adds:

- 0.3 seconds before each lesson.
- 1.2 seconds after its title.
- 0.8 seconds after ordinary action paragraphs.
- 1.2 seconds after paragraphs about checks, confirmation, deletion, clearing, or favorites.
- 2 seconds after the final paragraph of a lesson.

These silences are added to the model's existing natural pauses. The small 0.6B model has limited documented instruction control: the upstream capability table marks instruction control for the 1.7B variant, while its model-card prose is broader. This revision therefore does not rely on a tone prompt. It uses voice choice, shorter passages and explicit pauses.

## Timing clarification

**Neither the earlier Ryan audio nor this Aiden revision was stretched or compressed to match the video.** Both used natural generated speech. The earlier version added two seconds between whole lessons. This version explicitly requests speed 1.0 and preserves every speech PCM sample during assembly. There is no pitch shift, tempo filter, resampling or duration fitting.

These are audio previews, not synchronized replacement soundtracks. A later video edit should align the screen actions and holds to the approved narration timing. `generation-report.json` records each segment's start time, speech duration and added pause for that future edit.

## Reproduce and verify

Run from the repository root, with the existing local server on port 8765:

```sh
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/instructional/generate.py
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/instructional/verify.py
```

The generator reuses matching cached segments. `validation.json` checks that lesson assembly is exactly the generated PCM plus the specified silence, that the combined output decodes, and that earlier audio and video hashes have not changed. These checks do not establish subjective pronunciation or tone quality.

Model: `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit`. No additional model download or external speech API is used.

Source: [Qwen3-TTS capabilities and voice descriptions](https://github.com/QwenLM/Qwen3-TTS).

## Completed output

Seven lessons, 70 separately generated passages, 408.74 seconds total (6 minutes 49 seconds). All speech samples are preserved exactly in the WAV assembly. Explicit pauses and the unchanged original audio/video hashes passed verification. The MP3 decoded successfully.

## Production tools after cleanup

Generation and verification code moved to [figures/tools/local-qwen-narration/instructional](../../tools/local-qwen-narration/instructional). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../../tools/README.md).
