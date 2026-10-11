# From the piste to the replay

Editorial architecture video · Practical STE-inspired narration

## A simpler way to review a bout

This app helps a parent review fencing videos with one fencer. It runs on an iPhone and an iPad.

A fencing match is called a bout. The parent can stop and restart the camera during that bout.

One bout can therefore have several recordings. The app groups them so the parent can find the right moments later.

The parent saves useful sections as review clips. A review clip is a separate, shorter movie from an original recording.

Both devices use the same private iCloud account. The parent can save a clip on the phone and review it on the tablet.

We will follow that work through the app. The app organizes video for review. It does not judge fencing technique.

## One app. Three storage boundaries.

Start with the screens on the left. They show tournaments, bouts, and clips. They also receive the parent's actions.

The app controller decides which work follows each action. Its code name is App View Model. Services perform the individual jobs.

The local store saves records on the current device. A record contains details about an item, such as a bout.

The schedule services turn screenshots into proposed bouts. This work stays on the device. The parent must confirm the result.

The media services open original recordings, export review clips, and control playback. The original recordings remain in Photos.

Private iCloud storage holds confirmed records and edited clips. Photos, the local device, and private CloudKit each have a different job.

## Open locally. Then refresh.

When the app starts, the entry code creates its dependencies. These are the services that the app needs to work.

The setup function connects the controller, local store, and media services. Tests can replace these services with controlled test versions.

The controller runs its load function. It reads the saved fencer name and tournament records from the local store.

If no fencer name exists, the app shows setup. After setup, the parent can create a tournament and add bouts.

When iCloud is available, refresh gets remote changes. It also connects pending Photos links and resumes unfinished clip uploads.

The app also removes old, abandoned working files from its managed folders. Original recordings in Photos remain unchanged.

## Read the schedule. Keep the parent in control.

The parent selects one or more schedule screenshots. The parent can also choose manual entry and type the bouts.

Vision reads words and table cells from each screenshot. The result includes their positions and warnings about uncertain text.

The rule parser finds the saved fencer in the table. It extracts the opponent and position in the full bout order.

The optional language model can help interpret the result. It runs on the device. The fixed rules remain available without it.

The evidence check compares proposed details with the recognized text. It rejects values that the screenshot data does not support.

The parent checks the proposed bouts and corrects mistakes. Confirm requires an opponent name and a positive, unique bout number.

The app saves valid new bouts. An identical saved bout does not need another record. Only confirmed details can reach iCloud.

## Choose the bout. Then choose the recordings.

The parent opens a known bout before selecting recordings. The app therefore knows where every selected recording should belong.

The import service prepares the selection. It checks for known recordings and records any files that it cannot open.

The parent reviews the results before confirmation. If one file fails, the parent can still confirm the other successful selections.

Confirmation creates a recording record for each successful selection. Each record links the recording to the chosen bout.

The app saves capture time, duration, and available Photos identifiers. An identifier is a stable label used to connect records.

The original stays in Photos. A shared Photos identifier can help the other device find the same recording.

The app orders recordings by capture time. It does not guess their bouts. An eligible recording link can move to another bout.

## Save a clip locally. Then upload it.

The parent opens an original recording and selects a start and end time. Save Clip starts the clip workflow.

The workflow checks the selected times. The start must come before the end, and both must fit inside the recording.

The video service exports that section into a separate movie. Export means creating this new file. The original remains unchanged.

The app saves the file location and clip duration. The clip record now says that an upload is pending.

The upload queue first saves the clip's metadata. Metadata means details such as its bout, source recording, and selected times.

Next, the asset service attaches the movie file to the cloud record. The app marks the clip available after upload succeeds.

A temporary network failure keeps the file for another attempt. Other errors can require Retry Upload. Failed exports can be exported again.

## Play separate clips as one bout.

The saved-bout player gets the review clips in time order. It sorts by original recording time, then by clip start time.

The playback queue tracks the current clip. Previous and Next change that selection. The app does not merge the movie files.

For each clip, the app first checks its local export. It then checks downloaded copies before requesting the file from iCloud.

The video player opens the resolved file. Continuous mode moves to the next clip when playback ends. Focused mode stops instead.

The transport controls set speed, time, and play or pause. The chosen speed remains active when the player changes clips.

Dragging the timeline asks the player to move to a time. This request is called a seek. The picture follows the drag.

The seek coordinator keeps the newest requested position. It avoids a queue of old positions. Release requests the final selected time.

## Recover changes without losing the distinction.

A local save marks work for synchronization. Stable record identifiers let the app update existing records instead of creating copies.

The metadata service sends pending changes and receives remote updates. It saves synchronization state so unfinished work can continue later.

Explicit refresh also checks the full metadata zone for missed records. The zone groups this app's records in private CloudKit storage.

Incoming changes update the local records. A clip record can arrive before its movie file. The player can show Waiting for upload.

Deleting a clip starts a coordinated removal. The app handles active uploads and a known cloud asset before removing the local clip.

The app queues the record deletion and clears downloaded copies. If cloud deletion cannot finish, the pending work remains for recovery.

Clear Local Clip Copies is different. It removes files that can be downloaded again. It keeps cloud records and protects pending uploads.

## The records connect the whole journey.

A tournament contains bouts. Each bout connects its original recordings and review clips. Stable identifiers keep these relationships clear.

Each review clip stores its source recording and selected time range. That link explains where the clip came from.

A favorite flag belongs to a review clip. The app treats a bout as a favorite when any clip has that flag.

Remember the three storage locations. Photos holds originals. The device holds local work. Private CloudKit holds confirmed records and edited clips.

The complete path is simple: choose a bout, select recordings, save useful clips, and review them together. The parent controls each choice.
