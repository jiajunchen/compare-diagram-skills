# Overall codebase architecture

Trace SwiftUI actions through on-device services, SwiftData, Photos, and private CloudKit.

The source is the reviewed production-code analysis. Select a flow in the HTML to step through it. The Local only / iCloud available toggle reflects whether cloud-dependent steps can run.

## Components

- **Parent / fencer** (`user`): Parent / fencer; SwiftUI actions
- **AppRootView** (`root`): AppRootView; launch + scene activation
- **Tournament, schedule, bout,** (`views`): Tournament, schedule, bout,; timeline, player, settings views
- **AppViewModel** (`vm`): AppViewModel; UI state + workflow orchestration
- **ScheduleReviewViewModel** (`review`): ScheduleReviewViewModel; editable, unconfirmed drafts
- **Schedule source -> Vision recognition** (`schedule`): Schedule source -> Vision recognition; -> deterministic parser -> Foundation Model; -> proposal validator
- **Screenshot bytes + OCR/proposal** (`drafts`): Screenshot bytes + OCR/proposal; in memory until confirmation
- **LocalRepository / SwiftData** (`repo`): LocalRepository / SwiftData; settings, tournaments, bouts, source links, clips
- **BoutImportCoordinator** (`import`): BoutImportCoordinator; PhotoLibraryService
- **Photos / iCloud Photos** (`photos`): Photos / iCloud Photos; original videos; read on explicit import/open
- **ClipWorkflow -> VideoEditingService** (`editing`): ClipWorkflow -> VideoEditingService; AVFoundation export
- **App support files** (`files`): App support files; pending exports + downloaded clips
- **ClipUploadQueue** (`upload`): ClipUploadQueue; CloudMetadataService + CloudAssetService
- **Private CloudKit** (`cloud`): Private CloudKit; confirmed metadata + edited CKAssets
- **BoutPlaybackQueue + MediaPlayerModel** (`play`): BoutPlaybackQueue + MediaPlayerModel; ClipDownloadCoordinator + cache

## Flows

### Launch and local state

Root wiring, local load, and first screen.

1. **AppRootView → AppViewModel:** load / refresh.
2. **AppViewModel → LocalRepository / SwiftData:** fetch records.
3. **Parent / fencer → Tournament, schedule, bout,:** open app.
4. **Tournament, schedule, bout, → AppViewModel:** observed state.

### Schedule extraction

Drafts stay in memory until confirmation.

1. **Tournament, schedule, bout, → ScheduleReviewViewModel:** Import Schedule.
2. **ScheduleReviewViewModel → Schedule source -> Vision recognition:** extract.
3. **ScheduleReviewViewModel → Screenshot bytes + OCR/proposal:** temporary proposal.
4. **ScheduleReviewViewModel → AppViewModel:** confirm drafts.
5. **AppViewModel → LocalRepository / SwiftData:** insert bouts.

### Import recordings

Original videos remain in Photos.

1. **Tournament, schedule, bout, → AppViewModel:** import action.
2. **AppViewModel → BoutImportCoordinator:** prepare / confirm.
3. **BoutImportCoordinator → Photos / iCloud Photos:** read video + IDs.
4. **BoutImportCoordinator → LocalRepository / SwiftData:** source links.

### Create and upload clip

Export locally, then sync metadata and edited CKAsset.

1. **Tournament, schedule, bout, → AppViewModel:** trim selection.
2. **AppViewModel → ClipWorkflow -> VideoEditingService:** trim / export.
3. **ClipWorkflow -> VideoEditingService → App support files:** local clip.
4. **ClipWorkflow -> VideoEditingService → LocalRepository / SwiftData:** clip status.
5. **AppViewModel → ClipUploadQueue:** sync / retry.
6. **ClipUploadQueue → Private CloudKit:** metadata + CKAsset.
7. **ClipUploadQueue → LocalRepository / SwiftData:** sync state.

### Play and cache

Use a local export or managed cache; download if needed.

1. **Tournament, schedule, bout, → BoutPlaybackQueue + MediaPlayerModel:** player controls.
2. **AppViewModel → BoutPlaybackQueue + MediaPlayerModel:** clip URL / unload.
3. **BoutPlaybackQueue + MediaPlayerModel → App support files:** cache / replay.
4. **BoutPlaybackQueue + MediaPlayerModel → Private CloudKit:** download clip.

## Scope notes

- The entity page shows UUID references; its steps are relationship traversal, not method calls.
- The object-call page shows principal production calls. See [CALL_INDEX.md](../CALL_INDEX.md) for all function declarations.
- Photos originals are external. CloudKit stores confirmed metadata and edited review clips.
- Schema-only ScheduleExtractionRun has no production insertion call.
