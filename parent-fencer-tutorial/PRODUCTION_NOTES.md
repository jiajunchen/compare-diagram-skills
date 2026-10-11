# Capture decisions

The capture harness lives outside the application and compiles through a temporary project. No product code changes were needed.

- **Photos permission:** Attempts to grant permission externally did not reliably suppress the prompt during the UI test. Granting while the app was running also invalidated its automation connection. After reassessing this approach, the capture now resets authorization before launch and records the actual system Allow Full Access button. This matches a new user's experience and has its own narrated step.
- **Schedule review:** The visible review card can contain warnings above its proposed bouts. Waiting for an offscreen, lazily created text field is insufficient. The capture now scrolls the schedule list and waits for the opponent field. An earlier assumption that recognition had rejected the whole schedule was incorrect: the rows needed to be brought into view. The fixture also uses explicit bout numbers for clarity.
- **Confirmation buttons:** SwiftUI exposes more than one accessibility match for some confirmation controls. The harness selects the first matching control. Deletion and cleanup assertions confirm the action's result.
- **Final capture:** Exploratory takes were used to verify the individual paths. The delivered film is rendered from the final complete run, after these capture issues were resolved.

The UI assertions cover two imported schedule bouts, a manually entered bout, successful video import, two exported review clips, the clip favorite state, the derived bout favorite state, deletion leaving one clip, and cleared local storage disabling the cleanup action.

The raw simulator movie uses sparse frames during still screens. Composition first converts the whole recording to a constant 30 fps, preserving still-screen holds before making per-instruction cuts. Visual QA caught and corrected direct-seek jumps across these holds.
