# Narration revision: practical STE target

The user requested about 80% of the way toward ASD-STE100, with app background before the technical explanation.

This revision applies the high-value writing practices: short sentences, active voice, clear action order, common words, and one term for one meaning. The renderer uses `style: 80`. This setting selects its practical writing checks; it does not calculate an ASD-STE100 conformity percentage. This is an STE-inspired explanation, not a certified dictionary audit.

References: [official ASD-STE100 overview](https://asd-ste100.org/about.html), [official writing guidance FAQ](https://www.asd-ste100.org/STE_faq.html), and [Issue 9 specification](https://www.asd-ste100.org/assets/files/ASD-STE100_ISSUE9.pdf).

## What changed

- Added two opening chapters: the app's audience and purpose, then one complete bout-review example.
- Explained a bout before using the term throughout the video.
- Defined record, identifier, draft, export, downloaded copy, and seek before relying on them.
- Explained each component's job before giving its code name.
- Kept most exact function names in diagrams so the listener need not decode long code names.
- Replaced abstract descriptions with concrete actions and conditions.
- Used the same names for original recordings, recording links, and review clips.
- Preserved the important storage, confirmation, upload, playback, and deletion behavior.

## Examples

| Earlier wording | Revised approach |
| --- | --- |
| Observable state connects the results back to the interface. | The screen shows information and receives the parent's actions. |
| LocalRepository gives these components a shared persistence interface. | The local store holds records on the current device. |
| The on-device language model proposes typed candidates. | This language model runs on the device. The app can continue without it. |
| The resolver prefers a local export. | For each clip, the app first looks for a local file. |
| New drag positions replace obsolete pending positions. | If the parent drags again, the service keeps the newest position. |

## Terms used in the narration

| Term | Meaning |
| --- | --- |
| Bout | One fencing match |
| Original recording | A video in Photos |
| Recording link | App details that identify an original recording |
| Review clip | A separate movie containing a selected section of an original recording |
| Record | A saved set of details about an item |
| App controller | AppViewModel, which decides what work happens next |
| Local store | Records on the current device, stored with SwiftData |
| Service | A component that does a specific job |
| Cloud record | Portable app details in private CloudKit storage |
| Downloaded copy | A local copy of a cloud video file |
| Export | Creation of a separate movie from a selected time range |
| Seek | A request to change the playback position |

## Checks

[language-validation.json](language-validation.json) records the current measurements. Every narration sentence has at most 18 words. The mean is 9.5 words across 155 sentences. No sentence exceeds the revision's 20-word target. No narration beat contains a semicolon or more than six sentences.

The renderer reports zero writing warnings. A manual review also checks term consistency, explanation order, and technical meaning. Automated checks alone cannot establish complete conformity with the STE dictionary.
