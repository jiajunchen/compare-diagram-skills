# Organization pathways

Step through first launch, tournament creation, and manual or screenshot schedule entry.

The source is the reviewed production-code analysis. Select a flow in the HTML to step through it. The Local only / iCloud available toggle reflects whether cloud-dependent steps can run.

## Components

- **Open app** (`launch`): Open app
- **AppDependencies.make** (`boot`): AppDependencies.make; open SwiftData; wire live services
- **AppViewModel.load** (`load`): AppViewModel.load; check iCloud; fetch local settings/tournaments
- **Settings found?** (`settings`): Settings found?
- **FirstRunSetupView** (`first`): FirstRunSetupView; saveFencerName -> SwiftData
- **TournamentNavigationView** (`nav`): TournamentNavigationView; select / refreshCloud
- **New Tournament** (`new`): New Tournament; TournamentFormView.save
- **AppViewModel.saveTournament** (`save`): AppViewModel.saveTournament; validate name; insert/update Tournament; SwiftData save -> schedule CloudKit sync
- **TournamentDetailView** (`detail`): TournamentDetailView; show bouts / open selected bout
- **Import Schedule** (`import`): Import Schedule; screenshot(s) or Manual Entry
- **Manual drafts** (`manual`): Manual drafts; add opponent + full-order bout number
- **Vision recognize each screenshot** (`ocr`): Vision recognize each screenshot; deterministic parse + optional on-device model; validator reconciles source-backed proposal
- **Review/edit drafts** (`review`): Review/edit drafts; confirm or discard
- **AppViewModel.confirmSchedule** (`confirm`): AppViewModel.confirmSchedule; validate nonempty, opponent, positive/unique number; insert new Bouts; mark tournament confirmed
- **BoutDetailView** (`bout`): BoutDetailView; edit/delete confirmed bout; import recordings

## Flows

### First launch

Local settings missing; save the fencer name.

1. **Open app → AppDependencies.make:** wire services.
2. **AppDependencies.make → AppViewModel.load:** load.
3. **AppViewModel.load → Settings found?:** check settings.
4. **Settings found? → FirstRunSetupView:** no.
5. **FirstRunSetupView → TournamentNavigationView:** save name.

### Returning launch

Existing local settings open navigation.

1. **Open app → AppDependencies.make:** wire services.
2. **AppDependencies.make → AppViewModel.load:** load.
3. **AppViewModel.load → Settings found?:** check settings.
4. **Settings found? → TournamentNavigationView:** yes.

### Create tournament

Save one Tournament record before importing bouts.

1. **TournamentNavigationView → New Tournament:** New Tournament.
2. **New Tournament → AppViewModel.saveTournament:** validate / insert.
3. **AppViewModel.saveTournament → TournamentDetailView:** open detail.

### Manual schedule

Manual drafts use full-order bout numbers.

1. **TournamentDetailView → Import Schedule:** Import Schedule.
2. **Import Schedule → Manual drafts:** manual.
3. **Manual drafts → Review/edit drafts:** edit drafts.
4. **Review/edit drafts → AppViewModel.confirmSchedule:** confirm.
5. **AppViewModel.confirmSchedule → BoutDetailView:** open bout.

### Screenshot schedule

Vision and parser produce editable source-backed proposals.

1. **TournamentDetailView → Import Schedule:** Import Schedule.
2. **Import Schedule → Vision recognize each screenshot:** screenshots.
3. **Vision recognize each screenshot → Review/edit drafts:** edit drafts.
4. **Review/edit drafts → AppViewModel.confirmSchedule:** confirm.
5. **AppViewModel.confirmSchedule → BoutDetailView:** open bout.

## Scope notes

- The entity page shows UUID references; its steps are relationship traversal, not method calls.
- The object-call page shows principal production calls. See [CALL_INDEX.md](../CALL_INDEX.md) for all function declarations.
- Photos originals are external. CloudKit stores confirmed metadata and edited review clips.
- Schema-only ScheduleExtractionRun has no production insertion call.
