# MVP codebase analysis

These diagrams trace the production Swift code on `mvp-codebase-analysis`.
The app has **one native SwiftUI frontend and no app-owned backend server**.
Its durable local store is SwiftData; private CloudKit synchronizes confirmed
metadata and edited clip assets. iCloud Photos remains the original-video
library. Simulator fakes and test fixtures are omitted from the diagrams.

## Diagrams

| Review question | Vector diagram | Print version | Ratio |
| --- | --- | --- | --- |
| How do UI, on-device services, local files, Photos, and CloudKit exchange data? | [01 Architecture](../graphviz/01_architecture.svg) | [PDF](../graphviz/01_architecture.pdf) | 16:9 |
| Which persisted records refer to which others? | [02A Entities](../graphviz/02a_entities.svg) | [PDF](../graphviz/02a_entities.pdf) | 16:9 |
| Which objects call the principal cross-component methods? | [02B Object calls](../graphviz/02b_object_calls.svg) | [PDF](../graphviz/02b_object_calls.pdf) | 16:9 |
| What happens during launch, tournament creation, and schedule confirmation? | [03A Organization pathways](../graphviz/03a_organization_pathways.svg) | [PDF](../graphviz/03a_organization_pathways.pdf) | 9:16 |
| What happens during recording import, trimming, upload, playback, and cleanup? | [03B Media pathways](../graphviz/03b_media_pathways.svg) | [PDF](../graphviz/03b_media_pathways.pdf) | 9:16 |

## Alternative renderers

The same five reviewed node and arrow definitions are also rendered with
[Python Diagrams](../diagrams_library/01_architecture.svg) and
[PlantUML](../plantuml/01_architecture.svg). Each folder contains all five numbered
figures as SVG, PDF, and PNG. The PlantUML folder also includes editable
`.puml` source. Both sets keep the original aspect ratios and on-page color
legends. The PlantUML figures use the Diagram Creator skill's default dark
palette: dark page and cards, bright category borders and swatches, and light
labels. The Diagrams version keeps its light palette. It uses `Diagram`,
`Cluster`, `Node`, and `Edge` objects; the PlantUML version uses
components/classes and PlantUML arrows.
The original figures remain the easiest to read when an arrow-dense page needs
close inspection.

## Interactive review set

