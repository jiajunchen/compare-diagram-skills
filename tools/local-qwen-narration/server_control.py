"""Start, inspect, or stop this task's loopback-only MLX Audio server."""

import sys as _sys
from pathlib import Path as _Path
_sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
from layout import FIGURES, REPO, QWEN, TOOLS, assets, runtime

from pathlib import Path
import subprocess,os,json,sys,time,urllib.request,signal,socket
H=(FIGURES / 'local-qwen-narration');C=runtime('local-qwen-narration');C.mkdir(exist_ok=True);STATE=C/'server.json';PORT=8765
cmd=[str(QWEN/'.venv/bin/python'),'-m','mlx_audio.server','--host','127.0.0.1','--port',str(PORT),'--tts-max-batch-size','1','--allowed-origins',f'http://127.0.0.1:{PORT}',f'http://localhost:{PORT}','--log-dir',str(C/'logs')]
def status():
 try:
  with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/v1/models',timeout=3) as r:return json.load(r)
 except Exception:return None
mode=sys.argv[1] if len(sys.argv)>1 else 'status'
if mode=='start':
 if status() is not None:print('Server already responds on localhost:8765');sys.exit(0)
 with socket.socket() as s:s.bind(('127.0.0.1',PORT))
 env={**os.environ,'HF_HOME':str(QWEN/'huggingface'),'HF_HUB_DISABLE_TELEMETRY':'1','TOKENIZERS_PARALLELISM':'false','PYTHONUNBUFFERED':'1'}
 with (C/'server.log').open('a') as log:
  p=subprocess.Popen(cmd,cwd=H,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 STATE.write_text(json.dumps({'pid':p.pid,'port':PORT,'command':cmd},indent=2)+'\n')
 for _ in range(60):
  if status() is not None:print(f'Server ready: http://127.0.0.1:{PORT}/docs (PID {p.pid})');break
  if p.poll() is not None:raise RuntimeError('Server exited; inspect .runtime/figures/local-qwen-narration/server.log')
  time.sleep(.5)
 else:raise RuntimeError('Server startup timed out; inspect .runtime/figures/local-qwen-narration/server.log')
elif mode=='stop':
 state=json.loads(STATE.read_text());pid=state['pid'];actual=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout
 if 'mlx_audio.server' not in actual or str(PORT) not in actual:raise RuntimeError('Saved PID is not this server; no process stopped.')
 os.kill(pid,signal.SIGTERM);print('Local Qwen server stopped.')
elif mode=='status':print(json.dumps({'server':status(),'process':json.loads(STATE.read_text()) if STATE.exists() else None},indent=2))
else:raise SystemExit('Use start, status, or stop.')
