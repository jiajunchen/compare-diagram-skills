# Production function declaration index

267 declarations in 29 Swift files. Generated from the current source tree.
The [object call graph](graphviz/02b_object_calls.svg) shows the cross-component calls; this index includes internal helpers, view actions, protocol requirements, and fakes.

## `FencingVideoAnalysis/App/AppEntry/AppDependencies.swift`

- [`make`](../FencingVideoAnalysis/App/AppEntry/AppDependencies.swift#L48)
- [`syntheticDocument`](../FencingVideoAnalysis/App/AppEntry/AppDependencies.swift#L134)

## `FencingVideoAnalysis/App/AppEntry/AppViewModel.swift`

- [`load`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L126)
- [`refreshCloud`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L161)
- [`saveFencerName`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L184)
- [`saveTournament`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L200)
- [`selectTournament`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L229)
- [`deleteTournament`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L234)
- [`addBout`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L267)
- [`updateConfirmedBout`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L285)
- [`isBoutFavorite`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L320)
- [`refreshFavoriteBoutIDs`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L322)
- [`deleteConfirmedBout`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L327)
- [`confirmSchedule`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L346)
- [`prepareRecordings`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L409)
- [`confirmRecordings`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L413)
- [`discardRecordings`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L420)
- [`sourceRecordings`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L424)
- [`localSourceURL`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L428)
- [`sourceAsset`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L432)
- [`connectPhotos`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L436)
- [`moveRecording`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L468)
- [`removeRecording`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L472)
- [`mediaStatus`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L480)
- [`createClip`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L484)
- [`retryClip`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L493)
- [`retryUpload`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L503)
- [`deleteClip`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L505)
- [`synchronizeDeletion`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L516)
- [`reviewClips`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L525)
- [`unloadBoutClips`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L529)
- [`localUploadedClipBytes`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L533)
- [`clearLocalClipCopies`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L537)
- [`toggleClipFavorite`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L541)
- [`playableURL`](../FencingVideoAnalysis/App/AppEntry/AppViewModel.swift#L563)

## `FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift`

- [`move`](../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift#L156)
- [`remove`](../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift#L166)
- [`refreshRecordings`](../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift#L179)
- [`save`](../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift#L187)
- [`delete`](../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift#L200)
- [`body`](../FencingVideoAnalysis/Features/Bouts/BoutDetailView.swift#L247)

## `FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift`

- [`load`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L158)
- [`openCurrent`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L165)
- [`movePrevious`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L184)
- [`moveNext`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L189)
- [`finishCurrentClip`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L194)
- [`unloadClips`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L202)
- [`timeLabel`](../FencingVideoAnalysis/Features/Bouts/BoutPlayerView.swift#L219)

## `FencingVideoAnalysis/Features/Bouts/RecordingImportReviewView.swift`

- [`prepare`](../FencingVideoAnalysis/Features/Bouts/RecordingImportReviewView.swift#L101)
- [`confirm`](../FencingVideoAnalysis/Features/Bouts/RecordingImportReviewView.swift#L127)
- [`cancel`](../FencingVideoAnalysis/Features/Bouts/RecordingImportReviewView.swift#L142)

## `FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift`

- [`load`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L211)
- [`toggleFavorite`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L222)
- [`select`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L227)
- [`saveClip`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L242)
- [`retry`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L261)
- [`delete`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L274)
- [`play`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L283)
- [`timeLabel`](../FencingVideoAnalysis/Features/Bouts/SourceTimelineView.swift#L297)

## `FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift`

- [`loadScreenshots`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L156)
- [`startManual`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L175)
- [`extract`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L180)
- [`confirm`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L186)
- [`sampleScreenshotData`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L196)
- [`controls`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L381)
- [`magnify`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L423)
- [`pan`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L433)
- [`setZoom`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L447)
- [`resetZoom`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L452)
- [`bounded`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleImportView.swift#L459)

## `FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift`

- [`isRelevant`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L42)
- [`reset`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L69)
- [`extract`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L76)
- [`addDraft`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L116)
- [`removeDraft`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L121)
- [`moveDraft`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L126)
- [`moveDrafts`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L132)
- [`message`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L136)
- [`message`](../FencingVideoAnalysis/Features/ScheduleImport/ScheduleReviewViewModel.swift#L150)

## `FencingVideoAnalysis/Features/Settings/FencerSettingsView.swift`

- [`clearLocalCopies`](../FencingVideoAnalysis/Features/Settings/FencerSettingsView.swift#L81)
- [`refreshLocalStorage`](../FencingVideoAnalysis/Features/Settings/FencerSettingsView.swift#L92)

## `FencingVideoAnalysis/Features/Tournaments/TournamentDetailView.swift`

- [`mediaSummary`](../FencingVideoAnalysis/Features/Tournaments/TournamentDetailView.swift#L104)

## `FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift`

- [`saveChanges`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L28)
- [`saveChanges`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L55)
- [`makeContainer`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L60)
- [`saveChanges`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L96)
- [`tournaments`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L100)
- [`bouts`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L107)
- [`sourceRecordings`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L116)
- [`reviewClips`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L123)
- [`deleteTournament`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L136)
- [`deleteBout`](../FencingVideoAnalysis/Models/LocalModels/LocalRepository.swift#L146)

## `FencingVideoAnalysis/Services/BoutImportCoordinator.swift`

- [`prepareSelections`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L45)
- [`confirm`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L55)
- [`discard`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L85)
- [`requestPhotoAccess`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L89)
- [`linkPendingCloudPhotos`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L92)
- [`localCopy`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L120)
- [`sourceAsset`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L133)
- [`move`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L164)
- [`remove`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L187)
- [`status`](../FencingVideoAnalysis/Services/BoutImportCoordinator.swift#L201)

## `FencingVideoAnalysis/Services/BoutPlaybackQueue.swift`

- [`select`](../FencingVideoAnalysis/Services/BoutPlaybackQueue.swift#L23)
- [`previous`](../FencingVideoAnalysis/Services/BoutPlaybackQueue.swift#L28)
- [`next`](../FencingVideoAnalysis/Services/BoutPlaybackQueue.swift#L35)
- [`didFinishCurrentClip`](../FencingVideoAnalysis/Services/BoutPlaybackQueue.swift#L42)

## `FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift`

- [`cachedURL`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L63)
- [`store`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L75)
- [`clear`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L104)
- [`remove`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L113)
- [`fileURL`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L122)
- [`persist`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L124)
- [`resolve`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L142)
- [`clearCache`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L176)
- [`removeCachedCopies`](../FencingVideoAnalysis/Services/ClipDownloadCoordinator.swift#L178)

## `FencingVideoAnalysis/Services/ClipUploadQueue.swift`

- [`resumePending`](../FencingVideoAnalysis/Services/ClipUploadQueue.swift#L21)
- [`upload`](../FencingVideoAnalysis/Services/ClipUploadQueue.swift#L28)
- [`retry`](../FencingVideoAnalysis/Services/ClipUploadQueue.swift#L60)
- [`deleteCloudCopyIfNeeded`](../FencingVideoAnalysis/Services/ClipUploadQueue.swift#L72)
- [`setStatus`](../FencingVideoAnalysis/Services/ClipUploadQueue.swift#L88)
- [`isTemporaryCloudFailure`](../FencingVideoAnalysis/Services/ClipUploadQueue.swift#L94)

## `FencingVideoAnalysis/Services/ClipWorkflow.swift`

- [`createClip`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L55)
- [`retry`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L81)
- [`delete`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L100)
- [`clips`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L117)
- [`unloadUploadedClips`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L121)
- [`localExportBytes`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L152)
- [`clearLocalClipCopies`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L159)
- [`managedExportFiles`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L205)
- [`isManagedExportPath`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L216)
- [`removeAbandonedFiles`](../FencingVideoAnalysis/Services/ClipWorkflow.swift#L225)

## `FencingVideoAnalysis/Services/CloudAssetService.swift`

- [`saveExportedClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L10)
- [`downloadClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L11)
- [`deleteClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L12)
- [`failNextSave`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L19)
- [`saveExportedClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L21)
- [`downloadClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L29)
- [`deleteClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L38)
- [`saveExportedClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L50)
- [`downloadClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L59)
- [`deleteClip`](../FencingVideoAnalysis/Services/CloudAssetService.swift#L68)

## `FencingVideoAnalysis/Services/CloudKitAssetSpikeService.swift`

- [`roundTrip`](../FencingVideoAnalysis/Services/CloudKitAssetSpikeService.swift#L12)

## `FencingVideoAnalysis/Services/CloudMetadataService.swift`

- [`message`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L37)
- [`synchronize`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L47)
- [`synchronizeDeletions`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L48)
- [`queueDeletion`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L49)
- [`synchronize`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L53)
- [`synchronizeDeletions`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L54)
- [`synchronize`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L68)
- [`queueDeletion`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L83)
- [`staleRecordNames`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L92)
- [`knownRecordIDs`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L98)
- [`append`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L100)
- [`pendingRecords`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L114)
- [`markSynchronized`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L167)
- [`apply`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L188)
- [`shouldApply`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L306)
- [`encode`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L312)
- [`decode`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L313)
- [`make`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L323)
- [`decode`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L334)
- [`record`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L356)
- [`remember`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L367)
- [`forget`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L377)
- [`persist`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L384)
- [`useDownloadCoordinator`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L425)
- [`synchronize`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L430)
- [`synchronizeDeletions`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L453)
- [`reconcileEntireZone`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L466)
- [`reconcileKnownRecords`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L506)
- [`queueDeletion`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L530)
- [`scheduleSync`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L539)
- [`nextRecordZoneChangeBatch`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L554)
- [`handleEvent`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L573)
- [`removeLocalRecord`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L660)
- [`remove`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L671)
- [`deleteLocalRecord`](../FencingVideoAnalysis/Services/CloudMetadataService.swift#L680)

## `FencingVideoAnalysis/Services/DocumentRecognitionService.swift`

- [`addingQualityWarnings`](../FencingVideoAnalysis/Services/DocumentRecognitionService.swift#L62)
- [`recognize`](../FencingVideoAnalysis/Services/DocumentRecognitionService.swift#L86)
- [`recognize`](../FencingVideoAnalysis/Services/DocumentRecognitionService.swift#L90)
- [`recognize`](../FencingVideoAnalysis/Services/DocumentRecognitionService.swift#L178)

## `FencingVideoAnalysis/Services/ICloudSyncStatusService.swift`

- [`accountStatus`](../FencingVideoAnalysis/Services/ICloudSyncStatusService.swift#L9)
- [`accountStatus`](../FencingVideoAnalysis/Services/ICloudSyncStatusService.swift#L18)
- [`accountStatus`](../FencingVideoAnalysis/Services/ICloudSyncStatusService.swift#L38)

## `FencingVideoAnalysis/Services/OnDeviceModelService.swift`

- [`propose`](../FencingVideoAnalysis/Services/OnDeviceModelService.swift#L88)
- [`propose`](../FencingVideoAnalysis/Services/OnDeviceModelService.swift#L93)
- [`promptData`](../FencingVideoAnalysis/Services/OnDeviceModelService.swift#L124)
- [`propose`](../FencingVideoAnalysis/Services/OnDeviceModelService.swift#L157)

## `FencingVideoAnalysis/Services/PhotoLibraryService.swift`

- [`importSelections`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L129)
- [`requestPhotoAccess`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L130)
- [`localIdentifierForExistingRecording`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L131)
- [`cloudIdentifiers`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L133)
- [`copyFromICloudPhotos`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L134)
- [`videoAsset`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L135)
- [`removeWorkingFiles`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L136)
- [`removeWorkingFile`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L137)
- [`importSelections`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L152)
- [`cloudIdentifiers`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L225)
- [`localIdentifierForExistingRecording`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L237)
- [`copyFromICloudPhotos`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L260)
- [`videoAsset`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L299)
- [`requestPhotoAccessFromSystem`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L324)
- [`requestPhotoAccess`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L331)
- [`removeWorkingFiles`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L335)
- [`removeWorkingFile`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L341)
- [`importSelections`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L363)
- [`removeWorkingFiles`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L394)
- [`cloudIdentifiers`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L403)
- [`requestPhotoAccess`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L408)
- [`localIdentifierForExistingRecording`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L410)
- [`copyFromICloudPhotos`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L416)
- [`videoAsset`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L429)
- [`removeWorkingFile`](../FencingVideoAnalysis/Services/PhotoLibraryService.swift#L436)

## `FencingVideoAnalysis/Services/PlaybackState.swift`

- [`open`](../FencingVideoAnalysis/Services/PlaybackState.swift#L10)
- [`seek`](../FencingVideoAnalysis/Services/PlaybackState.swift#L18)
- [`setPlaying`](../FencingVideoAnalysis/Services/PlaybackState.swift#L22)
- [`setSpeed`](../FencingVideoAnalysis/Services/PlaybackState.swift#L24)
- [`open`](../FencingVideoAnalysis/Services/PlaybackState.swift#L48)
- [`open`](../FencingVideoAnalysis/Services/PlaybackState.swift#L52)
- [`play`](../FencingVideoAnalysis/Services/PlaybackState.swift#L61)
- [`pause`](../FencingVideoAnalysis/Services/PlaybackState.swift#L66)
- [`seek`](../FencingVideoAnalysis/Services/PlaybackState.swift#L71)
- [`scrub`](../FencingVideoAnalysis/Services/PlaybackState.swift#L77)
- [`finishScrub`](../FencingVideoAnalysis/Services/PlaybackState.swift#L84)
- [`playerTimeDidChange`](../FencingVideoAnalysis/Services/PlaybackState.swift#L94)
- [`setSpeed`](../FencingVideoAnalysis/Services/PlaybackState.swift#L98)
- [`stop`](../FencingVideoAnalysis/Services/PlaybackState.swift#L103)

## `FencingVideoAnalysis/Services/ScheduleParsingService.swift`

- [`parse`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L63)
- [`parse`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L67)
- [`mapping`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L237)
- [`cell`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L278)
- [`context`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L282)
- [`capture`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L305)
- [`normalizedHeader`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L314)
- [`normalizedName`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L318)
- [`numericValue`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L326)
- [`normalizedStrip`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L334)
- [`normalizedTime`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L338)
- [`normalizedPhase`](../FencingVideoAnalysis/Services/ScheduleParsingService.swift#L347)

## `FencingVideoAnalysis/Services/ScheduleProposalValidator.swift`

- [`reconcile`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L26)
- [`mergeString`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L126)
- [`mergeInt`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L160)
- [`trace`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L187)
- [`headerAllows`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L246)
- [`sourceRow`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L268)
- [`sameBout`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L281)
- [`warning`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L298)
- [`normalized`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L304)
- [`normalizedDigits`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L311)
- [`validTime`](../FencingVideoAnalysis/Services/ScheduleProposalValidator.swift#L317)

## `FencingVideoAnalysis/Services/ScheduleSourceService.swift`

- [`screenshots`](../FencingVideoAnalysis/Services/ScheduleSourceService.swift#L22)
- [`manual`](../FencingVideoAnalysis/Services/ScheduleSourceService.swift#L23)
- [`screenshots`](../FencingVideoAnalysis/Services/ScheduleSourceService.swift#L28)
- [`manual`](../FencingVideoAnalysis/Services/ScheduleSourceService.swift#L33)
- [`screenshots`](../FencingVideoAnalysis/Services/ScheduleSourceService.swift#L38)
- [`manual`](../FencingVideoAnalysis/Services/ScheduleSourceService.swift#L43)

## `FencingVideoAnalysis/Services/VideoEditingService.swift`

- [`validate`](../FencingVideoAnalysis/Services/VideoEditingService.swift#L10)
- [`cancel`](../FencingVideoAnalysis/Services/VideoEditingService.swift#L45)
- [`export`](../FencingVideoAnalysis/Services/VideoEditingService.swift#L50)
- [`export`](../FencingVideoAnalysis/Services/VideoEditingService.swift#L66)
- [`export`](../FencingVideoAnalysis/Services/VideoEditingService.swift#L110)

## `FencingVideoAnalysis/Services/VisualScrubCoordinator.swift`

- [`seek`](../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift#L6)
- [`seek`](../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift#L13)
- [`drag`](../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift#L35)
- [`finish`](../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift#L41)
- [`cancel`](../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift#L48)
- [`startWorkerIfNeeded`](../FencingVideoAnalysis/Services/VisualScrubCoordinator.swift#L56)
