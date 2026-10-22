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
// Szenario 2: 16 FI/LS mit eigener Zuleitung (ohne HLAK), Klemmen X0/X1 und Reihenumbruch
const res2 = await pg.evaluate(() => { const keep = JSON.stringify(state);
  state = normalize({ name: 'Test Wallboxen', pitch: 125, rows: [{ te: 12, items: [] }], wires: [], buses: [], circuits: [] });
  state.auto.outCs = { '16': '4', '32': '6' };
  for (let i = 0; i < 16; i++) state.rows[0].items.push(mkItem(i < 8 ? 'ADZ316D' : 'ADX432D'));
  autoAll(); const T = topo();
  const r = { singles: T.singles.length, x0: state.rows.flatMap(r => r.items).filter(i => i.role === 'feed').length, over: state.rows.filter(r => usedMm(r) > r.te * TE + 0.01).length, cs: [...new Set(state.circuits.map(c => c.cs))].join('/'), bad: checks().filter(c => c.lvl === 'bad').length };
  state = normalize(JSON.parse(keep)); render(); return r; });
console.log(res2);
if (res2.singles !== 16 || res2.x0 !== 80 || res2.over || res2.cs !== '4/6' || res2.bad) { console.error('FEHLER Szenario 2', res2); process.exit(1); }
await pg.evaluate(() => { ui.tab = 'proj'; ui.menuOpen = true; renderTab(); });
const [dl] = await Promise.all([pg.waitForEvent('download', { timeout: 20000 }), pg.click('[data-pdfgo="int"]')]);
mkdirSync(join(ROOT, '..', 'tests', 'out'), { recursive: true });
await dl.saveAs(join(ROOT, '..', 'tests', 'out', 'beispiel.pdf'));
console.log('PDF:', dl.suggestedFilename());
await b.close(); srv.close();
if (errs.length || !res.wires) { console.error('FEHLER', errs); process.exit(1); }
console.log('OK');
