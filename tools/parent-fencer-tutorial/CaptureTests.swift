import XCTest
import UIKit

/// Media-production harness, compiled only by the isolated tutorial project.
final class TutorialCaptureTests: XCTestCase {
    let app = XCUIApplication()
    var lesson = 1
    var step = 0

    func emit(_ kind: String, _ label: String, _ element: XCUIElement? = nil) {
        let r = element?.frame ?? .zero
        let screen = app.frame
        let event: [String: Any] = ["kind": kind, "lesson": lesson, "step": step,
            "label": label, "time": Date().timeIntervalSince1970,
            "rect": [r.minX, r.minY, r.width, r.height],
            "screen": [screen.width, screen.height]]
        let data = try! JSONSerialization.data(withJSONObject: event, options: [.sortedKeys])
        print("TUTORIAL_EVENT " + String(data: data, encoding: .utf8)!)
        fflush(stdout)
    }
    func tap(_ element: XCUIElement, _ label: String) {
        XCTAssertTrue(element.waitForExistence(timeout: 20), label)
        guard element.exists else { print(app.debugDescription); return }
        step += 1; emit("begin", label, element)
        Thread.sleep(forTimeInterval: 0.7)
        emit("tap", label, element); element.tap()
        Thread.sleep(forTimeInterval: 1.5); emit("end", label)
    }
    func type(_ element: XCUIElement, _ text: String, _ label: String, replace: Bool = false) {
        tap(element, label)
        emit("typing", label, element)
        if replace, let old = element.value as? String, !old.isEmpty {
            element.typeText(String(repeating: XCUIKeyboardKey.delete.rawValue, count: old.count))
        }
        element.typeText(text)
        Thread.sleep(forTimeInterval: 0.7); emit("typed", label, element)
    }
    func hold(_ label: String, _ element: XCUIElement? = nil) {
        step += 1; emit("begin",label,element);Thread.sleep(forTimeInterval:2.0);emit("end",label)
    }
    func scroll(_ label: String, up: Bool = true) {
        step += 1;emit("begin",label)
        if up { app.swipeUp() } else { app.swipeDown() }
        Thread.sleep(forTimeInterval:0.8);emit("end",label)
    }
    func slider(_ id: String, _ value: CGFloat, _ label: String) {
        let control=app.sliders[id]
        XCTAssertTrue(control.waitForExistence(timeout:10))
        step += 1;emit("begin",label,control);Thread.sleep(forTimeInterval:0.7)
        emit("drag",label,control);control.adjust(toNormalizedSliderPosition:value)
        Thread.sleep(forTimeInterval:1);emit("end",label)
    }
    func testRecordSevenLessons() {
        continueAfterFailure = false
        XCUIDevice.shared.orientation = .landscapeLeft
        app.launchArguments = ["-testStoreID",UUID().uuidString,"-useFakeCloudKit"]
        print("TUTORIAL_READY_FOR_PHOTOS"); fflush(stdout)
        Thread.sleep(forTimeInterval: 4)
        app.launch()
        XCTAssertTrue(app.textFields["fencerNameField"].waitForExistence(timeout:20))
        Thread.sleep(forTimeInterval:2)
        hold("welcome")
        type(app.textFields["fencerNameField"],"Alex Rivera","enter-fencer")
        tap(app.buttons["continueSetupButton"],"continue-setup")
        tap(app.buttons["newTournamentButton"],"new-tournament")
        type(app.textFields["tournamentNameField"],"Autumn Practice Open","tournament-name")
        tap(app.buttons["saveTournamentButton"],"save-tournament")
        if !app.buttons["importScheduleButton"].exists { tap(app.staticTexts["Autumn Practice Open"].firstMatch,"open-tournament") }
        hold("tournament-ready")

        lesson=2
        tap(app.buttons["importScheduleButton"],"import-schedule")
        tap(app.buttons["selectScheduleScreenshotsButton"],"open-screenshot-photos")
        Thread.sleep(forTimeInterval:2)
        print("PICKER_TREE " + app.debugDescription)
        let cell=app.images.matching(NSPredicate(format:"identifier == 'PXGGridLayout-Info' AND label BEGINSWITH 'Photo,'")).firstMatch
        XCTAssertTrue(cell.waitForExistence(timeout:10), "Schedule photo in picker")
        tap(cell,"select-screenshot")
        tap(app.buttons["Add"].firstMatch,"add-screenshot")
        XCTAssertTrue(app.buttons["confirmScheduleButton"].waitForExistence(timeout:30))
        let scheduleList = app.descendants(matching: .any)["scheduleReviewList"]
        step += 1; emit("begin", "review-schedule", scheduleList)
        scheduleList.swipeUp()
        XCTAssertTrue(app.textFields["reviewOpponentField"].firstMatch.waitForExistence(timeout: 10))
        Thread.sleep(forTimeInterval: 2); emit("end", "review-schedule")
        tap(app.buttons["confirmScheduleButton"],"confirm-schedule")
        XCTAssertTrue(app.buttons["openBoutDetailButton-1"].waitForExistence(timeout:10))
        hold("schedule-ready")

        lesson=3
        tap(app.buttons["importScheduleButton"],"manual-open")
        tap(app.buttons["manualScheduleButton"],"manual-entry")
        tap(app.buttons["addProposedBoutButton"],"add-manual-bout")
        type(app.textFields["reviewOpponentField"].firstMatch,"Casey Jordan","manual-opponent")
        type(app.textFields["reviewBoutNumberField"].firstMatch,"4","manual-number",replace:true)
        tap(app.buttons["confirmScheduleButton"],"confirm-manual")
        XCTAssertTrue(app.buttons["openBoutDetailButton-4"].waitForExistence(timeout:10))
        hold("manual-ready")

        lesson=4
        tap(app.buttons["openBoutDetailButton-1"],"choose-bout")
        tap(app.buttons["importRecordingsButton"],"import-videos")
        tap(app.buttons["selectRecordingsButton"],"select-recordings")
        Thread.sleep(forTimeInterval:2)
        print("VIDEO_PICKER_TREE " + app.debugDescription)
        let videos=app.images.matching(NSPredicate(format:"identifier == 'PXGGridLayout-Info' AND label BEGINSWITH 'Video,'"))
        XCTAssertGreaterThanOrEqual(videos.count,2)
        tap(videos.element(boundBy:0),"select-video-one")
        tap(videos.element(boundBy:1),"select-video-two")
        tap(app.buttons["Add"].firstMatch,"add-selected-videos")
        let permission = XCUIApplication(bundleIdentifier: "com.apple.springboard").buttons.matching(NSPredicate(format: "label CONTAINS 'Allow' AND NOT label CONTAINS 'Don'")).firstMatch
        tap(permission, "allow-photos")
        let confirm=app.buttons["confirmRecordingImportButton"]
        XCTAssertTrue(confirm.waitForExistence(timeout:20))
        hold("review-video-import")
        tap(confirm,"confirm-video-import")
        XCTAssertTrue(app.buttons["openSourceTimelineButton"].waitForExistence(timeout:15))
        hold("recordings-ready")

        lesson=5
        tap(app.buttons["openSourceTimelineButton"],"open-editor")
        XCTAssertTrue(app.sliders["sourceScrubber"].waitForExistence(timeout:20))
        tap(app.buttons["sourcePlayPauseButton"],"preview-original")
        Thread.sleep(forTimeInterval:2)
        tap(app.buttons["sourcePlayPauseButton"],"pause-original")
        scroll("show-trim-controls")
        slider("clipStartSlider",0.10,"first-clip-start")
        slider("clipEndSlider",0.45,"first-clip-end")
        tap(app.buttons["saveClipButton"],"save-first-clip")
        XCTAssertTrue(app.staticTexts["Available"].firstMatch.waitForExistence(timeout:25))
        slider("clipStartSlider",0.55,"second-clip-start")
        slider("clipEndSlider",0.90,"second-clip-end")
        tap(app.buttons["saveClipButton"],"save-second-clip")
        Thread.sleep(forTimeInterval:2)
        scroll("show-review-clips")
        let stars=app.buttons.matching(NSPredicate(format:"identifier BEGINSWITH %@","favoriteClipListButton-"))
        XCTAssertEqual(stars.count,2)
        tap(stars.element(boundBy:0),"favorite-first-clip")
        XCTAssertEqual(stars.element(boundBy:0).value as? String,"Favorite")
        hold("clip-star-meaning",stars.element(boundBy:0))
        tap(app.navigationBars["Bout Recordings"].buttons["Done"],"close-editor")
        hold("bout-star-meaning",app.images["favoriteBoutDetailIndicator"])
        XCTAssertEqual(app.images["favoriteBoutDetailIndicator"].value as? String,"Favorite")

        lesson=6
        tap(app.buttons["openSourceTimelineButton"],"open-clips-for-delete")
        scroll("find-clips-for-delete")
        scroll("show-clips-for-delete")
        let deletes=app.buttons.matching(NSPredicate(format:"identifier BEGINSWITH %@","deleteReviewClip-"))
        tap(deletes.element(boundBy:0),"delete-first-clip")
        hold("delete-warning",app.buttons["confirmDeleteReviewClipButton"].firstMatch)
        tap(app.buttons["confirmDeleteReviewClipButton"].firstMatch,"confirm-clip-delete")
        XCTAssertEqual(stars.count,1)
        hold("one-clip-remains")
        tap(app.navigationBars["Bout Recordings"].buttons["Done"],"close-after-delete")
        hold("bout-no-favorite",app.images["favoriteBoutDetailIndicator"])
        XCTAssertEqual(app.images["favoriteBoutDetailIndicator"].value as? String,"Not favorite")
        tap(app.navigationBars["Bout Details"].buttons["Cancel"],"close-bout")

        lesson=7
        // iPad sidebar keeps the global Fencer action visible.
        tap(app.buttons["Fencer"],"open-fencer-settings")
        hold("storage-counters",app.staticTexts["localUploadedClipSize"])
        tap(app.buttons["clearLocalClipCopiesButton"],"clear-local-copies")
        hold("storage-warning",app.buttons["confirmClearLocalClipCopiesButton"].firstMatch)
        tap(app.buttons["confirmClearLocalClipCopiesButton"].firstMatch,"confirm-clear-copies")
        hold("storage-result",app.staticTexts["localUploadedClipSize"])
        XCTAssertFalse(app.buttons["clearLocalClipCopiesButton"].isEnabled)
        hold("finish")
        emit("complete","all-seven-lessons")
    }
}
