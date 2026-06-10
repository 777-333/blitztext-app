# Windows Blitztext Alternative

Dieses Mini-Tool ist eine Windows-Alternative zum macOS-only Blitztext-Projekt.

## Features

- Globaler Hotkey `F8` zum Starten/Stoppen der Aufnahme
- Transkription mit OpenAI `whisper-1` oder lokal mit `faster-whisper`
- Optionales Text-Rewriting mit `gpt-4o-mini`
- Ergebnis landet in der Zwischenablage
- Optional: automatisches Einfuegen per `Ctrl+V`

## Voraussetzungen

- Windows 10/11
- Python 3.10+
- OpenAI API Key

## Installation

Im Projektordner ausfuehren:

```powershell
cd windows-blitztext
../.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Wenn du die lokale venv aus dem Repo nicht nutzen willst:

```powershell
python -m pip install -r requirements.txt
```

## API Key setzen (PowerShell)

Nur fuer das aktuelle Terminal:

```powershell
$env:OPENAI_API_KEY="dein_key_hier"
```

Permanent fuer dein Benutzerprofil:

```powershell
setx OPENAI_API_KEY "dein_key_hier"
```

Danach neues Terminal oeffnen.

## Start

Ohne Rewriting:

```powershell
../.venv/Scripts/python.exe app.py
```

Offline ohne OpenAI (lokale Transkription):

```powershell
../.venv/Scripts/python.exe app.py --offline --offline-model small
```

Hinweis zu Offline-Modellen:

- Gueltige Groessen sind typischerweise: `tiny`, `base`, `small`, `medium`, `large-v3`
- Beim ersten Start wird das Modell automatisch heruntergeladen
- Offline-Modus braucht keinen OpenAI API Key

Mit Rewriting:

```powershell
../.venv/Scripts/python.exe app.py --rewrite
```

Offline + Rewriting (Hybrid):

```powershell
../.venv/Scripts/python.exe app.py --offline --rewrite
```

Dabei bleibt die Transkription lokal, nur der Rewrite nutzt OpenAI.

Mit Rewriting und Auto-Paste:

```powershell
../.venv/Scripts/python.exe app.py --rewrite --auto-paste
```

## Bedienung

- `F8`: Aufnahme Start/Stop
- `ESC`: App beenden

Nach dem Stoppen wird das Ergebnis transkribiert und in die Zwischenablage kopiert.

## Doppelklick-Start (ohne Terminal)

Im Ordner `windows-blitztext` gibt es jetzt zwei Starter:

- `Start-Blitztext-Offline.bat`
- `Start-Blitztext-Hybrid.bat`
- `Start-Blitztext-Tray-Offline.bat`
- `Start-Blitztext-Tray-Hybrid.bat`

Beide starten die App minimiert per Doppelklick.

- **Offline Starter**: lokale Transkription ohne OpenAI
- **Hybrid Starter**: lokale Transkription + OpenAI Rewrite
- **Tray Offline Starter**: Offline + System-Tray-Icon
- **Tray Hybrid Starter**: Hybrid + System-Tray-Icon

Wichtig fuer Hybrid:

- `OPENAI_API_KEY` muss als Umgebungsvariable gesetzt sein
- sonst bricht der Starter mit Hinweis ab

Beenden der laufenden App:

- Fenster, in das eingefuegt wird, fokussieren
- `ESC` druecken

## v0.4: Autostart beim Windows-Login

Du kannst Blitztext jetzt automatisch beim Login starten lassen.

Verfuegbare Skripte:

- `Enable-Autostart-Offline.bat`
- `Enable-Autostart-Hybrid.bat`
- `Disable-Autostart.bat`
- `Autostart-Status.bat`

Empfohlener Ablauf:

1. `Autostart-Status.bat` ausfuehren
2. Gewuenschten Modus aktivieren
3. Optional Status erneut pruefen

Hinweise:

- Es wird immer nur **ein** Autostart-Modus aktiv gehalten
- Hybrid braucht `OPENAI_API_KEY` als Benutzer-Umgebungsvariable
- Primar wird der Windows Task Scheduler genutzt
- Falls Scheduler gesperrt ist, wird automatisch der Startup-Ordner verwendet

## v0.5: Echter Tray-Modus

Mit `--tray` laeuft Blitztext mit dauerhaftem Icon im Systembereich.

Tray-Menue:

- Statusanzeige
- Aufnahme starten
- Aufnahme stoppen
- Beenden

Start per CLI:

```powershell
../.venv/Scripts/python.exe app.py --offline --tray
```

Oder per Doppelklick:

- `Start-Blitztext-Tray-Offline.bat`
- `Start-Blitztext-Tray-Hybrid.bat`

## v0.6: Optionaler Autostart direkt im Tray

Zusatzskripte fuer Login-Start direkt im System-Tray:

- `Enable-Autostart-Tray-Offline.bat`
- `Enable-Autostart-Tray-Hybrid.bat`

Verhalten:

- Aktiviert genau einen Autostart-Modus (andere Modi werden entfernt)
- Nutzt bevorzugt Task Scheduler
- Nutzt automatisch Startup-Ordner-Fallback, falls Scheduler nicht verfuegbar ist

Status und Deaktivierung:

- `Autostart-Status.bat` zeigt jetzt auch Tray-Task/Fallback-Status
- `Disable-Autostart.bat` entfernt auch Tray-Autostart-Eintraege

## Hinweise

- Das Tool nutzt dein Standard-Mikrofon in Windows.
- Bei `--auto-paste` sollte das Zielfenster fokussiert sein.
- Falls globale Hotkeys blockiert werden, starte das Terminal ggf. als Administrator.
- Der erste Offline-Start kann laenger dauern, da das Modell geladen wird.
