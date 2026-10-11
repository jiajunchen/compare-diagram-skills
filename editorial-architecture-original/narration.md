# Original technical narration

Restored from commit 7179657, before the ASD-STE100 revision.

## From Fencing Footage to Review

Imagine recording a fencing bout in several short bursts. How does the app turn those separate recordings into an ordered, cross-device review?

We will follow the data, then the function calls. Every path comes from the current Swift implementation, including its failure and recovery behavior.

## One bout, many recordings

Start with a tournament. Each Bout belongs to that tournament, and each bout can contain many source recordings.

A SourceRecording describes an original video in Photos. Stopping and restarting the camera creates another source, not another bout.

Each ReviewClip selects a start and end within one source. Several clips can therefore point back to the same recording.

Continuous review does not merge those movie files. The repository sorts clips by source capture time, clip start time, and finally identifier.

One global setting stores the fencer's name. These relationships use explicit identifiers; the code does not rely on automatic SwiftData relationship cascades.

## Screens, state, and services

Think of SwiftUI as the controls. Screens collect choices and display results, while the app view model coordinates most user actions.

AppViewModel exposes operations such as saveTournament, confirmSchedule, createClip, and refreshCloud. Observable state connects the results back to the interface.

Coordinators handle focused workflows. BoutImportCoordinator manages sources; ClipWorkflow manages exports; separate upload and download coordinators move edited clips.

LocalRepository gives these components a shared persistence interface. SwiftData stores records locally, and explicit save calls can trigger cloud synchronization.

Framework adapters wrap Photos, AVFoundation, Vision, Foundation Models, and CloudKit. Dependency injection lets tests replace them with controlled fakes.

## Launch and ordinary edits

Launch begins with AppDependencies dot make. It creates the repository, chooses service implementations, and supplies the root view with dependencies.

The root creates Model state and calls load. Local settings and tournaments load first; available iCloud then permits a refresh.

With no saved fencer setting, the app shows setup. Continue calls saveFencerName; an empty name produces a validation error.

Tournament forms call saveTournament. Selecting a tournament calls selectTournament, which reads its ordered bouts. Bout edits call updateConfirmedBout and reject number collisions.

Each successful local save reaches Storage immediately. Cloud work follows asynchronously. Foreground activation and pull-to-refresh call refreshCloud to discover remote changes.

## Read the schedule on-device

The screenshot picker supplies image data to ScheduleReviewViewModel. Its extract function starts Vision recognition on each selected screenshot.

Recognition collects tables, cells, text, and positions. The deterministic Parser matches the saved fencer and derives the opponent and full bout-order number.

Model assistance is optional. The on-device language model proposes typed candidates when available; failure leaves the deterministic results available.

The Validator checks source evidence before accepting suggestions. A model response cannot invent a valid row simply by sounding confident.

Editable drafts remain local and unconfirmed. Unsupported layouts can fall back to manual entry; screenshots and recognized text never enter the app's CloudKit records.

## Human confirmation is the boundary

The parent edits opponent names and bout numbers before tapping Confirm Schedule. That action calls the app view model's confirmSchedule function.

Validation requires a known tournament, at least one draft, nonempty opponents, and positive unique bout numbers.

A number that conflicts with another saved opponent blocks confirmation. The app skips an identical number and opponent pair, avoiding a duplicate.

Confirmed bouts retain opponent and number from this screen. The phase becomes unknown; other extracted context does not become imported bout fields.

Only after saving can Cloud metadata synchronize these records. Discard writes nothing; a save failure removes inserted rows and restores prior tournament fields.

## Import links, not original uploads

Import begins inside a selected bout. The parent chooses up to twenty videos, so the destination is explicit; no automatic bout matching occurs.

Preparation checks known Photos identifiers and rejects duplicates. Normal imports read metadata and retain a Photos link without copying the full original.

Photos can return usable selections alongside individual failures. Confirmation inserts source records; cancelling discards the prepared batch and any temporary working files.

