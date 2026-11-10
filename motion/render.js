// Renders motion/index.html frame-by-frame with Playwright and pipes frames to ffmpeg.
// Usage:
//   node render.js stills 1.5 6 12        -> PNG stills in ./stills
//   node render.js video out.mp4 [workers] -> silent H.264 video (30 fps, 1080x1920)
const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');
const { chromium } = require('playwright');

const ROOT = __dirname;
const FPS = 30;
const DURATION = 49.4;
const MIME = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.png': 'image/png', '.woff2': 'font/woff2', '.mp3': 'audio/mpeg' };

function serve() {
  return new Promise(res => {
    const srv = http.createServer((req, rsp) => {
      const f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]).replace(/^\/+/, '') || 'index.html');
      if (!f.startsWith(ROOT) || !fs.existsSync(f)) { rsp.writeHead(404); return rsp.end(); }
      rsp.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
      fs.createReadStream(f).pipe(rsp);
    }).listen(0, '127.0.0.1', () => res(srv));
  });
}

async function openPage(browser, port) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(`http://127.0.0.1:${port}/index.html`);
  await page.evaluate(() => window.setup());
  await page.waitForTimeout(300);
  return page;
}

async function renderRange(browser, port, f0, f1, outFile) {
  const page = await openPage(browser, port);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-r', String(FPS), outFile], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = f0; f < f1; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: 'jpeg', quality: 94 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`${path.basename(outFile)} frame ${f}/${f1}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await page.close();
}

(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const srv = await serve();
  const port = srv.address().port;
  const browser = await chromium.launch({ args: ['--disable-gpu-vsync', '--force-color-profile=srgb'] });
  if (mode === 'stills') {
    fs.mkdirSync(path.join(ROOT, 'stills'), { recursive: true });
    const page = await openPage(browser, port);
    for (const a of args) {
      const t = parseFloat(a);
      await page.evaluate(t => window.render(t), t);
      await page.screenshot({ path: path.join(ROOT, 'stills', `t${t.toFixed(2)}.png`) });
    }
  } else {
    const out = path.resolve(args[0] || 'video.mp4');
    const workers = parseInt(args[1] || '3', 10);
    const total = Math.ceil(DURATION * FPS);
    const per = Math.ceil(total / workers);
    const parts = [];
    const jobs = [];
    for (let w = 0; w < workers; w++) {
      const f0 = w * per, f1 = Math.min(total, f0 + per);
      const part = `${out}.part${w}.mp4`;
      parts.push(part);
      jobs.push(renderRange(browser, port, f0, f1, part));
    }
    await Promise.all(jobs);
    const list = `${out}.list.txt`;
    fs.writeFileSync(list, parts.map(p => `file '${p}'`).join('\n'));
    await new Promise(r => spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy', out], { stdio: 'inherit' }).on('close', r));
    parts.forEach(p => fs.unlinkSync(p)); fs.unlinkSync(list);
    console.log('wrote', out);
  }
  await browser.close();
  srv.close();
})();
