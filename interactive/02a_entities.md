# Entity relationships

Follow persisted identifiers, Photos references, and CloudKit assets. These are relationships, not runtime calls.

The source is the reviewed production-code analysis. Select a flow in the HTML to step through it. The Local only / iCloud available toggle reflects whether cloud-dependent steps can run.

## Components

- **AppSettings** (`settings`): AppSettings; PK id (stable cloudID); fencerName, syncState
- **Tournament** (`tournament`): Tournament; PK id; name, venue, startDate, timezone; scheduleImportStatus, syncState
- **Bout** (`bout`): Bout; PK id | FK tournamentID; phase, opponent, sequenceNumber; pool, strip, scheduledAt, syncState
- **ScheduleExtractionRun** (`run`): ScheduleExtractionRun; PK id | FK tournamentID; status, warnings, modelAssistanceUsed; (schema only; no production inserts)
- **SourceRecording** (`source`): SourceRecording; PK id | FK tournamentID, boutID; importBatchID, Photos IDs; recordedAt, duration, localWorkingFilePath
- **ReviewClip** (`clip`): ReviewClip; PK id | FK boutID, sourceRecordingID; trim range, localExportPath; cloudAssetRecordName, mediaSyncStatus; isFavorite
- **PHAsset (Photos)** (`photo`): PHAsset (Photos); original recording
- **CKRecord + CKAsset** (`asset`): CKRecord + CKAsset; ReviewClip-{UUID}

## Flows

### Tournament records

One tournament owns ordered bouts and linked recordings.

1. **AppSettings → Tournament:** fencer name.
2. **Tournament → Bout:** 1 to many.
3. **Bout → SourceRecording:** 1 to many.
4. **SourceRecording → ReviewClip:** 1 to many.

### Direct UUID references

Links are ID fields, not SwiftData @Relationship properties.

1. **Tournament → SourceRecording:** tournamentID.
2. **Bout → ReviewClip:** boutID.

### Photos original

SourceRecording stores identifiers for an external original.

1. **SourceRecording → PHAsset (Photos):** Photos asset IDs.

### Cloud clip asset

Edited review clip points to its private CloudKit asset.

1. **ReviewClip → CKRecord + CKAsset:** cloudAssetRecordName.

### Schema-only run

ScheduleExtractionRun is modeled but has no production insertion path.

1. **Tournament → ScheduleExtractionRun:** schema reference.

## Scope notes

- The entity page shows UUID references; its steps are relationship traversal, not method calls.
- The object-call page shows principal production calls. See [CALL_INDEX.md](../CALL_INDEX.md) for all function declarations.
- Photos originals are external. CloudKit stores confirmed metadata and edited review clips.
- Schema-only ScheduleExtractionRun has no production insertion call.
