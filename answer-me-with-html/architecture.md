---
template: doc
theme: blueprint
mode: light
lang: en
title: Inside Fencing Video Analysis
subtitle: A source-grounded guide to the screens, functions, data, and recovery paths
source: Swift source at 8a8c101
reviewed: 2026-10-03
---
The app connects one fencer, tournaments, bouts, source recordings, and edited review clips. SwiftUI handles interaction; local workflows save progress; Apple frameworks handle recognition, media, and cloud storage.

Read chapters A–G for the operation paths. Chapter H maps every Swift file and named function declaration. Use the page contents to jump between chapters.

## A Structure and storage boundaries

### The architecture in one picture
```flow
SwiftUI screens -> AppViewModel: organization and media actions
SwiftUI screens -> Feature models: extraction and playback
AppViewModel -> Workflow coordinators: import, trim, upload, download
AppViewModel -> LocalRepository: records and ordering
Workflow coordinators -> Apple services: Photos, AVFoundation, CloudKit
Feature models -> Apple services: Vision, Foundation Models, AVPlayer
LocalRepository -> SwiftData: save local state
LocalRepository -> CloudKit metadata: schedule explicit sync
```
The arrows group dependencies, not a single ordered execution. Feature models are ScheduleReviewViewModel and MediaPlayerModel.

AppViewModel exposes services used to construct ScheduleReviewViewModel; extraction runs in that feature model. Workflow coordinators are BoutImportCoordinator, ClipWorkflow, ClipUploadQueue, and ClipDownloadCoordinator.

### Repository layout
```tree list
FencingVideoAnalysis/
  App/
    AppEntry/ | app bootstrap, dependency wiring, shared AppViewModel
    Navigation/ | adaptive tournament navigation
  Features/
    FirstRunSetup/ | save the single fencer name
    Tournaments/ | create, edit, select, and delete tournaments
    ScheduleImport/ | screenshots, extraction, review, confirmation
    Bouts/ | import, source trimming, clip replay, shared player controls
    Settings/ | fencer name, Photos permission, local clip storage
  Models/
    DomainModels/ | six SwiftData entities and SyncState
    LocalModels/ | repository, schema, ordering, local deletion
  Services/ | framework adapters, coordinators, parsers, sync, cache
FencingVideoAnalysisTests/ | unit, integration, and physical-device probes
FencingVideoAnalysisUITests/ | end-to-end UI journeys
scripts/ | simulator test entry points and schedule evaluation
figures/ | architecture artifacts and their generators
```
The current executable tree has 35 Swift files and targets iOS 26.0. The folder list in ARCHITECTURE.md also contains proposed feature folders; use this map for the implemented layout.

### Ownership and relationships
```flow
AppSettings -> Tournament: shared fencer context
Tournament -> Bout: tournamentID
Bout -> SourceRecording: boutID
SourceRecording -> ReviewClip: sourceRecordingID
Bout -> ReviewClip: boutID
```
AppSettings is a single global setting, not a foreign-key parent of Tournament. The other links use UUID fields, not SwiftData relationship properties.

| Entity | Purpose and key fields | Persistence |
| --- | --- | --- |
| AppSettings | Stable cloud ID, fencerName, timestamps, syncState | Local and private CloudKit |
| Tournament | Name, venue, date, timezone, import status | Local and private CloudKit |
| Bout | Tournament ID, opponent, sequence number, status; optional context fields | Confirmed records sync |
| SourceRecording | Bout ID, capture time, duration, filename, import batch, Photos IDs | Portable metadata syncs |
| ReviewClip | Source ID, bout ID, start/end, duration, favorite, asset reference, media state | Metadata and edited movie sync |
| ScheduleExtractionRun | Diagnostic schema for extraction status and warnings | Defined locally; current extraction UI does not create these records |

### Where the bytes live
| Data | Location | Boundary |
| --- | --- | --- |
| Original videos | Photos; optional Apple-managed iCloud Photos storage | The app never uploads originals to its CloudKit container |
| Source link | Local Photos ID plus portable cloudPhotoAssetID | Only the portable ID crosses devices |
| Legacy source copies | Application Support/SourceRecordings | Local only; successful Photos-backed open can remove the old copy |
| Exported review clips | Application Support/PendingClips | Durable file while upload is pending; may remain after upload |
| Downloaded review clips | Application Support/DownloadedClips | Managed cache with index.json; default limit 2,000,000,000 bytes |
| Schedule screenshots, OCR, drafts | Feature memory during review | No cloud serialization |
| App metadata | SwiftData plus private CloudKit | The repository disables automatic SwiftData CloudKit integration |
| Sync recovery state | CloudMetadataSyncState.json and CloudRecordSystemFields.json | Engine state and record versions stay on the device |

`SwiftDataRepository.makeContainer()` selects `cloudKitDatabase: .none`. Explicit CloudKit services control the cloud boundary.

## B Launch, navigation, and organization

### Launch and foreground refresh
```sequence num
App -> Dependencies: make()
Dependencies -> Services: build repository and adapters
App -> AppViewModel: AppRootView creates model
App -> AppViewModel: .task → load()
AppViewModel -> Services: accountStatus(); local reads
AppViewModel -> Services: refreshCloud() if available
AppViewModel --> App: setup or tournament navigation
```
`FencingVideoAnalysisApp` stores bootstrap as a Result. A bootstrap failure shows local-data failure. A later load failure offers `load()` again.

`load()` migrates an older settings ID to `AppSettings.cloudID`. It reads local data before cloud refresh, so unavailable iCloud does not block local organization.

After loading, `load()` calls `ClipWorkflow.removeAbandonedFiles()` for old, unreferenced source and export files. The cutoff is 24 hours. Test stores disable this cleanup.