linkPendingCloudPhotos maps device-local identifiers to portable cloud identifiers. Those portable links synchronize, while local identifiers and file paths stay on the device.

Opening a source calls sourceAsset, then PhotoKit's videoAsset path. Photos can download its original; a legacy app copy provides fallback when available.

## Turn a time range into a clip

In the source timeline, the parent marks start and end. Save Clip calls createClip with a trim range and progress callback.

Workflow validates finite times, increasing bounds, and source duration. It saves a ReviewClip record with exporting status before rendering starts.

The Exporter uses AVAssetExportSession with a passthrough preset. It writes the selected range as an independent movie in the PendingClips folder.

Successful export saves the local path and measured duration, then changes status to pendingUpload. AppViewModel starts an asynchronous upload task.

Cancel stops the export and removes partial output. Export failure leaves a retryable record; retryClip exports again using the same clip identifier.

## Metadata first, video second

pendingUpload and the local export path form a durable queue. resumePending retries queued or interrupted uploads when cloud refresh reaches that stage.

upload first synchronizes the Metadata record. That creates the destination record before the service tries to attach the edited movie.

CKAsset upload uses a direct CloudKit database save. The metadata engine and asset service therefore take separate paths, even though they share one record.

Success marks the clip available. Temporary account or network failures return it to the queue; other failures can require an explicit Retry Upload.

An in-flight set prevents duplicate uploads. Deletion waits for an active upload, and late callbacks check that they must not restore a deleted clip.

## Resolve once, play in order

Play Bout builds an Ordered queue from the repository's sorted review clips. openCurrent then asks playableURL to resolve the selected file.

The resolver prefers a Local export. If that file is absent, it checks the managed download cache before contacting CloudKit.

A downloaded Cloud asset enters the cache and must contain a video track. Missing asset data can mean the other device is still uploading.

AVPlayer opens the resolved URL. At the end notification, continuous mode advances through the queue; focused mode pauses on the current clip.

Previous, Next, and clip selection use the same resolver. The selected playback speed survives automatic transitions, so reviewing slowly remains consistent across files.

## Scrubbing follows the newest intent

Dragging the Slider calls scrub on the player model. It clamps the time and sends the newest position to the scrub coordinator.

The Scrub coordinator keeps at most one seek in flight. New drag positions replace obsolete pending positions instead of creating a decoding backlog.

Preview seeks allow a small tolerance. Releasing the slider calls finishScrub and requests an exact final seek at the selected time.

Player model ignores ordinary playhead updates during the drag. Generation checks stop an old completion from altering a newly opened recording.

Speed controls offer half, normal, and double speed. The model updates an active player's rate immediately; leaving the screen stops playback and cancels scrub work.

## Cloud recovery and safe deletion

A Local save schedules metadata work through the repository callback. CKSyncEngine sends changes, fetches changes, and persists its recovery state locally.

Explicit refresh also scans the metadata zone to repair missed deliveries. Pending local saves and deletions receive protection during this reconciliation.

Conflict handling remembers the server record version. A newer remote value can win; otherwise the local change retries against the current version.

A Delete action removes cloud-backed clip assets before their local records. Removing a source requires no clips; deleting a bout requires no linked media.

Tournament deletion proceeds through clips, sources, bouts, and the tournament. It is not one transaction; failures can leave partial progress and queued cloud deletion.

## Keep meaning, release local bytes

A Clip star changes favorite metadata without exporting the movie again. The bout star derives from its clips, rather than a separate user toggle.

Offload checks distinguish deletion from storage cleanup. Bout unloading requires every local export in that bout to have a confirmed available cloud asset.

Global cleanup skips pending uploads, removes eligible uploaded copies, and clears downloaded clips. Managed-path checks protect files outside the app's workspace.

Cloud clips remain available for later download. Originals stay in Photos; screenshots stay local; the app's private cloud stores portable metadata and edited clips.

That separation makes the architecture work: local progress, explicit confirmation, independent media files, and recoverable transfer. Simulator fakes test logic; real cloud behavior still needs device checks.
