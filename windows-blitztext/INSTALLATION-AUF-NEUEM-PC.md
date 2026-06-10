# Blitztext auf einem anderen PC installieren

Diese App ist eine reine Python-Anwendung — es gibt **keine fertige `.exe`**.
Du installierst also Python + die benoetigten Bibliotheken. Ist einmal eingerichtet,
laeuft alles wie gewohnt.

---

## 1. Python installieren

- **Python 3.10 oder neuer** von https://www.python.org/downloads/
- Beim Installieren wichtig: Haekchen **"Add Python to PATH"** setzen.

## 2. App-Dateien kopieren

Den Ordner `windows-blitztext` (mit `app.py`, `requirements.txt` und den `.bat`-Dateien)
auf den neuen Rechner kopieren — z. B. per USB-Stick, Cloud oder GitHub.
Mehr Code gibt es nicht; `app.py` ist die ganze App.

## 3. Bibliotheken installieren

Im Ordner ein PowerShell-Fenster oeffnen und eine virtuelle Umgebung anlegen:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Das installiert automatisch alles aus der `requirements.txt`:
`openai`, `sounddevice`, `soundfile`, `numpy`, `pyperclip`, `pynput`,
`faster-whisper`, `pystray`, `pillow`.

> **Hinweis:** Die `.bat`-Starter erwarten die venv im **uebergeordneten** Ordner
> (`..\.venv`), so wie auf dem urspruenglichen Rechner. Wenn du den Ordner
> `windows-blitztext` allein kopierst, leg die venv eine Ebene hoeher an —
> oder passe die Pfade in den `.bat`-Dateien an.

## 4. Mikrofon

Kein Download noetig — die App nutzt das Standard-Mikrofon von Windows.

## 5. OpenAI API-Key — nur wenn du Online/Rewrite willst

- **Reiner Offline-Modus** (`--offline`): **kein** Key noetig.
  Beim ersten Start laedt sich das Whisper-Modell automatisch herunter
  (Internet beim ersten Mal noetig, danach offline).
- **Hybrid/Rewrite**: braucht einen Key:

  ```powershell
  setx OPENAI_API_KEY "dein_key_hier"
  ```

  Danach neues Terminal oeffnen.

---

## Zusammengefasst

| Brauchst du                                        | Pflicht?            |
| -------------------------------------------------- | ------------------- |
| Python 3.10+                                       | ja, immer           |
| Ordner `windows-blitztext`                         | ja, immer           |
| `pip install -r requirements.txt`                  | ja, immer           |
| Internet beim 1. Offline-Start (Modell-Download)   | ja, einmalig        |
| OpenAI API-Key                                     | nur fuer Rewrite/Online |
| FFmpeg o. Ae.                                      | nein, nicht noetig  |

---

## Starten

Danach genauso starten wie gewohnt — z. B. Doppelklick auf:

- `Start-Blitztext-Tray-Hybrid.bat`  (Offline-Transkription + OpenAI Rewrite, Tray-Icon)
- `Start-Blitztext-Tray-Offline.bat` (komplett offline, Tray-Icon)

Oder Autostart beim Login einrichten mit:

- `Enable-Autostart-Tray-Hybrid.bat`
- `Enable-Autostart-Tray-Offline.bat`

## Bedienung

- `F8` = Aufnahme Start/Stop
- `ESC` = App beenden
- Der erkannte Text wird automatisch dort eingefuegt, wo der Cursor steht (Auto-Paste).
