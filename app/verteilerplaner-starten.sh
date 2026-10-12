#!/bin/sh
# macOS / Linux: startet den Verteilerplaner unter http://localhost:8765
cd "$(dirname "$0")"
( sleep 1; (command -v xdg-open >/dev/null && xdg-open http://localhost:8765/) || open http://localhost:8765/ ) >/dev/null 2>&1 &
exec python3 -m http.server 8765 --bind 127.0.0.1