| Trigger | Function path | Result or guard |
| --- | --- | --- |
| App becomes active | AppRootView.onChange(scenePhase) → AppViewModel.refreshCloud() | Runs only after local load |
| Pull tournament or bout list | .refreshable → refreshCloud() | Discovers new remote records and resumes pending uploads |
| Enter fencer; Continue | FirstRunSetupView button → saveFencerName() → insert or update AppSettings → saveChanges() | Rejects an empty trimmed name |
| Fencer settings; Save | FencerSettingsView button → saveFencerName() | Same validation; marks settings pending |
| New Tournament | TournamentNavigationView state → TournamentFormView | Opens an unsaved form |
| Save tournament | TournamentFormView button → saveTournament() → insert/update → saveChanges() → tournaments() | Rejects an empty name; selects the saved tournament |
| Select tournament | List selection binding → selectTournament(id) → repository.bouts(in:) | Loads that tournament's ordered bouts |
| Edit tournament | TournamentDetailView state → TournamentFormView(existing:) → saveTournament(existing:) | Updates timestamps and pending state |
| Open bout | TournamentDetailView button → selectedBout + showingBoutDetail | Presents BoutDetailView; .task calls refreshRecordings() |
| Save bout edits | BoutDetailView.save() → updateConfirmedBout() → saveChanges() | Requires opponent, positive number, and no number collision |
| Cancel form | SwiftUI dismiss() | Discards unsaved form state |

`updateConfirmedBout()` restores previous values if persistence fails. The public `addBout()` helper exists, but the current manual-entry screen uses schedule drafts and `confirmSchedule()`.

### How local changes reach the cloud
`saveChanges()` calls `ModelContext.save()`, then `didSave`. On a physical device with live metadata, dependency wiring connects `didSave` to `LiveCloudMetadataService.scheduleSync()`.

This is asynchronous cloud scheduling. A successful local save does not mean the other device has already received the change.

### Screen presentation
NavigationSplitView adapts the tournament list and detail. Bout import and schedule review use sheets. PlaybackPresentation uses a sheet on iPhone and a 90%-sized overlay within a full-screen cover on iPad.

## C Schedule screenshots to confirmed bouts

### Extraction path
```sequence num
Screen -> ReviewModel: loadScreenshots() → extract()
ReviewModel -> Extractors: recognize() for each image
ReviewModel -> Extractors: parse(); propose()
ReviewModel -> Validator: reconcile()
Validator --> ReviewModel: drafts and warnings
ReviewModel --> Screen: state = ready
Screen -> Persistence: confirm() → confirmSchedule()
Persistence --> Screen: saved bouts or validation error
```
The screenshot picker allows up to 10 images. `loadScreenshots()` reads Data through PhotosPickerItem.loadTransferable, then `LiveScheduleSourceService.screenshots()` creates the source.

Diagram lanes group the screen, ReviewModel, extractor services, validator, and persistence. The following table names each concrete implementation.

### What each stage actually does
| Stage | Functions | Behavior |
| --- | --- | --- |
| Recognition | LiveDocumentRecognitionService.recognize() | Validates image data and orientation; attempts RecognizeDocumentsRequest for tables |
| Text recognition | RecognizeTextRequest.perform() | Runs accurate OCR as well; falls back to document text lines if needed |
| Quality checks | RecognizedScheduleDocument.addingQualityWarnings() | Adds recognition warnings; no readable transcript throws |
| Deterministic parsing | DeterministicScheduleParser.parse(), mapping(), normalizedName(), numericValue(), context() | Maps table columns, matches the saved fencer on either side, extracts the opponent and full bout-order position |
| Model assistance | LiveOnDeviceModelService.propose(), promptData() | Uses SystemLanguageModel when available; guided generation returns typed candidates |
| Evidence validation | ScheduleProposalValidator.reconcile(), mergeString(), mergeInt(), trace(), sourceRow() | Requires source evidence; rejects unsupported rows and values; retains deterministic findings on conflicts |
| Editable review | ScheduleReviewViewModel.extract() → EditableBoutDraft.init | Exposes opponent and bout number; filters and deduplicates visible warnings |
| Confirmation | AppViewModel.confirmSchedule() | Validates the whole draft set before inserting bouts |

The current deterministic parser processes recognized tables. Text recognition does not itself guarantee a supported table layout. Unsupported layouts need review or manual entry.

The model receives bounded OCR/table text. `promptData()` limits the final input to 18,000 characters. Model unavailability or generation failure retains deterministic results.

### Review actions and branches
| Action | Triggered function or state | Effect |
| --- | --- | --- |
| Manual Entry | startManual() → scheduleSourceService.manual() → extract() | Review state becomes ready without OCR or model calls |
| Add bout draft | ScheduleReviewViewModel.addDraft() | Uses the next draft number; still unconfirmed |
| Edit opponent or number | SwiftUI bindings into review.drafts | Changes memory only |
| Remove draft | removeDraft(at:) | Removes one proposed bout |
| Reorder drafts | moveDraft(from:to:) or moveDrafts(from:to:) | Changes draft display order; saved bout order uses the explicit number |
| Enlarge screenshot | enlargedImageIndex → ScheduleImageViewer | Inspects selected screenshot without changing extraction |
| Zoom or pan | magnify(), pan(), setZoom(), resetZoom(), bounded() | Changes viewer scale and offset |
| Retry extraction | ScheduleImportView.extract(source) | Re-runs recognition, parsing, model assistance, and validation |
| New Source | clear source and picker state → review.reset() | Discards the current proposal in memory |
| Discard Schedule | confirmation dialog → dismiss() | The app writes no confirmed records |
| Confirm Schedule | ScheduleImportView.confirm() → AppViewModel.confirmSchedule() | Saves normalized confirmed bouts |

### Confirmation contract
`confirmSchedule()` requires at least one draft, a known tournament, nonempty opponents, and positive unique bout numbers. It rejects conflicts with an existing number and different opponent.

The app skips an identical existing number/opponent pair. New bouts use phase `unknown`; imported pool, strip, and schedule-time context are not persisted by this screen.

The app sets `scheduleImportStatus = confirmed` and clears `scheduleSourceURL` on the tournament. Save failure removes inserted bouts and restores the tournament's prior fields.

## D Import and reopen source recordings

### Import starts in a known bout
```sequence num
Review screen -> AppViewModel: prepareRecordings()
AppViewModel -> Import coordinator: prepareSelections()
Import coordinator -> Photos: importSelections()
Photos --> Review screen: batch and per-item failures
Review screen -> AppViewModel: confirmRecordings()
AppViewModel -> Import coordinator: confirm(); linkPendingCloudPhotos()
Import coordinator -> Photos: cloudIdentifiers()
AppViewModel --> Review screen: onSaved(result); dismiss
```
There is no automatic bout matching. The selected bout provides the destination. Duplicate detection checks known device-local asset IDs across that tournament and within the batch.

