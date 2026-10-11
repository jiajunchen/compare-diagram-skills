// Reuse the requested skill's bundled CLI; never print the loaded credentials.
import { existsSync, readFileSync, writeFileSync, mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const directory = resolve(root, 'figures/architecture-video');
const rendererRoot = process.argv[2];
if (!rendererRoot) throw new Error('Pass a checkout of QingYunA/answer-me-with-html as the first argument.');
const cli = resolve(rendererRoot, 'skills/answer-me-with-html/scripts/am.mjs');
if (!existsSync(cli)) throw new Error('The renderer checkout does not contain the bundled skill CLI.');
const envFile = resolve(root, '.env');
if (existsSync(envFile)) process.loadEnvFile(envFile);
process.env.ELEVENLABS_API_KEY ||= process.env.ElevenLab_API;
if (!process.env.ELEVENLABS_API_KEY) throw new Error('An ElevenLabs API key is required in the environment or .env.');
// The upstream fit box caps width at 1100px even when an SVG is wider.
// Measure the uncapped diagram and reserve space for three-line captions.
let renderer = readFileSync(cli, 'utf8');
const fitBefore = 'const s = Math.min(1600 / fit.offsetWidth, 740 / fit.offsetHeight, 3.4);';
const fitAfter = "fit.style.maxWidth = 'none'; const s = Math.min(1560 / fit.offsetWidth, 520 / fit.offsetHeight, 3.4);";
const safeBefore = 'bottom: H - 150';
if (!renderer.includes(fitBefore) || !renderer.includes(safeBefore)) {
  throw new Error('Renderer layout changed; review the compatibility patch before rendering.');
}
renderer = renderer.replace(fitBefore, fitAfter).replace(safeBefore, 'bottom: H - 290');
// Preserve 30 fps while reusing identical frames during static narration holds.
// This renderer animates only around scene and beat boundaries; two seconds
// covers its longest reveal/focus transition for this storyboard.
const loopBefore = 'for (let i = 0; i < frames; i++) {\n      await evaluate(`render(${i / info.fps})`);\n      const { data } = await page("Page.captureScreenshot", { format: "jpeg", quality: 92, clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 } });';
const loopAfter = `const events = await evaluate('JSON.parse(document.getElementById("amv-data").textContent).segments.flatMap(s => [s.start, ...s.beats.flatMap(b => [b.start,b.end])])');
    let heldFrame;
    for (let i = 0; i < frames; i++) {
      const time = i / info.fps;
      if (!heldFrame || events.some(event => time >= event && time < event + 2)) {
        await evaluate('render(' + time + ')');
        const shot = await page("Page.captureScreenshot", { format: "jpeg", quality: 92, clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 } });
        heldFrame = shot.data;
      }
      const data = heldFrame;`;
if (!renderer.includes(loopBefore)) throw new Error('Renderer export loop changed; review frame reuse.');
renderer = renderer.replace(loopBefore, loopAfter);
const temporary = mkdtempSync(resolve(tmpdir(), 'sports-video-render-'));
const patchedCli = resolve(temporary, 'am.mjs');
writeFileSync(patchedCli, renderer);
const args = [patchedCli, 'video', resolve(directory, 'architecture-video.md'), '-o',
  resolve(directory, 'architecture-video.html'), '--voice', 'elevenlabs', '--no-open'];
if (!process.argv.includes('--html-only')) args.push('--mp4');
const child = spawn(process.execPath, args, { cwd: root, env: process.env, stdio: 'inherit' });
child.on('error', () => { console.error('Could not start the renderer.'); process.exitCode = 1; });
child.on('exit', (code) => { rmSync(temporary, { recursive: true, force: true }); process.exitCode = code ?? 1; });
