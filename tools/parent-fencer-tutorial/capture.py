"""Run the tutorial-only UI harness without modifying the app project or tests."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import os,shutil,subprocess,json,time,signal,re
HERE=(FIGURES / 'parent-fencer-tutorial');ROOT=HERE.parent.parent
SIM='ECE7004E-982A-4528-B7A4-1E5ABC046C8A'
env={**os.environ,'DEVELOPER_DIR':'/Volumes/MacMiniEx/Applications/Xcode.app/Contents/Developer'}
cache=runtime('parent-fencer-tutorial');cache.mkdir(exist_ok=True)
project=cache/'FencingVideoAnalysis.xcodeproj'
shutil.copytree(ROOT/'FencingVideoAnalysis.xcodeproj',project,dirs_exist_ok=True)
p=project/'project.pbxproj';s=p.read_text().replace('projectDirPath = "";',f'projectDirPath = "{ROOT}";')
s=s.replace('path = LaunchTests.swift; sourceTree = "<group>";',f'path = "{(TOOLS / 'parent-fencer-tutorial/CaptureTests.swift')}"; sourceTree = "<absolute>";')
p.write_text(s)
if os.environ.get('TUTORIAL_RESUME_STORE'):
 harness=((TOOLS / 'parent-fencer-tutorial/CaptureTests.swift')).read_text().replace('UUID().uuidString', '"'+os.environ['TUTORIAL_RESUME_STORE']+'"')
 start=harness.index('        XCTAssertTrue(app.textFields["fencerNameField"]')
 end=harness.index('        lesson=6',start)
 prep='        XCTAssertTrue(app.staticTexts["Autumn Practice Open"].firstMatch.waitForExistence(timeout:20))\n        app.staticTexts["Autumn Practice Open"].firstMatch.tap()\n        XCTAssertTrue(app.buttons["openBoutDetailButton-1"].waitForExistence(timeout:10))\n        app.buttons["openBoutDetailButton-1"].tap()\n        let stars=app.buttons.matching(NSPredicate(format:"identifier BEGINSWITH %@","favoriteClipListButton-"))\n        step=46\n'
 harness=harness[:start]+prep+harness[end:]
 target=cache/'ResumeCaptureTests.swift';target.write_text(harness)
 p.write_text(p.read_text().replace(str((TOOLS / 'parent-fencer-tutorial/CaptureTests.swift')),str(target)))
cmd=['xcodebuild','-project',str(project),'-scheme','FencingVideoAnalysis','-configuration','Test','-destination','platform=iOS Simulator,id='+SIM,'-derivedDataPath',str(ROOT/'build/TutorialCaptureData'),'-parallel-testing-enabled','NO','-only-testing:FencingVideoAnalysisUITests/TutorialCaptureTests/testRecordSevenLessons','CODE_SIGNING_ALLOWED=NO','test']
recordings=assets('parent-fencer-tutorial') / 'recordings';recordings.mkdir(exist_ok=True)
raw=recordings/'capture.mov';log=cache/'capture.log';videoLog=cache/'video.log'
with videoLog.open('w') as vf,log.open('w') as lf:
 start=time.time()
 recorder=subprocess.Popen(['xcrun','simctl','io',SIM,'recordVideo','--codec=h264','--force',str(raw)],env=env,stdout=vf,stderr=vf)
 (assets('parent-fencer-tutorial') / 'recording-clock.json').write_text(json.dumps({'hostStart':start,'simulator':SIM},indent=2))
 try:
  result=subprocess.Popen(cmd,env=env,stdout=lf,stderr=subprocess.STDOUT)
  granted=False
  while result.poll() is None:
   if not granted and 'TUTORIAL_READY_FOR_PHOTOS' in log.read_text():
    subprocess.run(['xcrun','simctl','privacy',SIM,'reset','photos','com.example.FencingVideoAnalysis'],env=env,check=True)
    granted=True
   time.sleep(.5)
 finally:
  recorder.send_signal(signal.SIGINT);recorder.wait(timeout=30)
 events=[]
 for line in log.read_text().splitlines():
  if 'TUTORIAL_EVENT ' in line:
   events.append(json.loads(line.split('TUTORIAL_EVENT ',1)[1]))
 (HERE/'capture-events.json').write_text(json.dumps(events,indent=2)+'\n')
 print(f'UI capture exit {result.returncode}; {len(events)} events; log {log}')
 if result.returncode:print('\n'.join(log.read_text().splitlines()[-25:]))
 raise SystemExit(result.returncode)