`PhotoSelection.init(item:)` supplies a metadata loader for normal picker selections. New imports retain Photos identifiers and metadata without creating a full-size working copy. The service also supports a file-copy path for selections without that loader.

`LivePhotoLibraryService.importSelections()` rejects missing Photos identifiers and invalid durations. It reports individual failures without discarding usable selections.

### Confirmation, cancel, and repair
| Trigger | Function path | State change |
| --- | --- | --- |
| Add to Bout | RecordingImportReviewView.confirm() → confirmRecordings() → BoutImportCoordinator.confirm() | Creates one SourceRecording per usable item with a shared importBatchID |
| Persistence failure | BoutImportCoordinator.confirm() catch | Removes inserted records and attempts working-file cleanup |
| Cancel before confirmation | cancel() → discardRecordings() → discard() → removeWorkingFiles() | Drops prepared working copies |
| Cancel during preparation | cancel() → loadTask.cancel(); prepare() checks cancelRequested | Cleans completed results before dismissal |
| Select another batch | prepare() → discardRecordings(previousBatch) | Removes the prior unsaved batch |
| Link source across devices | linkPendingCloudPhotos() → cloudIdentifiers(for:) → saveChanges() | Saves cloudPhotoAssetID; marks source metadata pending |
| Repair older imports | localIdentifierForExistingRecording() | Matches filename and duration; uses capture time to resolve ambiguity |
| Allow Photos Access | FencerSettingsView → AppViewModel.connectPhotos() | Requests permission, links pending sources, then refreshes cloud |
| Permission denied | connectPhotos() → needsDeviceSettings | UI offers UIApplication.openSettingsURLString |

A cloud-link failure can leave the recording saved locally. `confirmRecordings()` reports that linking failed instead of undoing a successful import.

### Open a source for playback or trimming
```flow
Select source -> AppViewModel.sourceAsset: SourceTimelineView.select
AppViewModel.sourceAsset -> BoutImportCoordinator.sourceAsset: resolve recording
BoutImportCoordinator.sourceAsset -> PhotoLibrary.videoAsset: local or cloud Photos ID exists
PhotoLibrary.videoAsset -> PhotoKit AVAsset: permission and identifier mapping
BoutImportCoordinator.sourceAsset -> Legacy AVURLAsset: Photos fails and local copy exists
PhotoKit AVAsset -> MediaPlayerModel.open: playback asset
Legacy AVURLAsset -> MediaPlayerModel.open: fallback asset
```
`videoAsset()` first tries the local Photos ID, then maps the portable cloud ID to this device's ID. `PHImageManager.requestAVAsset` allows network access, so Photos may download the original.

After a successful Photos-backed open, `sourceAsset()` attempts to remove the older app working file. If neither Photos nor a legacy file is usable, the screen shows an error.

`localSourceURL()` → `localCopy()` → `copyFromICloudPhotos()` also exists for callers needing a local URL. The current SourceTimelineView uses `sourceAsset()`, not this copy path.

### Move and remove
`BoutDetailView.move()` → `AppViewModel.moveRecording()` → `BoutImportCoordinator.move()` changes boutID. It requires a destination in the same tournament and no saved review clips for that source.

`BoutDetailView.remove()` → `AppViewModel.removeRecording()` → `BoutImportCoordinator.remove()` deletes the link and managed working file. It blocks sources with clips, then queues a cloud source deletion.

`LocalRepository.sourceRecordings(in:)` orders by capture time, then UUID. Original Photos assets remain unchanged.

## E Trim, export, upload, and retry

### Save Clip pathway
```flow
Save Clip -> AppViewModel.createClip: SourceTimelineView.saveClip
AppViewModel.createClip -> BoutImportCoordinator.sourceAsset: obtain source
BoutImportCoordinator.sourceAsset -> ClipWorkflow.createClip: asset and trim range
ClipWorkflow.createClip -> Save exporting record: validate range
Save exporting record -> VideoEditingService.export: AVAssetExportSession
VideoEditingService.export -> Save pendingUpload: exported MOV and duration
Save pendingUpload -> ClipUploadQueue.upload: asynchronous Task
ClipUploadQueue.upload -> Metadata.synchronize: create cloud record
Metadata.synchronize -> Assets.saveExportedClip: attach CKAsset
Assets.saveExportedClip -> Save available: cloudAssetRecordName
```
Setting a start or end marker copies the current playhead into view state. Range sliders edit those values directly. The Save button disables obvious invalid ranges.

`TrimRange.validate()` also checks finite values, nonnegative start, increasing end, and source duration. Both ClipWorkflow and the export service validate the range.

`LiveVideoEditingService.export()` uses the passthrough preset and a CMTimeRange. It writes a separate UUID-named MOV into PendingClips and reports progress every 100 ms.

### Media state transitions
```flow
exporting -> pendingUpload: export succeeds
exporting -> exportFailed: export throws
exportFailed -> pendingUpload: retry export succeeds
pendingUpload -> uploading: upload starts
uploading -> available: asset save succeeds
uploading -> pendingUpload: temporary cloud error
uploading -> needsAttention: other failure
needsAttention -> pendingUpload: retry upload
```
`ReviewClip.mediaSyncStatus` and `localExportPath` form the durable upload queue. `ClipUploadQueue.resumePending()` retries `pendingUpload` and `uploading` records after cloud refresh.

### Failure and retry actions
| Trigger or condition | Function path | Result |
| --- | --- | --- |
| Cancel Export | exportTask.cancel() → cancellation handler → ExportCancellation.cancel() → session.cancelExport() | Export service removes partial output; initial create records exportFailed on error |
| Retry failed export | SourceTimelineView.retry() → AppViewModel.retryClip() → ClipWorkflow.retry() | Reuses the clip ID; exports again, then schedules upload |
| Retry Upload | AppViewModel.retryUpload() → ClipUploadQueue.retry() → upload() | Requires an existing export file |
| Missing export during upload | ClipUploadQueue.upload() → setStatus() | Marks needsAttention |
| Account/network/service failure | isTemporaryCloudFailure() | Returns clip to pendingUpload |
| Repeated upload request | inFlight ID set | Prevents a duplicate in-flight upload |
| Delete during upload | deleteCloudCopyIfNeeded() waits for upload completion | The deleting set prevents late callbacks from reviving the clip |

