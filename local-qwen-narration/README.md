# Local Qwen3-TTS narration trial

This folder contains a local speech alternative for the parent and fencer tutorial. It reuses the seven scripts and spoken lesson titles from `../parent-fencer-tutorial-paced/timeline.json`. It does not rebuild or change any video. No ElevenLabs service or key is used.

## Listen

- `sample-ryan.wav`: short English voice sample.
- `qwen-narration.mp3`: all seven lessons, with two seconds between lessons.
- `qwen-narration.wav`: uncompressed combined audio.
- `lesson-01.wav` through `lesson-07.wav`: individual lessons.
- `narration.md`: exact narration text.

These are listening tests. Speech durations differ from the existing video; this audio is not a synchronized replacement soundtrack. Pronunciation and tone should be judged by listening before using it in a new video.

## Model choice

Machine: Mac mini, Apple M4, 10 CPU cores, 10 GPU cores, 24 GB unified memory. The server runs MLX Audio 0.5.8 on Apple's Metal GPU in an isolated Python 3.12 environment.

Model: `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit`, preset voice **Ryan**, English. The official checkpoint is named **0.6B CustomVoice**, while its Hugging Face card lists approximately **0.9B total parameters**. This is the small model discussed in the request. Eight-bit weights provide a conservative quality choice on this machine. Only one request runs at a time. The downloaded model cache occupies about 1.8 GB; runtime memory is substantially larger.

Sources: [official model](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice), [MLX conversion](https://huggingface.co/mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit), [MLX Audio](https://github.com/Blaizzy/mlx-audio).

## Server

The server is bound to **127.0.0.1:8765**. API documentation: <http://127.0.0.1:8765/docs>. It stays running after generation, but does not auto-start after reboot. The server was already stopped when the folders were organized; use `start` when needed. Run these commands from the repository root:

```sh
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/server_control.py status
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/server_control.py start
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/server_control.py stop
```

To regenerate missing outputs:

```sh
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/generate.py sample
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/generate.py all
```

New generation requests reuse files whose request hash matches. The original request caches were removed during cleanup; the finished audio and measurement reports were preserved. Delete the corresponding WAV to force a new take. Text-to-speech requests use the local `/v1/audio/speech` endpoint. The model was downloaded once from Hugging Face. Speech inference runs locally and requires no speech API credits. The server does not read the project's `.env`.

## Reproduce the environment

```sh
/opt/homebrew/bin/python3.12 -m venv .runtime/qwen-tts/.venv
.runtime/qwen-tts/.venv/bin/pip install -r figures/tools/local-qwen-narration/requirements-lock.txt
```

`hardware.json` records the tested model revision. `.runtime/figures/local-qwen-narration/server.log` holds server diagnostics. The virtual environment, weights and generated audio are local ignored files; scripts, reports and narration are tracked.

## Measurements and verification

`sample-report.json` includes the cold request, including first download and loading. `generation-report.json` measures the seven subsequent requests with the model loaded. Its real-time factor is generation seconds divided by audio seconds; below 1 means faster than playback.

**Do not interpret process RSS as total model memory.** MLX uses Metal allocations that are not fully represented by RSS. `validation.json` records macOS physical footprint and its lifetime peak after the full run, alongside audio signal checks and model health. The peak includes transient decoding allocations. Audio decode and signal checks cannot establish narration quality.

Run verification with:

```sh
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/verify.py
```

### Observed results on this Mac

- Seven lessons: 396.72 seconds of generated audio, 410.72 seconds including the added lesson pauses.
- Warm generation: 220.63 seconds total, 1.80 times playback speed.
- macOS physical footprint after generation: 3.2 GB; lifetime peak: 17.2 GB (rounded macOS figures).
- All WAVs: mono, 24 kHz, 16-bit PCM; no clipped samples and no silence of two seconds or more within individual lessons. The combined file has intentional pauses between lessons.
- Combined MP3 fully decoded without errors. All four prior full-length video hashes are unchanged.

This small model is operationally feasible on this 24 GB machine. The observed decoding peak leaves limited room for other large workloads; the larger 1.7B model is not recommended for this setup based on this trial. For future video production, generating short narration segments would also allow more precise timing and may reduce transient decoding memory. That segmented configuration was not benchmarked in this trial.

## Model location after cleanup

Downloaded model weights are preserved in `.runtime/qwen-tts/huggingface/hub/`, outside the finished-results folder. The isolated environment is `.runtime/qwen-tts/.venv/`. Server logs and request caches are disposable files under `.runtime/figures/local-qwen-narration/`. See the [tools guide](../tools/README.md).

## Production tools after cleanup

Generation and verification code moved to [figures/tools/local-qwen-narration](../tools/local-qwen-narration). Run the commands above from the repository root. Disposable render files now go under `.runtime/figures/`; finished exports remain here. See the [shared tools guide](../tools/README.md).
