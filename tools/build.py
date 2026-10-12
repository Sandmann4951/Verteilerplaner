"""Baut die startfertige App nach app/ aus src/verteilerplaner.html.
Aufruf im Repo-Hauptordner:  python tools/build.py   (benötigt Pillow für die Icons)"""
import os, re, shutil, json, zipfile
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
from PIL import Image, ImageDraw
SRC='src/verteilerplaner.html'; OUT='app'
shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT+'/libs'); os.makedirs(OUT+'/icons')
s=open(SRC,encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,(a[:70],s.count(a)); s=s.replace(a,b)
# local libs first, CDN as fallback
rep('const LIBS={jspdf:"https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js",autotable:"https://cdn.jsdelivr.net/npm/jspdf-autotable@3.8.2/dist/jspdf.plugin.autotable.min.js",xlsx:"https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"};',
    'const LIBS={jspdf:"libs/jspdf.umd.min.js",autotable:"libs/jspdf.plugin.autotable.min.js",xlsx:"libs/xlsx.full.min.js"};')
# normal browser downloads
rep('''async function saveFile(name,data){
  try{ dlP=dlP||(window.claude&&window.claude.use?window.claude.use("downloads"):Promise.resolve(null)); const dl=await dlP;
    if(!dl){toast("Dateien speichern ist in dieser Ansicht nicht verfügbar");return false}
    await dl.save({filename:name,data}); toast(`${name} gespeichert`); return true;''','''async function saveFile(name,data){
  try{ const blob=data instanceof Blob?data:new Blob([data],{type:/\\.json$/.test(name)?"application/json":/\\.csv$/.test(name)?"text/csv;charset=utf-8":"application/octet-stream"});
    const url=URL.createObjectURL(blob); const a=document.createElement("a"); a.href=url; a.download=name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(url),4000);
    toast(`${name} wird heruntergeladen`); return true;''')
head='''<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#0a6a88">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<style>:root{color-scheme:light}body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>
</head>
<body>
'''
tail='''
<script>if("serviceWorker" in navigator&&location.protocol.startsWith("http"))navigator.serviceWorker.register("sw.js").catch(()=>{});</script>
</body>
</html>
'''
open(OUT+'/index.html','w',encoding='utf-8').write(head+s+tail)
for f in ('jspdf.umd.min.js','jspdf.plugin.autotable.min.js','xlsx.full.min.js'): shutil.copy('vendor/'+f,OUT+'/libs/')
# icons: DIN rail with modules
for n in (192,512):
    im=Image.new('RGB',(n,n),(10,106,136)); d=ImageDraw.Draw(im); u=n/16
    d.rounded_rectangle([2*u,2*u,14*u,14*u],radius=u,fill=(230,232,233))
    d.rectangle([2.6*u,7.3*u,13.4*u,8.7*u],fill=(158,164,169))
    for i,c in enumerate([(122,74,30),(27,31,35),(139,144,149),(31,111,209)]):
        x=3.4*u+i*2.4*u; d.rectangle([x,4.2*u,x+2.0*u,11.8*u],fill=(251,251,248),outline=(60,60,60),width=max(1,int(u/6)))
        d.rectangle([x+0.6*u,6.6*u,x+1.4*u,7.6*u],fill=(58,63,68)); d.rectangle([x,4.2*u,x+2.0*u,4.8*u],fill=c)
    im.save(f'{OUT}/icons/icon-{n}.png')
json.dump({"name":"Verteilerplaner","short_name":"Verteilerplaner","start_url":"./index.html","scope":"./","display":"standalone","background_color":"#e6e8e9","theme_color":"#0a6a88","lang":"de",
  "icons":[{"src":"icons/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any maskable"}]},
  open(OUT+'/manifest.webmanifest','w',encoding='utf-8'),ensure_ascii=False,indent=1)
open(OUT+'/sw.js','w').write('''const C="verteilerplaner-v1";
const FILES=["./","index.html","manifest.webmanifest","libs/jspdf.umd.min.js","libs/jspdf.plugin.autotable.min.js","libs/xlsx.full.min.js","icons/icon-192.png","icons/icon-512.png"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES)));self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim()});
/* Netzwerk zuerst (Updates sofort sichtbar), Cache als Offline-Reserve */
self.addEventListener("fetch",e=>{if(e.request.method!=="GET")return;e.respondWith(fetch(e.request).then(r=>{if(r.ok&&new URL(e.request.url).origin===location.origin){const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp))}return r}).catch(()=>caches.match(e.request)))});
''')
ps=r'''# Verteilerplaner - lokaler Webserver (nur dieser Rechner)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Split-Path -Parent $MyInvocation.MyCommand.Path))
$port = 8765
$prefix = "http://localhost:$port/"
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($prefix)
try { $listener.Start() } catch {
  Write-Host "Port $port ist belegt - der Verteilerplaner laeuft vermutlich schon. Browser wird geoeffnet."
  Start-Process $prefix; Start-Sleep -Seconds 3; exit
}
Write-Host ""
Write-Host "  Verteilerplaner laeuft unter $prefix"
Write-Host "  Dieses Fenster offen lassen. Beenden: Fenster schliessen oder Strg+C."
Write-Host ""
Start-Process $prefix
$mime = @{ '.html'='text/html; charset=utf-8'; '.js'='application/javascript; charset=utf-8'; '.json'='application/json'; '.webmanifest'='application/manifest+json'; '.png'='image/png'; '.svg'='image/svg+xml'; '.css'='text/css'; '.ico'='image/x-icon' }
while ($listener.IsListening) {
  $ctx = $listener.GetContext()
  try {
    $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart('/'))
    if ([string]::IsNullOrEmpty($rel)) { $rel = 'index.html' }
    $file = [IO.Path]::GetFullPath((Join-Path $root $rel))
    if ($file.StartsWith($root, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path -LiteralPath $file -PathType Leaf)) {
      $bytes = [IO.File]::ReadAllBytes($file)
      $ext = [IO.Path]::GetExtension($file).ToLower()
      if ($mime.ContainsKey($ext)) { $ctx.Response.ContentType = $mime[$ext] } else { $ctx.Response.ContentType = 'application/octet-stream' }
      $ctx.Response.Headers.Add('Cache-Control','no-cache')
      $ctx.Response.ContentLength64 = $bytes.Length
      $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else { $ctx.Response.StatusCode = 404 }
  } catch { $ctx.Response.StatusCode = 500 }
  finally { $ctx.Response.Close() }
}
'''
open(OUT+'/server.ps1','w',encoding='utf-8-sig',newline='\r\n').write(ps)
open(OUT+'/Verteilerplaner starten.bat','w',encoding='ascii',newline='\r\n').write('@echo off\r\ntitle Verteilerplaner\r\npowershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0server.ps1"\r\n')
open(OUT+'/verteilerplaner-starten.sh','w',newline='\n').write('#!/bin/sh\n# macOS / Linux: startet den Verteilerplaner unter http://localhost:8765\ncd "$(dirname "$0")"\n( sleep 1; (command -v xdg-open >/dev/null && xdg-open http://localhost:8765/) || open http://localhost:8765/ ) >/dev/null 2>&1 &\nexec python3 -m http.server 8765 --bind 127.0.0.1\n')
os.chmod(OUT+'/verteilerplaner-starten.sh',0o755)
open(OUT+'/LIESMICH.txt','w',encoding='utf-8-sig',newline='\r\n').write('''VERTEILERPLANER - lokale Version
================================

Starten (Windows)
  1. Ordner "Verteilerplaner" an einen festen Ort kopieren, z. B. Dokumente.
  2. Doppelklick auf "Verteilerplaner starten.bat".
     Ein schwarzes Fenster zeigt den lokalen Server, der Browser öffnet
     http://localhost:8765 . Das Fenster während der Arbeit offen lassen.
  3. Als App installieren (einmalig): In Edge oder Chrome rechts in der
     Adressleiste auf das Symbol "App installieren" klicken. Danach startet
     der Verteilerplaner in einem eigenen Fenster mit Startmenü-Eintrag.
     Der Server (Schritt 2) muss dafür laufen; offline geht es danach auch,
     solange die App einmal geladen wurde.

Starten (macOS / Linux)
  ./verteilerplaner-starten.sh   (benötigt python3)

Ohne Server
  index.html per Doppelklick öffnen geht auch. Dann klappt aber die
  App-Installation nicht, und die Daten liegen getrennt von denen unter
  localhost.

Daten
  - Projekte und Stammdaten speichert der Browser lokal für die Adresse
    http://localhost:8765 . Anderer Browser oder anderer Port = andere Daten.
  - Regelmäßig sichern: Reiter "Projekt & PDF" -> "Projekt speichern",
    Reiter "Stammdaten" -> "Stammdaten speichern". So überträgst du auch
    Daten aus der Claude-Version in diese lokale Version (Datei speichern,
    hier "Projekt öffnen" bzw. "Stammdaten laden").
  - Browserdaten löschen löscht auch die Projekte. Deshalb die Sicherungen.

Hinweise
  - Der Server lauscht nur auf diesem Rechner (localhost), Kollegen im
    Netzwerk erreichen ihn nicht.
  - Port belegt? In server.ps1 die Zeile "$port = 8765" ändern.
  - Schriften werden ohne Internet durch Systemschriften ersetzt;
    alles andere läuft offline.
''')
# zip zum Weitergeben (nicht im Repo, siehe .gitignore)
os.makedirs('dist',exist_ok=True); zp='dist/Verteilerplaner.zip'
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
    for dp,dn,fn in os.walk(OUT):
        for f in fn:
            full=os.path.join(dp,f); arc=os.path.join('Verteilerplaner',os.path.relpath(full,OUT))
            zi=zipfile.ZipInfo.from_file(full,arc)
            if f.endswith('.sh'): zi.external_attr=(0o755<<16)
            with open(full,'rb') as fh: z.writestr(zi,fh.read(),zipfile.ZIP_DEFLATED)
print('built', OUT, '+', zp, os.path.getsize(zp))
