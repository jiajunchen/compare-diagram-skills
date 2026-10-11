# How the Fencing Review App Works

This video explains the app's purpose first. Then it follows a recording through the app, one step at a time.

## Why this app exists

This app helps a parent review fencing videos with one fencer. It runs on an iPhone and an iPad.

A Parent can stop the camera during a long pause. One fencing match, called a bout, can therefore have several recordings.

Those recordings stay in Photos. The app groups the recordings by tournament and bout, so the parent can find them later.

The parent saves useful sections as Review clips. Each review clip contains a short part of an original recording.

The parent and fencer can watch those clips together. The current app organizes video for review. It does not judge fencing technique.

## Follow one bout through the app

First, the parent enters the fencer's name and creates a tournament. The app saves the name for later tournaments.

Next, the parent adds the bouts. The app can read a schedule screenshot. The parent checks the result before saving it.

The parent opens the correct bout and selects its recordings. For example, two recordings can belong to the same bout.

The parent selects a useful section from each recording. The app saves each section as a separate review clip.

The app sends the review clips to private iCloud storage. The parent can then watch them on an iPad with the same account.

## How the app connects the records

Now look inside the app. A record is a saved set of details about an item, such as a tournament.

Each Bout belongs to one tournament. Each recording link belongs to one bout. Unique labels, called identifiers, connect these records.

A Recording link tells the app which original recording to open. The original video file stays in Photos.

A Review clip has a start time and an end time within that original recording. One recording can supply several review clips.

The app sorts review clips by recording time, then by start time. The app plays separate files in that order.

## Which part does each job

The Screen shows information and receives the parent's actions. For example, the parent can tap Save Clip.

The App controller decides what work must happen next. Its code name is AppViewModel. We will call it the app controller.

Services do specific jobs. One service opens recordings from Photos. Other services create review clips or transfer files.

The Local store holds records on the current device. The app uses Apple's SwiftData tool to read and save these records.

These parts have separate jobs. Tests can replace an Apple service with a test service, then check the app's response.

## What happens when the app opens

When the app opens, the Setup code connects the app controller, local store, and services. The make function starts this setup.

The app controller then runs its load function. It reads the fencer's name and tournament records from the local store.

If the app has no saved fencer name, the parent enters one. The app checks that the name is not empty.

When the parent saves a tournament, the app checks its name. Then the app saves the tournament in the local store.

The app also checks iCloud. If iCloud is available, the app gets remote changes. Local work can continue when iCloud is unavailable.

## How the app reads a schedule

The parent selects a schedule screenshot. The Text reader finds the words and table cells. This reader uses Apple's Vision tool.

The Rule parser applies fixed rules to the table. It finds the saved fencer's name, the opponent, and the bout number.

The Optional model can suggest missing details. This language model runs on the device. The app can continue without it.

The Evidence check compares each suggestion with the screenshot data. It rejects values that the source data does not support.

The app shows Draft bouts for the parent to review. A draft is a proposed record. The app has not confirmed it yet.

## Why the parent must confirm the schedule

The parent checks each opponent and bout number. The parent can correct a draft, remove it, or add a bout manually.

Confirm Schedule calls the confirmSchedule function. The app requires an opponent name and a positive bout number for each draft.

If two different opponents have the same bout number, the app asks for a correction. It does not save that draft set.

The app saves valid new bouts in the Local store. An identical saved bout does not need another record.

Only confirmed details enter the Cloud records. Screenshots and draft text stay on the device. Discard closes the review without saving bouts.

## How recordings enter a bout

The parent opens a bout before selecting recordings. The Import service therefore knows which bout should receive each recording link.

The parent can select up to twenty recordings. The app checks for duplicate selections and recordings that it cannot open.

The Bout screen shows the results. If one selection fails, the parent can still confirm the other selections.

After confirmation, the app saves the recording links. Normal imports save Photos links and recording details, without another full video copy.

The app can share a Photos link with the other device. To open the original, that device also needs Photos access.

## How the app creates a review clip

The parent opens an original recording. The parent marks the start and end of a useful section, then taps Save Clip.

Save Clip calls createClip. The Clip service checks that the start comes before the end and that both times fit the recording.

The Video tool copies that section into a separate movie file. The app calls this process an export. The original stays unchanged.

The app saves the file location and clip duration. It also records that the review clip still needs an upload.

Cancel stops the export and removes the unfinished file. If export fails, Retry uses the saved start and end times.

## How a review clip reaches iCloud

The Upload service sends saved review clips to iCloud. The local store keeps a list of clips that still need an upload.

First, the service saves the clip's Cloud record. This record contains details such as the bout, original recording, and selected times.

Next, the service attaches the Video file to that record. The file upload uses a separate CloudKit call from the record update.

After the upload succeeds, the app marks the clip Available. The other device can request the review clip when the parent opens it.

If the network fails, the app keeps the local file for another attempt. Other errors can require the Retry Upload button.

## How the app plays the review clips

Play Bout gets the review clips in time order. The player starts with the selected clip in this list.

For each clip, the app first looks for a Local file. If no export file exists, the app checks downloaded copies.

A Downloaded copy is a temporary local copy of a cloud file. The app downloads the clip only when necessary.

Continuous mode starts the next clip when the current clip ends. Single-clip mode stops at the end of the current clip.

The parent can also select Previous or Next. Half speed, normal speed, and double speed remain available during review.

## How the picture follows the slider

The parent drags the Slider to move through a clip. The picture changes during the drag, so the parent can find an action.

The Seek service asks the video tool to move to a time. A seek is a request to change the playback position.

The service handles one seek at a time. If the parent drags again, the service keeps the newest position.

During a drag, the video tool can show a nearby frame. After release, the service requests the exact selected time.

This method avoids a long list of old requests. When the parent closes the player, the app stops playback and cancels pending requests.

## How the app handles changes and deletions

A local save asks the Cloud service to send changed records. The service also gets changes from the other device.

The app saves transfer progress on the device. After a restart, the cloud service can continue work that remains unfinished.

Refresh also checks for records that the device missed. If both devices changed a record, the newer remote update can replace it.

A Delete action differs from removal of a downloaded copy. Delete removes the app record and its cloud file where applicable.

The app blocks removal of a recording link while review clips still use it. Tournament deletion removes clips before their parent records.

## Favorites, storage, and the main idea

When the parent stars a review clip, the app saves a favorite flag. A bout is a favorite if any clip has that flag.

Clear Local Clip Copies removes local files that the app can get from iCloud again. The app keeps files that still need an upload.

Unload Bout Clips applies to one bout. It first checks that every local export in that bout has an available cloud copy.

Remember the three storage locations. Photos holds original recordings. The device holds local work. Private iCloud storage holds confirmed records and review clips.

These parts support one task: find a bout, save useful review clips, and watch them together. The parent remains in control of each choice.
