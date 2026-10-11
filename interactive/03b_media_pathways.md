# Media pathways

Track Photos links, trim/export, private asset upload, playback, retry, and cleanup.

The source is the reviewed production-code analysis. Select a flow in the HTML to step through it. The Local only / iCloud available toggle reflects whether cloud-dependent steps can run.

## Components

- **Open confirmed bout** (`bout`): Open confirmed bout
- **Import Recordings** (`pick`): Import Recordings; PhotosPicker: up to 20 videos
- **BoutImportCoordinator.prepareSelections** (`prepare`): BoutImportCoordinator.prepareSelections; PhotoLibraryService reads metadata / Photos IDs; show batch, failures, cancellation
- **Confirm batch** (`confirm`): Confirm batch; insert SourceRecording links in SwiftData; try linking iCloud Photos IDs
- **Review and Trim Recordings** (`timeline`): Review and Trim Recordings; load ordered sources + clips
- **Open source** (`asset`): Open source; PhotoKit AVAsset; local fallback if needed
- **Select trim range** (`trim`): Select trim range; ClipWorkflow.createClip -> AVFoundation export; ReviewClip: exporting -> pendingUpload
- **ClipUploadQueue.upload** (`upload`): ClipUploadQueue.upload; sync metadata -> save CKAsset; ReviewClip: uploading -> available
- **Failure path** (`fail`): Failure path; exportFailed / pendingUpload / needsAttention; retry export or upload
- **Play clip / Play Bout** (`play`): Play clip / Play Bout; ordered ReviewClips -> playableURL
- **Local export or managed cache?** (`local`): Local export or managed cache?
- **ClipDownloadCoordinator.resolve** (`download`): ClipDownloadCoordinator.resolve; check iCloud -> download CKAsset -> cache
- **MediaPlayerModel + BoutPlaybackQueue** (`player`): MediaPlayerModel + BoutPlaybackQueue; seek, scrub, speed, next clip (continuous)
- **Unload / Clear Local Copies** (`offload`): Unload / Clear Local Copies; only confirmed available exports; clear cache; retain CloudKit records/assets
- **Delete clip/source/bout/tournament** (`delete`): Delete clip/source/bout/tournament; asset first, then local records, queue metadata deletion; Photos original stays intact

## Flows

### Import recordings

Selections are reviewed before SourceRecording links are inserted.

1. **Open confirmed bout → Import Recordings:** PhotosPicker.
2. **Import Recordings → BoutImportCoordinator.prepareSelections:** prepareSelections.
3. **BoutImportCoordinator.prepareSelections → Confirm batch:** Add to Bout.
4. **Confirm batch → Review and Trim Recordings:** load sources.

### Trim and upload

Export locally first; upload confirmed edited clip.

1. **Review and Trim Recordings → Open source:** open source.
2. **Open source → Select trim range:** select range.
3. **Select trim range → ClipUploadQueue.upload:** export success.
4. **ClipUploadQueue.upload → Play clip / Play Bout:** available.

### Retry a failure

Status is retained for export or cloud retry.

1. **Select trim range → Failure path:** export failure.
2. **Failure path → ClipUploadQueue.upload:** retry.
3. **ClipUploadQueue.upload → Play clip / Play Bout:** available.

### Local playback

A local export or managed cache plays without a fresh download.

1. **Play clip / Play Bout → Local export or managed cache?:** resolve URL.
2. **Local export or managed cache? → MediaPlayerModel + BoutPlaybackQueue:** yes.
3. **MediaPlayerModel + BoutPlaybackQueue → Unload / Clear Local Copies:** optional cleanup.

### Cloud playback

Download edited clip when local media is unavailable.

1. **Play clip / Play Bout → Local export or managed cache?:** resolve URL.
2. **Local export or managed cache? → ClipDownloadCoordinator.resolve:** no.
3. **ClipDownloadCoordinator.resolve → MediaPlayerModel + BoutPlaybackQueue:** cached URL.

### Delete safely

Cloud asset deletion precedes local record cleanup; Photos original remains.

1. **Review and Trim Recordings → Delete clip/source/bout/tournament:** delete action.

## Scope notes

- The entity page shows UUID references; its steps are relationship traversal, not method calls.
- The object-call page shows principal production calls. See [CALL_INDEX.md](../CALL_INDEX.md) for all function declarations.
- Photos originals are external. CloudKit stores confirmed metadata and edited review clips.
- Schema-only ScheduleExtractionRun has no production insertion call.