The workspace-installed [architecture-diagram skill](https://github.com/konraddzbik/architecture-diagram-skill)
produces five self-contained HTML pages. Select a scenario and step through its
handoffs; click a node to jump to its first step, or drag nodes to rearrange the
canvas. The Local only / iCloud available control exposes cloud-dependent paths.
Each page has a companion Markdown description, a labeled color-swatch legend,
and a 16:9 or 9:16 diagram canvas.

| Review topic | Interactive page | Text description |
| --- | --- | --- |
| Architecture and data flows | [01 Architecture](../interactive/01_architecture.html) | [Markdown](../interactive/01_architecture.md) |
| Entity relationships | [02A Entities](../interactive/02a_entities.html) | [Markdown](../interactive/02a_entities.md) |
| Cross-component object calls | [02B Object calls](../interactive/02b_object_calls.html) | [Markdown](../interactive/02b_object_calls.md) |
| Launch, tournament, and schedule | [03A Organization pathways](../interactive/03a_organization_pathways.html) | [Markdown](../interactive/03a_organization_pathways.md) |
| Recording, clip, playback, cleanup | [03B Media pathways](../interactive/03b_media_pathways.html) | [Markdown](../interactive/03b_media_pathways.md) |

Open an HTML file in a browser for the interactive controls. The entity page's
steps traverse references rather than showing runtime execution. The static
figures remain the print-ready versions.

## Cocoon AI architecture diagram set

The workspace-installed [architecture-diagram-generator skill](https://github.com/Cocoon-AI/architecture-diagram-generator)
also renders the same five reviewed node and connection sets. Its dark HTML
pages include an export toolbar and summary cards. Each diagram has an on-page
legend with category names and color swatches. The HTML artwork and standalone
exports retain the requested 16:9 or 9:16 ratio.

| Review topic | HTML page | Standalone SVG | Print PDF |
| --- | --- | --- | --- |
| Architecture and data flows | [01 Architecture](../cocoon_generator/01_architecture.html) | [SVG](../cocoon_generator/01_architecture.svg) | [PDF](../cocoon_generator/01_architecture.pdf) |
| Entity relationships | [02A Entities](../cocoon_generator/02a_entities.html) | [SVG](../cocoon_generator/02a_entities.svg) | [PDF](../cocoon_generator/02a_entities.pdf) |
| Cross-component object calls | [02B Object calls](../cocoon_generator/02b_object_calls.html) | [SVG](../cocoon_generator/02b_object_calls.svg) | [PDF](../cocoon_generator/02b_object_calls.pdf) |
| Launch, tournament, and schedule | [03A Organization pathways](../cocoon_generator/03a_organization_pathways.html) | [SVG](../cocoon_generator/03a_organization_pathways.svg) | [PDF](../cocoon_generator/03a_organization_pathways.pdf) |
| Recording, clip, playback, cleanup | [03B Media pathways](../cocoon_generator/03b_media_pathways.html) | [SVG](../cocoon_generator/03b_media_pathways.svg) | [PDF](../cocoon_generator/03b_media_pathways.pdf) |

The HTML toolbar loads its export libraries from the pinned CDNs in the skill
template. The committed SVG, PDF, and PNG files can be opened without them.

## Visual explainer review

The workspace-installed [visual-explainer skill](https://github.com/nicobailon/visual-explainer)
produces a [single source-traced review page](../visual_explainer/codebase_review.html).
It presents five hand-drawn diagrams, detailed walkthroughs, and the logic
follow-up candidates. The architecture, entity, and object-call figures use
16:9 canvases; the organization and media pathways use 9:16 canvases. Each
figure carries its own labeled color-swatch legend. On a phone, swipe within a
diagram to see its full width.

The page links to the production Swift files and to [CALL_INDEX.md](../CALL_INDEX.md).
The object-call figure shows principal cross-component calls; the index lists
every production function declaration. Open the HTML file in a browser. It
has inline CSS, JavaScript, and SVG; the optional IBM Plex web font loads from
Google Fonts, with local sans-serif and monospace fallbacks.

## Diagram Creator review set

The workspace-installed [diagram-creator skill](https://github.com/ferdinandobons/diagram-creator-skill)
produces five separate, self-contained HTML pages. They use its nested, tree,
grid, and timeline layouts with pan, zoom, and fit controls. The diagram areas
are 16:9 for architecture, entities, and object calls; the two pathways use
9:16. Titles and explanations sit outside those areas. Each page has a labeled
color-swatch legend without visible hex codes.

| Review topic | Diagram Creator page |
| --- | --- |
| Architecture and data flows | [01 Architecture](../diagram_creator/diagram-01_architecture.html) |
| Persisted entities and external assets | [02A Entities](../diagram_creator/diagram-02a_entities.html) |
| Principal object calls | [02B Object calls](../diagram_creator/diagram-02b_object_calls.html) |
| Launch, tournament, and schedule | [03A Organization pathways](../diagram_creator/diagram-03a_organization_pathways.html) |
| Recording, clip, playback, and cleanup | [03B Media pathways](../diagram_creator/diagram-03b_media_pathways.html) |

The pages are source-traced summaries of the same production paths as the other
sets. The entity tree shows logical ownership; the note explains the direct
UUID fields that a tree cannot display as cross-links. The object-call grid
shows representative calls, while [CALL_INDEX.md](../CALL_INDEX.md) lists every
production function declaration. The pathway timelines show the main route;
their notes identify alternate branches and failure handling. Use the earlier
interactive set when inspecting individual handoffs step by step.

## Obsidian Canvas review set

These five editable [JSON Canvas](https://jsoncanvas.org/) files show the same
reviewed nodes and connections in Obsidian's `.canvas` format. Open this
repository as an Obsidian vault, or copy the files into a vault. The cards are
self-contained text; no image attachments are needed. Each board has a color
legend with category names, a short reading note, and 16:9 or 9:16 extents.
Custom card colors use the Diagram Creator accent palette. Obsidian controls
the surrounding workspace theme.

| Review topic | Obsidian Canvas |
| --- | --- |
| Architecture and data flows | [01 Architecture](../obsidian_canvas/01_architecture.canvas) |
| Persisted entities and external assets | [02A Entities](../obsidian_canvas/02a_entities.canvas) |
| Principal object calls | [02B Object calls](../obsidian_canvas/02b_object_calls.canvas) |
| Launch, tournament, and schedule | [03A Organization pathways](../obsidian_canvas/03a_organization_pathways.canvas) |
| Recording, clip, playback, and cleanup | [03B Media pathways](../obsidian_canvas/03b_media_pathways.canvas) |

Solid and dashed source links become Canvas connections. Because JSON Canvas
does not specify line styles, labels identify reference, optional, and
schema-only links. The object-call board shows principal cross-component
routes; [CALL_INDEX.md](../CALL_INDEX.md) remains the complete function list.

The [function declaration index](../CALL_INDEX.md) lists all production Swift
function declarations. It complements 02B, which stays at a readable level
and therefore does not draw an arrow for every private helper or framework
callback. Solid arrows show direct flow; dashed arrows show optional,
indirect, or reference links. The data model uses UUID fields rather than
SwiftData `@Relationship` properties. Each diagram has its own on-page color
legend with category labels and color swatches.

## Source trace

- Launch and dependency wiring: [`FencingVideoAnalysisApp`](../../FencingVideoAnalysis/App/AppEntry/FencingVideoAnalysisApp.swift), [`AppDependencies`](../../FencingVideoAnalysis/App/AppEntry/AppDependencies.swift), [`AppRootView`](../../FencingVideoAnalysis/App/AppEntry/AppRootView.swift).
- Screens and workflow orchestration: [`AppViewModel`](../../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift), [`TournamentNavigationView`](../../FencingVideoAnalysis/App/Navigation/TournamentNavigationView.swift), [`ScheduleImportView`](../../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift), [`BoutDetailView`](../../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift).
- Local entities and ordering: [`DomainModels`](../../FencingVideoAnalysis/Models/DomainModels/DomainModels.swift), [`LocalRepository`](../../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift).
- Schedule: [`ScheduleReviewViewModel`](../../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift), [`DocumentRecognitionService`](../../FencingVideoAnalysis/Services/DocumentRecognitionService.swift), [`ScheduleParsingService`](../../FencingVideoAnalysis/Services/ScheduleParsingService.swift), [`OnDeviceModelService`](../../FencingVideoAnalysis/Services/OnDeviceModelService.swift), [`ScheduleProposalValidator`](../../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift).
- Photos and clips: [`BoutImportCoordinator`](../../FencingVideoAnalysis/Services/BoutImportCoordinator.swift), [`PhotoLibraryService`](../../FencingVideoAnalysis/Services/PhotoLibraryService.swift), [`ClipWorkflow`](../../FencingVideoAnalysis/Services/ClipWorkflow.swift), [`ClipUploadQueue`](../../FencingVideoAnalysis/Services/ClipUploadQueue.swift), [`ClipDownloadCoordinator`](../../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift).
- Cloud and playback: [`CloudMetadataService`](../../FencingVideoAnalysis/Services/CloudMetadataService.swift), [`CloudAssetService`](../../FencingVideoAnalysis/Services/CloudAssetService.swift), [`BoutPlaybackQueue`](../../FencingVideoAnalysis/Services/BoutPlaybackQueue.swift), [`PlaybackState`](../../FencingVideoAnalysis/Services/PlaybackState.swift).

## Important behavior shown by the pathways

1. **Launch:** `AppDependencies.make` opens SwiftData and creates services. `AppViewModel.load` checks iCloud, reads local records, then refreshes CloudKit when available. The root view chooses setup or tournament navigation from the currently observed settings.
2. **Tournament and bouts:** The tournament form calls `saveTournament`. User-facing manual bout entry occurs in **Import Schedule**. Screenshot entry runs Vision recognition, deterministic parsing, optional on-device model assistance, and reconciliation; the parent edits drafts before `confirmSchedule` inserts bouts.
3. **Recordings:** PhotosPicker selections are prepared and reviewed first. Confirmation inserts `SourceRecording` links. A later PhotoKit/iCloud Photos link lets the same original be opened on another device. Originals are never written back or deleted by the app.
4. **Clips:** A source AV asset and trim range go to `ClipWorkflow`; AVFoundation exports a local clip. `ClipUploadQueue` synchronizes its metadata and saves a CKAsset. Local status records pending, available, or recovery states.
5. **Replay:** `BoutPlaybackQueue` orders individual review clips. `playableURL` uses a local export, managed cache, or CloudKit download. `MediaPlayerModel` controls AVPlayer, speed, seek, and scrub. Files are not concatenated.
6. **Cleanup:** Clip offloading keeps CloudKit data and removes safe local copies. Deletion removes a clip asset first, then local records and queued metadata; source originals stay in Photos.

## Logic review: follow-up candidates

These are source-based findings, not failures reproduced on a device. They are
ordered by likely user impact.

1. **Remote bouts can display the wrong media status.** [`BoutImportCoordinator.status`](../../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L201) reports `Edited` only if a clip has `localExportPath`. A clip received from CloudKit is created with `pendingDownload` and no local export in [`CloudMetadataMapper.apply`](../../FencingVideoAnalysis/Services/CloudMetadataService.swift#L291). Its bout can therefore show `Ready to Edit` (or `Not Imported` if no source link has arrived) despite having review clips. The clip count and Play Bout button use a separate check, so the labels can disagree.
2. **First launch can briefly present setup before CloudKit settings arrive.** [`AppViewModel.load`](../../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L139) sets `isLoaded` before awaiting `refreshCloud`; [`AppRootView`](../../FencingVideoAnalysis/App/AppEntry/AppRootView.swift#L43) chooses setup when the local settings are nil. On a newly installed second device, the screen may appear while the cloud fetch is still running. A UI test with delayed cloud delivery would establish whether this is visible and whether entering a name can race with the fetched record.
3. **Two modeled paths are not user-facing production flows.** `AppViewModel.addBout` is called by tests but not by a production view; manual bout creation uses Import Schedule and `confirmSchedule`. `ScheduleExtractionRun` is in the SwiftData schema but has no production insertion call. The diagrams mark this so a reviewer does not infer an audit trail or a separate Add Bout action. These are scope/maintenance observations, not confirmed defects.

## Regeneration and verification

Python packages are installed only in the ignored `.venv` directory. Graphviz
provides the `dot` renderer and `rsvg-convert` renders the fixed-ratio SVG to
PDF and PNG. From the repository root:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -r figures/tools/diagrams/requirements.txt
.venv/bin/python figures/tools/diagrams/generate_diagrams.py
.venv/bin/python figures/tools/diagrams/generate_call_index.py
.venv/bin/python figures/tools/diagrams/verify_diagrams.py
.venv/bin/python figures/tools/diagrams/generate_alternatives.py
.venv/bin/python figures/tools/diagrams/verify_alternatives.py
.venv/bin/python figures/tools/diagrams/generate_interactive.py
.venv/bin/python figures/tools/diagrams/verify_interactive.py
.venv/bin/python figures/tools/diagrams/generate_cocoon.py
.venv/bin/python figures/tools/diagrams/verify_cocoon.py
.venv/bin/python figures/tools/diagrams/verify_visual_explainer.py
.venv/bin/python figures/tools/diagrams/generate_diagram_creator.py
.venv/bin/python figures/tools/diagrams/verify_diagram_creator.py
.venv/bin/python figures/tools/diagrams/generate_obsidian_canvas.py
.venv/bin/python figures/tools/diagrams/verify_obsidian_canvas.py
.venv/bin/python figures/tools/diagrams/verify_legend_labels.py
```

To check fullscreen behavior in a local Chrome or Chromium browser, install
`.venv/bin/python -m pip install -r figures/tools/diagrams/requirements-browser.txt` and run
`.venv/bin/python figures/tools/diagrams/verify_interactive_browser.py`. This checks all five
pages at desktop, smaller desktop, and phone viewport sizes.

The Cocoon HTML pages can be checked in local Chrome with
`.venv/bin/python figures/tools/diagrams/verify_cocoon_browser.py`. The skill is installed in
the ignored `.agents/skills/architecture-diagram-generator` folder. Install it
from the linked repository before regenerating on another checkout. The
generator uses its `resources/template.html` and the reviewed `.gv` sources.

The visual explainer is a hand-drawn HTML artifact in
`figures/visual_explainer/`. Its browser verifier checks source links, the five
aspect ratios and legends, desktop and phone layouts, both color schemes,
navigation, node spacing, and console errors. The visual-explainer skill is
installed in the ignored `.agents/skills/visual-explainer` folder for future
visual explanations. The verifier uses only the ignored `.venv` environment.
The legend-label verifier checks visible text in every generated SVG and HTML
diagram. Color values remain in source styles and graphics attributes so the
swatches still render, but the legend labels show category names only.

The Diagram Creator generator reads its content from the reviewed production
analysis encoded in `figures/tools/diagrams/generate_diagram_creator.py`. The skill is in the
ignored `.agents/skills/diagram-creator` folder. Regeneration and browser
verification use only the ignored `.venv` environment; the output HTML pages
need no runtime libraries. Google Fonts are optional, with local font fallbacks.

The Canvas generator reads the five reviewed `.gv` sources, uses Graphviz to
place editable cards, and writes JSON Canvas without modifying an Obsidian
vault. Its verifier checks file structure, source counts, links, board sizes,
legends, and card overlaps. Regeneration uses the ignored `.venv` environment
and the installed `dot` executable.

The interactive generator needs the skill template at
`.agents/skills/architecture-diagram/assets/template.html`. The `.agents/`
folder is ignored by Git. Install it from the linked repository under
`skills/architecture-diagram` before regenerating on another checkout. After
reinstalling, run `.venv/bin/python figures/tools/diagrams/patch_architecture_skill.py` to
restore the fullscreen layering fix to the skill's template; the project
generator checks that the installed template includes this fix.

For the alternative set, install the official PlantUML jar locally at
`.venv/tools/plantuml.jar` before running the generator. The tested version is
`1.2026.8` from the [official release](https://github.com/plantuml/plantuml/releases/tag/v1.2026.8),
with SHA-256 `5e1ecfa8ecd32c90b03bbf3b1eb6f020943f98ab0fcf4032be31a0002ee2c462`.
The Python `plantuml` package is used to encode/check the generated source;
the local jar renders it so the project diagram text is never sent to a
public rendering server. Java, Graphviz `dot`, and `rsvg-convert` are required
on the machine; Python dependencies remain confined to `.venv`.

All five diagrams are saved as SVG, PDF, and PNG. The PNG previews are included for
quick inspection; the SVG and PDF files remain sharp when zoomed. The diagrams
were checked by parsing each SVG, rendering each PDF, inspecting the previews,
and comparing their edges with the source files above. See
[quality_report.md](../graphviz/quality_report.md). The existing `scripts/test-unit.sh` was
attempted, but this machine's active Command Line Tools do not include
`simctl`, so simulator tests could not start. No app source code was changed.