The workflow saves the initial clip record before rendering starts. If the app terminates during export, that record can remain `exporting`; automatic upload resumption does not re-export it.

### Actual cloud asset implementation
Metadata uses CKSyncEngine. The asset service separately fetches the existing ReviewClip record, adds `videoAsset = CKAsset(fileURL:)`, and calls `CKDatabase.save()`.

This direct asset save is the implemented path. Do not infer that CKSyncEngine itself uploads the movie from the broader architecture description.

## F Playback, seeking, favorites, and local storage

### Open and replay clips
```sequence num
Player view -> AppViewModel: load() → reviewClips()
AppViewModel --> Player view: ordered queue
Player view -> AppViewModel: openCurrent() → playableURL()
AppViewModel -> Downloads: resolve() if no local export
Downloads -> Cache or CloudKit: cachedURL() or downloadClip()
Cache or CloudKit --> Downloads: local file; store and validate
Downloads --> AppViewModel: playable URL
AppViewModel --> Player view: open(); setSpeed()
```
`LocalRepository.reviewClips(in:)` orders by source capture time, then clip start, then UUID. Missing source metadata sorts last. A bout is a logical queue of independent files.

### Playback actions
| Action | Function path | Behavior |
| --- | --- | --- |
| Play or Pause | MediaPlayerModel.play() / pause() | Updates AVPlayer and PlaybackState |
| Select a clip row | BoutPlaybackQueue.select() → openCurrent(autoplay: false) | Resolves that clip without starting playback |
| Previous or Next | movePrevious()/moveNext() → queue.previous()/next() → openCurrent(autoplay: true) | Advances manually and starts playback |
| Clip finishes | AVPlayerItem.didPlayToEndTimeNotification → finishCurrentClip() → queue.didFinishCurrentClip() | Advances only in continuous mode; otherwise pauses |
| Change playback mode | Binding to queue.mode | Chooses continuous or focused single-clip mode |
| Change speed | PlaybackSpeedControl → MediaPlayerModel.setSpeed() → PlaybackState.setSpeed() | UI offers 0.5×, 1×, 2×; active AVPlayer rate updates immediately |
| Leave player | .onDisappear → MediaPlayerModel.stop() | Cancels scrub work, pauses, releases item, resets state |
| Play clip from editor | SourceTimelineView.play() → playableURL() → LocalClipPlayerView | Uses the same playback model and controls |
| Retry download or open | play(clip) or openCurrent(autoplay: false) | Repeats the resolution path |

PlaybackState supports extra 0.25× and 1.5× values internally. The visible speed buttons expose only the three values above.

### Dragging the timeline
```sequence num
Slider -> MediaPlayerModel: scrub(to:)
MediaPlayerModel -> PlaybackState: seek(to:) clamps time
MediaPlayerModel -> ScrubCoordinator: drag(to:)
ScrubCoordinator -> AVPlayerSeekTarget: seek(to:, tolerance: 0.15)
Slider -> MediaPlayerModel: finishScrub() on release
MediaPlayerModel -> ScrubCoordinator: finish(at:)
ScrubCoordinator -> AVPlayerSeekTarget: seek(to:, tolerance: 0)
```
`VisualScrubCoordinator.startWorkerIfNeeded()` allows one seek at a time. New drag positions replace obsolete pending positions. Final release requests an exact seek.

`MediaPlayerModel.playerTimeDidChange()` updates the playhead every 0.1 seconds, except during a drag. Generation checks prevent a stale completion from changing a newly opened player's scrub state.

### Download and cache decisions
`playableURL()` uses an existing local export first. `ClipDownloadCoordinator.resolve()` then tries the managed cache before checking iCloud and downloading.

`ManagedClipCache.store()` checks the 2 GB limit and keeps a 10 MB free-space margin. It evicts least-recently-used entries, copies through a partial file, and updates index.json.

The coordinator verifies a video track after download. Invalid video removes the cache entry. Missing asset data produces `waitingForAsset`; other errors distinguish account, network, missing record, storage, and format failures.

### Favorites and offloading
| Action | Function path | Guard or result |
| --- | --- | --- |
| Star any clip | FavoriteStarButton → toggleClipFavorite() → saveChanges() → refreshFavoriteBoutIDs() → Task refreshCloud() | Marks favoriteSyncState pending; no new video export |
| Display bout star | isBoutFavorite() reads favoriteBoutIDs | Derived from any starred clip; old Bout.isFavorite is compatibility data |
| Unload Bout Clips | BoutPlayerView.unloadClips() → playback.stop() → unloadBoutClips() → ClipWorkflow.unloadUploadedClips() | Requires all local exports in that bout to have an available cloud asset |
| Play an unloaded clip | openCurrent() → playableURL() | Downloads the cloud asset again |
| Clear Local Clip Copies | FencerSettingsView.clearLocalCopies() → clearLocalClipCopies() | Removes eligible uploaded exports across bouts and clears download cache |
| Inspect storage | refreshLocalStorage() → localUploadedClipBytes() → localExportBytes() | Counts actual managed export files; downloadedClipCacheBytes reads the cache |

Bout offload checks all local exports before removing any; one pending upload blocks that operation. Global cleanup instead skips pending uploads and reports the skipped count.

Global cleanup can remove unreferenced exports older than two hours when no active unlinked export exists. Startup cleanup uses the separate 24-hour cutoff.

Both paths keep CloudKit records and assets. Managed-path checks prevent deletion of files outside the export workspace.

## G Synchronization, remote changes, and deletion

### RefreshCloud is the recovery hub
```sequence num
AppViewModel -> Metadata: synchronize(discoverNewRecords: true)
Metadata -> CloudKit: sendChanges(); fetchChanges()
Metadata -> CloudKit: reconcile known records and zone
AppViewModel -> Media services: linkPendingCloudPhotos()
AppViewModel -> Metadata: sync again if links changed
AppViewModel -> Media services: resumePending()
AppViewModel -> LocalRepository: reload lists and favorite IDs
```
Cloud unavailability sets a visible error and leaves local changes pending. Metadata failure stops the refresh before upload resumption. Successful refresh clears the shared error message.

