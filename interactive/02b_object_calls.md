# Object call map

Explore production cross-component calls. The function index documents private helpers and framework callbacks.

The source is the reviewed production-code analysis. Select a flow in the HTML to step through it. The Local only / iCloud available toggle reflects whether cloud-dependent steps can run.

## Components

- **FencingVideoAnalysisApp** (`entry`): FencingVideoAnalysisApp; AppDependencies.make -> AppRootView
- **SwiftUI views** (`ui`): SwiftUI views; forms, schedule, bout, timeline, player, settings
- **AppViewModel** (`vm`): AppViewModel; load / refreshCloud; saveTournament / confirmSchedule / addBout*; prepare/confirmRecordings / createClip; playableURL / delete / offload
- **ScheduleReviewViewModel** (`review`): ScheduleReviewViewModel; extract / addDraft / removeDraft / moveDraft
- **Schedule services** (`schedule`): Schedule services; recognize -> parse -> propose -> reconcile
- **BoutImportCoordinator** (`bout`): BoutImportCoordinator; prepareSelections / confirm / linkPendingCloudPhotos; sourceAsset / move / remove
- **PhotoLibraryService** (`photos`): PhotoLibraryService; importSelections / cloudIdentifiers / videoAsset
- **ClipWorkflow** (`clip`): ClipWorkflow; createClip / retry / delete / clips; unloadUploadedClips / clearLocalClipCopies
- **VideoEditingService.export** (`editor`): VideoEditingService.export
- **LocalRepository** (`repo`): LocalRepository; insert / fetch / delete / saveChanges; tournaments / bouts / sourceRecordings / reviewClips
- **ClipUploadQueue** (`queue`): ClipUploadQueue; resumePending / upload / retry / deleteCloudCopyIfNeeded
- **CloudMetadataService** (`cloud`): CloudMetadataService; synchronize / synchronizeDeletions / queueDeletion; mapper pendingRecords / apply
- **CloudAssetService** (`assets`): CloudAssetService; saveExportedClip / downloadClip / deleteClip
- **Private CloudKit + Photos** (`ck`): Private CloudKit + Photos; framework boundaries
- **ClipDownloadCoordinator** (`download`): ClipDownloadCoordinator; resolve / clearCache / removeCachedCopies
- **BoutPlaybackQueue + MediaPlayerModel** (`player`): BoutPlaybackQueue + MediaPlayerModel; next / previous / finish / play / seek / scrub

## Flows

### Launch

App composition, UI, and local read.

1. **FencingVideoAnalysisApp → SwiftUI views:** AppRootView.
2. **SwiftUI views → AppViewModel:** load.
3. **AppViewModel → LocalRepository:** fetch.

### Schedule confirmation

Recognize and review before any bout insert.

1. **SwiftUI views → ScheduleReviewViewModel:** extract.
2. **ScheduleReviewViewModel → Schedule services:** recognize / parse / reconcile.
3. **ScheduleReviewViewModel → AppViewModel:** confirmed drafts.
4. **AppViewModel → LocalRepository:** insert / saveChanges.

### Recording and clip

Prepare Photos links, then export a trimmed clip.

1. **SwiftUI views → AppViewModel:** prepare / confirm.
2. **AppViewModel → BoutImportCoordinator:** import coordinator.
3. **BoutImportCoordinator → PhotoLibraryService:** videoAsset / IDs.
4. **BoutImportCoordinator → LocalRepository:** source links.
5. **AppViewModel → ClipWorkflow:** createClip.
6. **ClipWorkflow → VideoEditingService.export:** export.
7. **ClipWorkflow → LocalRepository:** clip status.

### Cloud synchronization

Confirmed metadata and edited clip asset only.

1. **AppViewModel → ClipUploadQueue:** upload / retry.
2. **ClipUploadQueue → CloudMetadataService:** synchronize.
3. **CloudMetadataService → LocalRepository:** apply records.
4. **ClipUploadQueue → CloudAssetService:** saveExportedClip.
5. **CloudAssetService → Private CloudKit + Photos:** CKAsset.

### Playback download

Resolve clip URL for the player queue.

1. **SwiftUI views → BoutPlaybackQueue + MediaPlayerModel:** playback controls.
2. **AppViewModel → ClipDownloadCoordinator:** playableURL.
3. **ClipDownloadCoordinator → CloudAssetService:** downloadClip.
4. **CloudAssetService → Private CloudKit + Photos:** private asset.

## Scope notes

- The entity page shows UUID references; its steps are relationship traversal, not method calls.
- The object-call page shows principal production calls. See [CALL_INDEX.md](../CALL_INDEX.md) for all function declarations.
- Photos originals are external. CloudKit stores confirmed metadata and edited review clips.
- Schema-only ScheduleExtractionRun has no production insertion call.
