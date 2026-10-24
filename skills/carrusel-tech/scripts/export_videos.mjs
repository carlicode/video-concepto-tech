#!/usr/bin/env node
// Exporta cada slide de carousel.html como un MP4 vertical 1080x1920 (30 fps, H.264).
// Uso:
//   node export_videos.mjs <carousel.html> <carpetaSalida>            -> un MP4 por slide
//   node export_videos.mjs <carousel.html> <carpetaSalida> --still 3:11  -> solo un PNG de prueba (slide 3, segundo 11)
//   node export_videos.mjs <carousel.html> <carpetaSalida> --only 3     -> re-exporta solo la slide 3
// Lee meta.json (junto al HTML) con duración y desfase de cada slide.
// Requiere: Google Chrome (o CHROME=/ruta), Node >= 22 y ffmpeg.
import {spawn, spawnSync} from 'node:child_process';
import {writeFileSync, readFileSync, mkdirSync, mkdtempSync, rmSync, existsSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, dirname, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const [,, htmlArg, outArg, ...rest] = process.argv;
if (!htmlArg || !outArg) { console.error('Uso: node export_videos.mjs <carousel.html> <carpetaSalida> [--still N:segundo]'); process.exit(1); }
const html = resolve(htmlArg), out = resolve(outArg), FPS = 30;
const meta = JSON.parse(readFileSync(join(dirname(html), 'meta.json'), 'utf8'));
const stillIdx = rest.indexOf('--still');
const still = stillIdx >= 0 ? rest[stillIdx + 1].split(':').map(Number) : null;
const onlyIdx = rest.indexOf('--only');
const only = onlyIdx >= 0 ? Number(rest[onlyIdx + 1]) : null;
mkdirSync(out, {recursive: true});

const chromePaths = [process.env.CHROME, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean);
const chromeBin = chromePaths.find(p => existsSync(p));
if (!chromeBin) { console.error('No encuentro Google Chrome. Define CHROME=/ruta/al/binario'); process.exit(1); }
if (!still && spawnSync('ffmpeg', ['-version']).status !== 0) { console.error('Falta ffmpeg (brew install ffmpeg)'); process.exit(1); }

const work = mkdtempSync(join(tmpdir(), 'carrusel-'));
const port = 9300 + Math.floor(Math.random() * 600);
const chrome = spawn(chromeBin, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${work}/profile`,
  '--hide-scrollbars', '--no-first-run', '--window-size=1080,1920', 'about:blank'], {stdio: 'ignore'});
const sleep = ms => new Promise(r => setTimeout(r, ms));
const cleanup = () => { try { chrome.kill(); } catch {} try { rmSync(work, {recursive: true, force: true}); } catch {} };
process.on('exit', cleanup);

let targets;
for (let i = 0; i < 60; i++) {
  try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (targets.find(t => t.type === 'page')) break; } catch {}
  await sleep(300);
}
if (!targets) { console.error('Chrome no arrancó'); process.exit(1); }
const ws = new WebSocket(targets.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise(r => ws.onopen = r);
let id = 0; const pend = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
const send = (method, params = {}) => new Promise(r => { const i = ++id; pend.set(i, r); ws.send(JSON.stringify({id: i, method, params})); });
const ev = async expr => {
  const r = await send('Runtime.evaluate', {expression: expr, awaitPromise: true, returnByValue: true});
  if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails));
  return r.result?.result?.value;
};

await send('Emulation.setDeviceMetricsOverride', {width: 1080, height: 1920, deviceScaleFactor: 1, mobile: false});
await send('Page.enable');
await send('Page.navigate', {url: pathToFileURL(html).href + '?export=1&s=1'});
await sleep(2500);
await ev('document.fonts.ready.then(()=>1)');
// Controla el tiempo de todas las animaciones CSS. La cabecera (clase .a), la línea del kicker y el fundido de la
// slide se dejan terminados para que el primer cuadro ya muestre el título; solo se anima el contenido.
await ev(`(()=>{
  window.__cur=-1;
  window.__seek=(i,l,g)=>{
    if(window.__cur!==i){go(i);window.__cur=i}
    for(const a of document.getAnimations()){
      a.pause();
      const tg=a.effect&&a.effect.target;
      const bg=tg&&tg.closest&&tg.closest('.bg');
      const ent=tg&&tg.classList&&((a.animationName==='rise'&&tg.classList.contains('a'))||a.animationName==='grow');
      const tr=a.transitionProperty!==undefined;
      a.currentTime=(ent||tr)?30000:(bg?g:l)*1000;
    }
    return 1;
  };
})()`);

const shot = async path => {
  const r = await send('Page.captureScreenshot', {format: 'png'});
  writeFileSync(path, Buffer.from(r.result.data, 'base64'));
};

if (still) {
  const [n, sec] = still;
  await ev(`window.__seek(${n - 1},${sec},${sec})`);
  await sleep(150);
  const p = join(out, `still-${n}.png`);
  await shot(p); console.log(p);
  process.exit(0);
}

let gtime = 0;
for (const s of meta.slides) {
  if (only && s.index !== only) continue;
  const dir = join(work, `s${s.index}`); mkdirSync(dir);
  const frames = Math.round(s.duration * FPS);
  for (let f = 0; f < frames; f++) {
    await ev(`window.__seek(${s.index - 1},${f / FPS + s.offset},${gtime / FPS})`);
    await shot(join(dir, `${String(f).padStart(5, '0')}.png`));
    gtime++;
  }
  const file = join(out, `slide-${s.index}-${s.type}.mp4`);
  const r = spawnSync('ffmpeg', ['-loglevel', 'error', '-y', '-framerate', String(FPS), '-i', join(dir, '%05d.png'),
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-r', String(FPS), file]);
  if (r.status !== 0) { console.error('ffmpeg falló', r.stderr?.toString()); process.exit(1); }
  rmSync(dir, {recursive: true, force: true});
  console.log(`slide ${s.index} (${s.type}) -> ${file} (${s.duration} s)`);
}
process.exit(0);