### Metadata functions and event paths
| Trigger | Function path | Purpose |
| --- | --- | --- |
| Local save | SwiftDataRepository.saveChanges() → didSave → scheduleSync() | Coalesces work with a 300 ms delay |
| Sync pass | synchronize() → CloudMetadataMapper.pendingRecords() | Builds only eligible portable records |
| Engine asks for a batch | nextRecordZoneChangeBatch() → CloudMetadataCKRecord.make() | Combines payload with remembered system fields |
| Engine state changes | handleEvent(.stateUpdate) | Writes serialized tokens and pending engine work |
| Records arrive | handleEvent(.fetchedRecordZoneChanges) → decode() → CloudMetadataMapper.apply() | Applies remote data to SwiftData |
| Saves succeed | handleEvent(.sentRecordZoneChanges) → markSynchronized() | Clears eligible pending metadata flags |
| Change-tag conflict | handleEvent() → systemFields.remember(server) | Applies a newer remote value or requeues local data with current server fields |
| Missing zone or record | handleEvent() | Recreates zone or clears stale system fields and requeues save |
| Explicit discovery | reconcileEntireZone() | Walks metadata-only pages from the start; repairs missed deliveries |
| Known-record repair | reconcileKnownRecords() | Fetches known IDs in batches of 100; throttles to one minute |
| Remote deletion | removeLocalRecord() → CloudLocalDeletion.remove() → deleteLocalRecord() | Removes local descendants and managed media |

`reconcileEntireZone()` requests payload and updatedAt fields, not video assets. It reconstructs remote names and removes stale local records while protecting pending local saves and deletes.

The mapper excludes local paths, device-local Photos IDs, screenshots, OCR, and drafts. Favorite updates reuse the existing ReviewClip record and preserve its video asset through remembered record fields.

### Metadata-before-media on the receiving device
A new remote ReviewClip can exist before its movie arrives. Mapper application creates it with `pendingDownload`. Opening it may yield `waitingForAsset`.

After a successful download, `AppViewModel.playableURL()` changes these states to `available`. The user can retry an incomplete download later.

### Explicit deletion pathways
| Action | Ordered function path | Protection and failure behavior |
| --- | --- | --- |
| Delete clip | SourceTimelineView.delete() → AppViewModel.deleteClip() → uploadQueue.deleteCloudCopyIfNeeded() → ClipWorkflow.delete() → queueDeletion(.clip) → removeCachedCopies() → synchronizeDeletion() | Cloud asset deletion runs before local record removal when a cloud asset reference exists |
| Remove recording | BoutDetailView.remove() → removeRecording() → BoutImportCoordinator.remove() → queueDeletion(.source) → synchronizeDeletion() | Requires no clips; removes only app-owned working copies |
| Delete empty bout | BoutDetailView.delete() → deleteConfirmedBout() → repository.deleteBout() → queueDeletion(.bout) | Blocks if sources or clips remain |
| Delete tournament | deleteTournament() → deleteClip() for each clip → boutImport.remove() for each source → repository.deleteTournament() | Deletes edited cloud assets before parent metadata; then queues source, bout, and tournament deletions |
| Receive parent deletion | CloudLocalDeletion.deleteLocalRecord() recursively handles descendants | Clears local clip cache, managed exports, source copies, and records |

`synchronizeDeletion()` calls `synchronizeDeletions()`. If deletes remain pending or sync fails, it reports that cloud deletion is waiting.

Deleting a cloud-backed clip can fail before local deletion if the cloud is unavailable. Tournament deletion consists of ordered steps, not one transaction; a failure can leave a partially completed deletion.

A pending delete takes precedence over fetched cloud records. This prevents a refresh from immediately restoring a record awaiting server deletion.

## H Source map, tests, and implementation limits

### How to verify this guide
This is a static source walkthrough at revision `8a8c101`, not a recorded runtime trace. Arrows with Task, callbacks, or notifications describe asynchronous triggers.

The linked source files provide exact declarations and call sites. File links need this repository beside the HTML; the explanation and diagrams work offline by themselves.

### Existing automated coverage
| Concern | Test files to inspect |
| --- | --- |
| Bootstrap and organization | AppDependenciesTests.swift, AppViewModelTests.swift, LocalRepositoryTests.swift |
| Schedule pipeline | ScheduleSourceServiceTests.swift, DocumentRecognitionServiceTests.swift, ScheduleParsingServiceTests.swift, OnDeviceModelServiceTests.swift, ScheduleProposalValidatorTests.swift |
| Review and confirmation | ScheduleReviewViewModelTests.swift, ScheduleConfirmationTests.swift, ScheduleEvaluationTests.swift |
| Photos import and source linking | PhotoLibraryServiceTests.swift, BoutImportCoordinatorTests.swift |
| Editing and upload | VideoEditingServiceTests.swift, ClipWorkflowTests.swift, ClipUploadQueueTests.swift |
| Playback and seeking | PlaybackStateTests.swift, VisualScrubCoordinatorTests.swift, BoutPlaybackQueueTests.swift |
| Cloud and downloads | CloudMetadataServiceTests.swift, CloudAssetServiceTests.swift, ClipDownloadCoordinatorTests.swift |
| Framework and device probes | FrameworkSpikeTests.swift, PhysicalCloudKitSpikeTests.swift, PhysicalScrubPerformanceTests.swift |
| End-to-end UI | LaunchTests.swift: setup, import, review, trim, replay, favorites, deletion, rotation, accessibility, remote Photos source |

Test scripts select simulators and run the Xcode Test configuration. `scripts/test-unit.sh`, `scripts/test-iphone.sh`, `scripts/test-ipad.sh`, and `scripts/test-all.sh` are the repository entry points.

This documentation task validates the HTML and references. It does not claim a new run of the app's simulator or physical-device test suites.

### Details that change how to read the architecture
- Simulator dependency wiring always uses fake metadata and asset services. Simulator success does not show live CloudKit synchronization.
- Test arguments can select in-memory stores, fake Photos, deterministic schedule fixtures, and isolated persistent stores.
- AppViewModel coordinates most actions; ScheduleReviewViewModel and MediaPlayerModel own distinct feature state.
- CloudAssetService performs direct database asset operations; CKSyncEngine handles metadata and deletion queues.
- The schema includes ScheduleExtractionRun, but the current schedule-review path does not write it.
- `addBout()` and the local source-copy API exist without a current screen calling them.
- CloudKitAssetSpikeService is a probe helper; normal uploads use LiveCloudAssetService.
- Scores, notes, automatic touch detection, and coaching summaries remain outside the current UI.
- Some documents describe broader or older paths. Function-level behavior in this guide follows the checked-in Swift implementation.

