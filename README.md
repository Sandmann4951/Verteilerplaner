# Verteilerplaner

Webanwendung zum grafischen Planen von Elektro-Unterverteilungen: Geräte mit
Hersteller-Artikelnummern auf Hutschienen setzen (1 TE = 18 mm, 12 TE je Feld),
Klemmen verdrahten, Phasenschienen und Hauptleitungsklemmen einfügen, Schrank
auswählen und die komplette Dokumentation als PDF ausgeben.

## Funktionen

- Aufbau in Reihen mit „+“-Plätzen, Papierkorb, Eigenschaften-Seitenleiste
- Phasenschienen, Steckbrücken, Hauptleitungsklemmen (HLAK)
- Auto-Verdrahtung nach festen Regeln: Zuleitung und Phasenschienen unten,
  Abgänge oben; LS hängen am FI links davon; X1 nur für externe Kabel,
  X2 nur für interne N/PE; interne Verbraucher direkt vom LS bzw. Netzteil
- Querschnittsprüfung (Absicherung, Klemmengröße, Vorsicherung), Kurzschlussprüfung
- Stromkreise mit Namen am LS, Leitung automatisch aus Polzahl und N
- Schrankauswahl (Hager, Striebel & John, Hensel) inkl. Feldverteiler,
  Platzbedarf mit Reserve, Warnung bei zu kleinem Schrank
- Stückliste mit Drahtmetern, Kunden- und interner Ansicht (EK)
- Stammdaten mit Preisen, Import per EAN, manuell oder CSV/Excel
- PDF: Deckblatt mit Schriftfeld, maßstäblicher Aufbauplan, Stromlaufplan,
  Stückliste, Stromkreis-, Klemmen- und Verdrahtungsliste

Projekte und Stammdaten liegen im Browser (localStorage) und lassen sich als
Datei speichern und laden.

## Ordner

| Ordner | Inhalt |
|---|---|
| `src/verteilerplaner.html` | Quellcode – hier wird entwickelt (eine Datei, HTML/CSS/JS) |
| `app/` | Startfertige lokale Version, erzeugt mit `tools/build.py` |
| `vendor/` | Bibliotheken für den Offline-Betrieb (jsPDF 2.5.1, jsPDF-AutoTable 3.8.2, SheetJS 0.18.5) |
| `tools/build.py` | Baut `app/` und `dist/Verteilerplaner.zip` |
| `tests/smoke.mjs` | Rauchtest: Auto-Verdrahtung und PDF-Export |

## Starten

Windows: Ordner `app` kopieren, `Verteilerplaner starten.bat` doppelklicken,
der Browser öffnet <http://localhost:8765>. Details in `app/LIESMICH.txt`.

## Entwickeln

```
python tools/build.py          # app/ neu bauen (Pillow für die Icons)
npm i playwright               # einmalig
node tests/smoke.mjs           # Rauchtest
```

Nach jeder Änderung an `src/` die App neu bauen und `app/` mit committen,
damit der Stand im Repo direkt lauffähig ist.

## Hinweis

Gehäusedaten und Preise stammen aus Herstellerkatalogen und Händlerangaben
(Stand 10/2026) und sind als Beispielpreise markiert. Vor Bestellung prüfen.
Die Planung ersetzt keine Prüfung nach DIN VDE / DIN EN 61439.
