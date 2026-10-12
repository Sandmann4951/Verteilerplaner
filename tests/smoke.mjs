// Rauchtest: lädt die App, führt Auto-Verdrahtung aus und erzeugt ein PDF.
// Aufruf:  npm i playwright  &&  node tests/smoke.mjs   (nach python tools/build.py)
import { chromium } from 'playwright';
import { createServer } from 'http';
import { readFileSync, existsSync, mkdirSync } from 'fs';
import { join, extname, dirname } from 'path';
import { fileURLToPath } from 'url';
const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', 'app');
const MIME = { '.html':'text/html; charset=utf-8', '.js':'application/javascript', '.json':'application/json', '.webmanifest':'application/manifest+json', '.png':'image/png' };
const srv = createServer((q, r) => { const f = join(ROOT, decodeURIComponent(q.url.split('?')[0]).replace(/^\/$/, '/index.html'));
  if (!f.startsWith(ROOT) || !existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { 'Content-Type': MIME[extname(f)] || 'application/octet-stream' }); r.end(readFileSync(f)); }).listen(8766);
const opts = process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {};
const b = await chromium.launch(opts);
const ctx = await b.newContext({ acceptDownloads: true }); const pg = await ctx.newPage();
const errs = []; pg.on('pageerror', e => errs.push(e.stack));
await pg.route('**/*', r => /localhost:8766/.test(r.request().url()) ? r.continue() : r.abort());
await pg.goto('http://localhost:8766/'); await pg.waitForTimeout(600);
const res = await pg.evaluate(() => { autoAll(); return { rows: state.rows.length, wires: state.wires.length, circuits: state.circuits.length, checks: checks().map(c => c.lvl + ': ' + c.t) }; });
console.log(res);
await pg.evaluate(() => { ui.tab = 'proj'; ui.menuOpen = true; renderTab(); });
const [dl] = await Promise.all([pg.waitForEvent('download', { timeout: 20000 }), pg.click('[data-pdfgo="int"]')]);
mkdirSync(join(ROOT, '..', 'tests', 'out'), { recursive: true });
await dl.saveAs(join(ROOT, '..', 'tests', 'out', 'beispiel.pdf'));
console.log('PDF:', dl.suggestedFilename());
await b.close(); srv.close();
if (errs.length || !res.wires) { console.error('FEHLER', errs); process.exit(1); }
console.log('OK');