### Reading sources
The accepted release and operating instructions are in [FINAL_BUILD_OPERATIONS.md](../../FINAL_BUILD_OPERATIONS.md). Product intent comes from [ARCHITECTURE.md](../../ARCHITECTURE.md), [PRODUCT_REQUIREMENTS.md](../../PRODUCT_REQUIREMENTS.md), and [USER_JOURNEY.md](../../USER_JOURNEY.md).

The page uses the [answer-me-with-html skill](https://github.com/QingYunA/answer-me-with-html/blob/main/skills/answer-me-with-html/SKILL.md) and its bundled renderer. The authoring source is [architecture.md](architecture.md).

### Complete Swift declaration index
This index lists every named `func` declaration in the app source, including private helpers, protocol requirements, and fakes. Initializers, properties, and anonymous SwiftUI action closures are not counted as named functions. The action chapters above explain those UI triggers.

#### AppDependencies

[FencingVideoAnalysis/App/AppEntry/AppDependencies.swift](../../FencingVideoAnalysis/App/AppEntry/AppDependencies.swift)

| Function | Declaration line |
| --- | --- |
| `make()` | 48 |
| `syntheticDocument()` | 134 |

#### AppRootView

[FencingVideoAnalysis/App/AppEntry/AppRootView.swift](../../FencingVideoAnalysis/App/AppEntry/AppRootView.swift)

This file declares types, initializers, or view properties; it has no named function declaration.

#### AppViewModel

[FencingVideoAnalysis/App/AppEntry/AppViewModel.swift](../../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift)

| Function | Declaration line |
| --- | --- |
| `load()` | 126 |
| `refreshCloud()` | 161 |
| `saveFencerName()` | 184 |
| `saveTournament()` | 200 |
| `selectTournament()` | 229 |
| `deleteTournament()` | 234 |
| `addBout()` | 267 |
| `updateConfirmedBout()` | 285 |
| `isBoutFavorite()` | 320 |
| `refreshFavoriteBoutIDs()` | 322 |
| `deleteConfirmedBout()` | 327 |
| `confirmSchedule()` | 346 |
| `prepareRecordings()` | 409 |
| `confirmRecordings()` | 413 |
| `discardRecordings()` | 420 |
| `sourceRecordings()` | 424 |
| `localSourceURL()` | 428 |
| `sourceAsset()` | 432 |
| `connectPhotos()` | 436 |
| `moveRecording()` | 468 |
| `removeRecording()` | 472 |
| `mediaStatus()` | 480 |
| `createClip()` | 484 |
| `retryClip()` | 493 |
| `retryUpload()` | 503 |
| `deleteClip()` | 505 |
| `synchronizeDeletion()` | 516 |
| `reviewClips()` | 525 |
| `unloadBoutClips()` | 529 |
| `localUploadedClipBytes()` | 533 |
| `clearLocalClipCopies()` | 537 |
| `toggleClipFavorite()` | 541 |
| `playableURL()` | 563 |

#### FencingVideoAnalysisApp

[FencingVideoAnalysis/App/AppEntry/FencingVideoAnalysisApp.swift](../../FencingVideoAnalysis/App/AppEntry/FencingVideoAnalysisApp.swift)

This file declares types, initializers, or view properties; it has no named function declaration.

#### TournamentNavigationView

[FencingVideoAnalysis/App/Navigation/TournamentNavigationView.swift](../../FencingVideoAnalysis/App/Navigation/TournamentNavigationView.swift)

This file declares types, initializers, or view properties; it has no named function declaration.

#### BoutDetailView

[FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift](../../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift)

| Function | Declaration line |
| --- | --- |
| `move()` | 156 |
| `remove()` | 166 |
| `refreshRecordings()` | 179 |
| `save()` | 187 |
| `delete()` | 200 |
| `body()` | 247 |

#### BoutPlayerView

[FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift](../../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift)

| Function | Declaration line |
| --- | --- |
| `load()` | 158 |
| `openCurrent()` | 165 |
| `movePrevious()` | 184 |
| `moveNext()` | 189 |
| `finishCurrentClip()` | 194 |
| `unloadClips()` | 202 |
| `timeLabel()` | 219 |

#### RecordingImportReviewView

[FencingVideoAnalysis/Features/Bouts/RecordingImportReviewView.swift](../../FencingVideoAnalysis/Features/Bouts/RecordingImportReviewView.swift)

| Function | Declaration line |
| --- | --- |
| `prepare()` | 101 |
| `confirm()` | 127 |
| `cancel()` | 142 |

#### SourceTimelineView

[FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift](../../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift)

| Function | Declaration line |
| --- | --- |
| `load()` | 211 |
| `toggleFavorite()` | 222 |
| `select()` | 227 |
| `saveClip()` | 242 |
| `retry()` | 261 |
| `delete()` | 274 |
| `play()` | 283 |
| `timeLabel()` | 297 |

#### FirstRunSetupView

[FencingVideoAnalysis/Features/FirstRunSetup/FirstRunSetupView.swift](../../FencingVideoAnalysis/Features/FirstRunSetup/FirstRunSetupView.swift)

This file declares types, initializers, or view properties; it has no named function declaration.

#### ScheduleImportView

[FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift](../../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift)

| Function | Declaration line |
| --- | --- |
| `loadScreenshots()` | 156 |
| `startManual()` | 175 |
| `extract()` | 180 |
| `confirm()` | 186 |
| `sampleScreenshotData()` | 196 |
| `controls()` | 381 |
| `magnify()` | 423 |
| `pan()` | 433 |
| `setZoom()` | 447 |
| `resetZoom()` | 452 |
| `bounded()` | 459 |

#### ScheduleReviewViewModel

[FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift](../../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift)

| Function | Declaration line |
| --- | --- |
| `isRelevant()` | 42 |
| `reset()` | 69 |
| `extract()` | 76 |
| `addDraft()` | 116 |
| `removeDraft()` | 121 |
| `moveDraft()` | 126 |
| `moveDrafts()` | 132 |
| `message()` | 136 |
| `message()` | 150 |

#### FencerSettingsView

[FencingVideoAnalysis/Features/Settings/FencerSettingsView.swift](../../FencingVideoAnalysis/Features/Settings/FencerSettingsView.swift)

| Function | Declaration line |
| --- | --- |
| `clearLocalCopies()` | 81 |
| `refreshLocalStorage()` | 92 |

#### TournamentDetailView

[FencingVideoAnalysis/Features/Tournaments/TournamentDetailView.swift](../../FencingVideoAnalysis/Features/Tournaments/TournamentDetailView.swift)

| Function | Declaration line |
| --- | --- |
| `mediaSummary()` | 104 |

#### TournamentFormView

[FencingVideoAnalysis/Features/Tournaments/TournamentFormView.swift](../../FencingVideoAnalysis/Features/Tournaments/TournamentFormView.swift)

This file declares types, initializers, or view properties; it has no named function declaration.

#### DomainModels

[FencingVideoAnalysis/Models/DomainModels/DomainModels.swift](../../FencingVideoAnalysis/Models/DomainModels/DomainModels.swift)

This file declares types, initializers, or view properties; it has no named function declaration.

#### LocalRepository

[FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift](../../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift)

| Function | Declaration line |
| --- | --- |
| `insert()` | 25 |
| `fetch()` | 26 |
| `delete()` | 27 |
| `saveChanges()` | 28 |
| `insert()` | 40 |
| `fetch()` | 47 |
| `delete()` | 51 |
| `saveChanges()` | 55 |
| `makeContainer()` | 60 |
| `insert()` | 81 |
| `fetch()` | 88 |
| `delete()` | 92 |
| `saveChanges()` | 96 |
| `tournaments()` | 100 |
| `bouts()` | 107 |
| `sourceRecordings()` | 116 |
| `reviewClips()` | 123 |
| `deleteTournament()` | 136 |
| `deleteBout()` | 146 |

#### BoutImportCoordinator

[FencingVideoAnalysis/Services/BoutImportCoordinator.swift](../../FencingVideoAnalysis/Services/BoutImportCoordinator.swift)

| Function | Declaration line |
| --- | --- |
| `prepareSelections()` | 45 |
| `confirm()` | 55 |
| `discard()` | 85 |
| `requestPhotoAccess()` | 89 |
| `linkPendingCloudPhotos()` | 92 |
| `localCopy()` | 120 |
| `sourceAsset()` | 133 |
| `move()` | 164 |
| `remove()` | 187 |
| `status()` | 201 |

#### BoutPlaybackQueue

[FencingVideoAnalysis/Services/BoutPlaybackQueue.swift](../../FencingVideoAnalysis/Services/BoutPlaybackQueue.swift)

| Function | Declaration line |
| --- | --- |
| `select()` | 23 |
| `previous()` | 28 |
| `next()` | 35 |
| `didFinishCurrentClip()` | 42 |

#### ClipDownloadCoordinator

[FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift](../../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift)

| Function | Declaration line |
| --- | --- |
| `cachedURL()` | 63 |
| `store()` | 75 |
| `clear()` | 104 |
| `remove()` | 113 |
| `fileURL()` | 122 |
| `persist()` | 124 |
| `resolve()` | 142 |
| `clearCache()` | 176 |
| `removeCachedCopies()` | 178 |

#### ClipUploadQueue

[FencingVideoAnalysis/Services/ClipUploadQueue.swift](../../FencingVideoAnalysis/Services/ClipUploadQueue.swift)

| Function | Declaration line |
| --- | --- |
| `resumePending()` | 21 |
| `upload()` | 28 |
| `retry()` | 60 |
| `deleteCloudCopyIfNeeded()` | 72 |
| `setStatus()` | 88 |
| `isTemporaryCloudFailure()` | 94 |

#### ClipWorkflow

[FencingVideoAnalysis/Services/ClipWorkflow.swift](../../FencingVideoAnalysis/Services/ClipWorkflow.swift)

| Function | Declaration line |
| --- | --- |
| `createClip()` | 55 |
| `retry()` | 81 |
| `delete()` | 100 |
| `clips()` | 117 |
| `unloadUploadedClips()` | 121 |
| `localExportBytes()` | 152 |
| `clearLocalClipCopies()` | 159 |
| `managedExportFiles()` | 205 |
| `isManagedExportPath()` | 216 |
| `removeAbandonedFiles()` | 225 |

#### CloudAssetService

[FencingVideoAnalysis/Services/CloudAssetService.swift](../../FencingVideoAnalysis/Services/CloudAssetService.swift)

| Function | Declaration line |
| --- | --- |
| `saveExportedClip()` | 10 |
| `downloadClip()` | 11 |
| `deleteClip()` | 12 |
| `failNextSave()` | 19 |
| `saveExportedClip()` | 21 |
| `downloadClip()` | 29 |
| `deleteClip()` | 38 |
| `saveExportedClip()` | 50 |
| `downloadClip()` | 59 |
| `deleteClip()` | 68 |

#### CloudKitAssetSpikeService

[FencingVideoAnalysis/Services/CloudKitAssetSpikeService.swift](../../FencingVideoAnalysis/Services/CloudKitAssetSpikeService.swift)

| Function | Declaration line |
| --- | --- |
| `roundTrip()` | 12 |

#### CloudMetadataService

[FencingVideoAnalysis/Services/CloudMetadataService.swift](../../FencingVideoAnalysis/Services/CloudMetadataService.swift)

| Function | Declaration line |
| --- | --- |
| `message()` | 37 |
| `synchronize()` | 47 |
| `synchronizeDeletions()` | 48 |
| `queueDeletion()` | 49 |
| `synchronize()` | 53 |
| `synchronizeDeletions()` | 54 |
| `synchronize()` | 68 |
| `queueDeletion()` | 83 |
| `staleRecordNames()` | 92 |
| `knownRecordIDs()` | 98 |
| `append()` | 100 |
| `pendingRecords()` | 114 |
| `markSynchronized()` | 167 |
| `apply()` | 188 |
| `shouldApply()` | 306 |
| `encode()` | 312 |
| `decode()` | 313 |
| `make()` | 323 |
| `decode()` | 334 |
| `record()` | 356 |
| `remember()` | 367 |
| `forget()` | 377 |
| `persist()` | 384 |
| `useDownloadCoordinator()` | 425 |
| `synchronize()` | 430 |
| `synchronizeDeletions()` | 453 |
| `reconcileEntireZone()` | 466 |
| `reconcileKnownRecords()` | 506 |
| `queueDeletion()` | 530 |
| `scheduleSync()` | 539 |
| `nextRecordZoneChangeBatch()` | 554 |
| `handleEvent()` | 573 |
| `removeLocalRecord()` | 660 |
| `remove()` | 671 |
| `deleteLocalRecord()` | 680 |

#### DocumentRecognitionService

[FencingVideoAnalysis/Services/DocumentRecognitionService.swift](../../FencingVideoAnalysis/Services/DocumentRecognitionService.swift)

| Function | Declaration line |
| --- | --- |
| `addingQualityWarnings()` | 62 |
| `recognize()` | 86 |
| `recognize()` | 90 |
| `recognize()` | 178 |

#### ICloudSyncStatusService

[FencingVideoAnalysis/Services/ICloudSyncStatusService.swift](../../FencingVideoAnalysis/Services/ICloudSyncStatusService.swift)

| Function | Declaration line |
| --- | --- |
| `accountStatus()` | 9 |
| `accountStatus()` | 18 |
| `accountStatus()` | 38 |

#### OnDeviceModelService

[FencingVideoAnalysis/Services/OnDeviceModelService.swift](../../FencingVideoAnalysis/Services/OnDeviceModelService.swift)

| Function | Declaration line |
| --- | --- |
| `propose()` | 88 |
| `propose()` | 93 |
| `promptData()` | 124 |
| `propose()` | 157 |

#### PhotoLibraryService

[FencingVideoAnalysis/Services/PhotoLibraryService.swift](../../FencingVideoAnalysis/Services/PhotoLibraryService.swift)

| Function | Declaration line |
| --- | --- |
| `importSelections()` | 129 |
| `requestPhotoAccess()` | 130 |
| `localIdentifierForExistingRecording()` | 131 |
| `cloudIdentifiers()` | 133 |
| `copyFromICloudPhotos()` | 134 |
| `videoAsset()` | 135 |
| `removeWorkingFiles()` | 136 |
| `removeWorkingFile()` | 137 |
| `importSelections()` | 152 |
| `cloudIdentifiers()` | 225 |
| `localIdentifierForExistingRecording()` | 237 |
| `copyFromICloudPhotos()` | 260 |
| `videoAsset()` | 299 |
| `requestPhotoAccessFromSystem()` | 324 |
| `requestPhotoAccess()` | 331 |
| `removeWorkingFiles()` | 335 |
| `removeWorkingFile()` | 341 |
| `importSelections()` | 363 |
| `removeWorkingFiles()` | 394 |
| `cloudIdentifiers()` | 403 |
| `requestPhotoAccess()` | 408 |
| `localIdentifierForExistingRecording()` | 410 |
| `copyFromICloudPhotos()` | 416 |
| `videoAsset()` | 429 |
| `removeWorkingFile()` | 436 |

#### PlaybackState

[FencingVideoAnalysis/Services/PlaybackState.swift](../../FencingVideoAnalysis/Services/PlaybackState.swift)

| Function | Declaration line |
| --- | --- |
| `open()` | 10 |
| `seek()` | 18 |
| `setPlaying()` | 22 |
| `setSpeed()` | 24 |
| `open()` | 48 |
| `open()` | 52 |
| `play()` | 61 |
| `pause()` | 66 |
| `seek()` | 71 |
| `scrub()` | 77 |
| `finishScrub()` | 84 |
| `playerTimeDidChange()` | 94 |
| `setSpeed()` | 98 |
| `stop()` | 103 |

#### ScheduleParsingService

[FencingVideoAnalysis/Services/ScheduleParsingService.swift](../../FencingVideoAnalysis/Services/ScheduleParsingService.swift)

| Function | Declaration line |
| --- | --- |
| `parse()` | 63 |
| `parse()` | 67 |
| `mapping()` | 237 |
| `cell()` | 278 |
| `context()` | 282 |
| `capture()` | 305 |
| `normalizedHeader()` | 314 |
| `normalizedName()` | 318 |
| `numericValue()` | 326 |
| `normalizedStrip()` | 334 |
| `normalizedTime()` | 338 |
| `normalizedPhase()` | 347 |

#### ScheduleProposalValidator

[FencingVideoAnalysis/Services/ScheduleProposalValidator.swift](../../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift)

| Function | Declaration line |
| --- | --- |
| `reconcile()` | 26 |
| `mergeString()` | 126 |
| `mergeInt()` | 160 |
| `trace()` | 187 |
| `headerAllows()` | 246 |
| `sourceRow()` | 268 |
| `sameBout()` | 281 |
| `warning()` | 298 |
| `normalized()` | 304 |
| `normalizedDigits()` | 311 |
| `validTime()` | 317 |

#### ScheduleSourceService

[FencingVideoAnalysis/Services/ScheduleSourceService.swift](../../FencingVideoAnalysis/Services/ScheduleSourceService.swift)

| Function | Declaration line |
| --- | --- |
| `screenshots()` | 22 |
| `manual()` | 23 |
| `screenshots()` | 28 |
| `manual()` | 33 |
| `screenshots()` | 38 |
| `manual()` | 43 |

#### VideoEditingService

[FencingVideoAnalysis/Services/VideoEditingService.swift](../../FencingVideoAnalysis/Services/VideoEditingService.swift)

| Function | Declaration line |
| --- | --- |
| `validate()` | 10 |
| `cancel()` | 45 |
| `export()` | 50 |
| `export()` | 66 |
| `export()` | 110 |

#### VisualScrubCoordinator

[FencingVideoAnalysis/Services/VisualScrubCoordinator.swift](../../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift)

| Function | Declaration line |
| --- | --- |
| `seek()` | 6 |
| `seek()` | 13 |
| `drag()` | 35 |
| `finish()` | 41 |
| `cancel()` | 48 |
| `startWorkerIfNeeded()` | 56 |

Index totals: **35 Swift files; 276 named function declarations**. Overloads and protocol declarations count separately.
