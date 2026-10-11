# Figure and video production tools

Finished results are indexed in [figures/README.html](../README.html). Run the commands below from the repository root. Each tool writes finished results back to its original named collection; shared paths are defined in [layout.py](layout.py).

## Folder layout

| Location | Contents | Retention |
| --- | --- | --- |
| `figures/<collection>/` | Finished diagrams, players, videos, audio, scripts of spoken narration, timelines, and validation reports | Keep |
| `figures/tools/diagrams/` | Original diagram generators and verifiers, dependency lists | Keep |
| `figures/tools/<collection>/` | Each presentation or narration pipeline's source code | Keep |
| `figures/tools/assets/` | Simulator source recordings, demo Photos media, capture clock, fonts, backgrounds, and title images | Keep locally; ignored by Git |
| `figures/local-qwen-narration/instructional/segments/` | Approved Aiden sentence recordings and request metadata | Keep locally; ignored by Git |
| `.runtime/figures/<collection>/` | Disposable render frames, subtitles, normalized footage, segment exports, and logs | Recreated as needed |
| `.runtime/qwen-tts/` | Downloaded model weights and the isolated Python environment | Keep locally; ignored by Git |

The former loose Graphviz files are now in `figures/graphviz/`. The former long figures README is preserved as [reference/codebase-analysis.md](../reference/codebase-analysis.md). [organization-report.json](organization-report.json) records moves, cleanup totals, and preserved-file hashes. Validation reports beside the outputs are retained production evidence; checks that compare source frames require a fresh render first.

## Check the organization

These checks inspect finished results without regenerating videos or requesting speech:

```sh
python3 figures/tools/verify_catalog.py
.venv/bin/python figures/tools/diagrams/verify_diagrams.py
.venv/bin/python figures/tools/diagrams/verify_legend_labels.py
.venv/bin/python figures/tools/answer-me-with-html/verify.py
.venv/bin/python figures/tools/local-qwen-narration/instructional/verify.py
.venv/bin/python figures/tools/parent-fencer-tutorial-qwen/check_timeline.py
```

`verify_catalog.py` checks local links, Python syntax, preserved media hashes, and absence of runtime files in the finished-results tree. The browser checks use the existing Playwright environment and local Chrome. The narrator assembly and timeline checks use the retained sentence recordings.

## Visual result catalog

The [catalog tools](catalog/README.md) build the HTML index from its collection descriptions, captured previews, and embedded fonts. The catalog includes the complete file and reference index from the earlier Markdown README.

```sh
.venv/bin/python -B figures/tools/catalog/build.py
.venv/bin/python -B figures/tools/catalog/verify.py
```

To refresh screenshots after changing a finished result, run `capture_previews.py` in the same folder before building. The verification checks work offline and do not regenerate video or speech.

## Diagrams

The diagram tools retain their original filenames and imports under [diagrams/](diagrams). Dependencies are in [requirements.txt](diagrams/requirements.txt) and [requirements-browser.txt](diagrams/requirements-browser.txt). The existing repository `.venv` remains the diagram and browser environment.

```sh
.venv/bin/python figures/tools/diagrams/generate_diagrams.py
.venv/bin/python figures/tools/diagrams/generate_call_index.py
.venv/bin/python figures/tools/diagrams/generate_interactive.py
.venv/bin/python figures/tools/diagrams/generate_cocoon.py
.venv/bin/python figures/tools/diagrams/generate_diagram_creator.py
.venv/bin/python figures/tools/diagrams/generate_obsidian_canvas.py
```

`generate_alternatives.py` produces the Diagrams and PlantUML sets. It requires the local PlantUML JAR at `.venv/tools/plantuml.jar`; see the [original environment notes](../reference/codebase-analysis.md). Regenerating that set replaces its exports, including PDFs edited manually.

The editorial atlas tools are in [diagram-design/](diagram-design); their provenance and commands are in the [atlas README](../diagram-design/README.md).

## Architecture presentations

| Tool folder | Results and production order |
| --- | --- |
| [architecture-video/](architecture-video) | [Dark 3b1b presentation](../architecture-video/README.md) |
| [editorial-architecture-video/](editorial-architecture-video) | [STE editorial presentation](../editorial-architecture-video/README.md) |
| [editorial-architecture-original/](editorial-architecture-original) | [Recovered original narration and editorial presentation](../editorial-architecture-original/README.md) |

The original editorial presentation can be rendered using its retained `narration.wav`, `timeline.json`, and the approved atlas. Its `recover.py` records the historical recovery operation; ordinary rerenders start with `prepare.py` and do not need temporary recovery files.

ElevenLabs response caches were removed. Running an ElevenLabs synthesis step can consume credits again. Existing narration and timelines are sufficient for rendering the completed editorial presentations; skip synthesis when reusing them. Renderers and encoders replace the result in their configured collection, so use a new collection when creating another edition.

## Parent and fencer videos

| Tool folder | Results and production order |
| --- | --- |
| [parent-fencer-tutorial/](parent-fencer-tutorial) | [First edition and simulator capture](../parent-fencer-tutorial/README.md) |
| [parent-fencer-tutorial-paced/](parent-fencer-tutorial-paced) | [Paced edition](../parent-fencer-tutorial-paced/README.md) |
| [parent-fencer-tutorial-qwen/](parent-fencer-tutorial-qwen) | [Qwen edition](../parent-fencer-tutorial-qwen/README.md) |

`CaptureTests.swift` is with the capture tool. Source recordings and demo media moved to `figures/tools/assets/parent-fencer-tutorial/`. The capture tool writes its clock there as well. Composers recreate normalized footage under `.runtime/figures/parent-fencer-tutorial/`. Fonts and slide backgrounds are shared source assets; the paced title images are in `assets/parent-fencer-tutorial-paced/` and are read directly by the Qwen transition renderer.

For a Qwen video rerender, existing approved audio and `alignment.json` allow skipping model inference. Run `prepare.py`, `check_timeline.py`, `compose.py`, `check_holds.py`, `transitions.py`, `export.py`, and `validate.py` in the order documented in its README.

## Local Qwen speech

The model environment moved intact from `figures/local-qwen-narration/.venv/` to `.runtime/qwen-tts/.venv/`. Downloaded TTS and alignment models remain in `.runtime/qwen-tts/huggingface/hub/`. The configured speech model is `mlx-community/Qwen3-TTS-12Hz-0.6B-CustomVoice-8bit`. The server was not running during cleanup and remains stopped.

```sh
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/server_control.py start
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/server_control.py status
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/instructional/generate.py
.runtime/qwen-tts/.venv/bin/python figures/tools/local-qwen-narration/server_control.py stop
```

The Aiden generator reuses the approved segment recordings when their request hashes match. Ryan request caches were removed; invoking its generator may synthesize again. Speech remains local on `127.0.0.1:8765`. Environment dependencies are preserved in [requirements-lock.txt](local-qwen-narration/requirements-lock.txt).

Temporary `.runtime/figures/` contents can be removed when no rendering or speech job is active. Keep `.runtime/qwen-tts/` to avoid downloading models and installing the environment again.
