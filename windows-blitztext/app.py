import argparse
import os
import tempfile
import threading
import time
from dataclasses import dataclass
from typing import Callable, List, Optional

import numpy as np
import pyperclip
import soundfile as sf
import sounddevice as sd
from openai import OpenAI
from pynput import keyboard


SAMPLE_RATE = 16000
CHANNELS = 1


@dataclass
class AppConfig:
    offline: bool
    offline_model: str
    rewrite: bool
    auto_paste: bool
    rewrite_model: str
    tray: bool


class PushToTalkRecorder:
    def __init__(self, samplerate: int = SAMPLE_RATE, channels: int = CHANNELS):
        self.samplerate = samplerate
        self.channels = channels
        self._chunks: List[np.ndarray] = []
        self._stream: Optional[sd.InputStream] = None
        self._recording = False
        self._lock = threading.Lock()

    @property
    def recording(self) -> bool:
        with self._lock:
            return self._recording

    def _callback(self, indata, frames, time_info, status):
        if status:
            print(f"[Audio] {status}")
        self._chunks.append(indata.copy())

    def start(self):
        with self._lock:
            if self._recording:
                return
            self._chunks = []
            self._stream = sd.InputStream(
                samplerate=self.samplerate,
                channels=self.channels,
                dtype="float32",
                callback=self._callback,
            )
            self._stream.start()
            self._recording = True

    def stop(self) -> Optional[np.ndarray]:
        with self._lock:
            if not self._recording:
                return None
            assert self._stream is not None
            self._stream.stop()
            self._stream.close()
            self._stream = None
            self._recording = False

        if not self._chunks:
            return None
        return np.concatenate(self._chunks, axis=0)


class LocalTranscriber:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None
        self._load_lock = threading.Lock()

    def _ensure_loaded(self):
        with self._load_lock:
            if self._model is not None:
                return
            # Import lazily so online-only users do not pay startup cost.
            from faster_whisper import WhisperModel

            self._model = WhisperModel(self.model_name, device="cpu", compute_type="int8")

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> str:
        self._ensure_loaded()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            sf.write(tmp_path, audio, sample_rate, subtype="PCM_16")
            segments, _ = self._model.transcribe(tmp_path, language="de", beam_size=5)
            text_parts = [segment.text.strip() for segment in segments if segment.text.strip()]
            return " ".join(text_parts).strip()
        finally:
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def transcribe_audio(client: OpenAI, audio: np.ndarray, sample_rate: int) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        sf.write(tmp_path, audio, sample_rate, subtype="PCM_16")
        with open(tmp_path, "rb") as f:
            result = client.audio.transcriptions.create(model="whisper-1", file=f)
        return result.text.strip()
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


def rewrite_text(client: OpenAI, text: str, model: str) -> str:
    system_prompt = (
        "You rewrite dictated text into clear, concise German. "
        "Keep original meaning and tone, fix grammar and structure, and avoid adding new facts."
    )
    resp = client.chat.completions.create(
        model=model,
        temperature=0.2,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
    )
    return resp.choices[0].message.content.strip()


def auto_paste_text():
    controller = keyboard.Controller()
    time.sleep(0.2)
    with controller.pressed(keyboard.Key.ctrl):
        controller.press("v")
        controller.release("v")


def parse_args() -> AppConfig:
    parser = argparse.ArgumentParser(description="Windows Blitztext alternative")
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Use local faster-whisper transcription instead of OpenAI whisper-1.",
    )
    parser.add_argument(
        "--offline-model",
        default="small",
        help="faster-whisper model size for local mode (tiny/base/small/medium/large-v3).",
    )
    parser.add_argument(
        "--rewrite",
        action="store_true",
        help="Rewrite transcript with an LLM (gpt-4o-mini by default).",
    )
    parser.add_argument(
        "--auto-paste",
        dest="auto_paste",
        action="store_true",
        default=True,
        help="After copying to clipboard, send Ctrl+V to the focused app (default: on).",
    )
    parser.add_argument(
        "--no-auto-paste",
        dest="auto_paste",
        action="store_false",
        help="Only copy to clipboard, do not paste at the cursor automatically.",
    )
    parser.add_argument(
        "--rewrite-model",
        default="gpt-4o-mini",
        help="Model for rewrite step when --rewrite is enabled.",
    )
    parser.add_argument(
        "--tray",
        action="store_true",
        help="Start with a system tray icon and background hotkey listener.",
    )
    args = parser.parse_args()
    return AppConfig(
        offline=args.offline,
        offline_model=args.offline_model,
        rewrite=args.rewrite,
        auto_paste=args.auto_paste,
        rewrite_model=args.rewrite_model,
        tray=args.tray,
    )


class BlitztextRuntime:
    def __init__(
        self,
        config: AppConfig,
        client: Optional[OpenAI],
        local_transcriber: Optional[LocalTranscriber],
    ):
        self.config = config
        self.client = client
        self.local_transcriber = local_transcriber
        self.recorder = PushToTalkRecorder()
        self.stop_event = threading.Event()
        self.busy_lock = threading.Lock()
        self._status_lock = threading.Lock()
        self._status_text = "Bereit"
        self._shutdown_once = threading.Event()
        self._shutdown_hook: Optional[Callable[[], None]] = None
        self._listener: Optional[keyboard.Listener] = None

    @property
    def status_text(self) -> str:
        with self._status_lock:
            return self._status_text

    def _set_status(self, text: str):
        with self._status_lock:
            self._status_text = text

    def set_shutdown_hook(self, hook: Callable[[], None]):
        self._shutdown_hook = hook

    def start_recording(self):
        if self.stop_event.is_set():
            return
        if self.busy_lock.locked():
            print("Noch am Verarbeiten, bitte kurz warten...")
            return
        if self.recorder.recording:
            return
        self.recorder.start()
        self._set_status("Aufnahme laeuft")
        print("Aufnahme gestartet. Druecke F8 zum Stoppen.")

    def stop_recording(self):
        if not self.recorder.recording:
            return
        audio = self.recorder.stop()
        self._set_status("Verarbeite")
        print("Aufnahme gestoppt.")
        threading.Thread(target=self.process_recording, args=(audio,), daemon=True).start()

    def process_recording(self, audio_data: Optional[np.ndarray]):
        if audio_data is None:
            self._set_status("Bereit")
            print("Keine Audio-Daten erkannt.")
            return

        with self.busy_lock:
            try:
                print("Transkribiere...")
                if self.config.offline:
                    transcript = self.local_transcriber.transcribe(audio_data, SAMPLE_RATE)
                else:
                    transcript = transcribe_audio(self.client, audio_data, SAMPLE_RATE)
                if not transcript:
                    print("Leeres Transkript erhalten.")
                    self._set_status("Bereit")
                    return

                final_text = transcript
                if self.config.rewrite:
                    print("Verbessere Text...")
                    final_text = rewrite_text(self.client, transcript, self.config.rewrite_model)

                pyperclip.copy(final_text)
                print("\n--- Ergebnis ---")
                print(final_text)
                print("---------------")
                print("In Zwischenablage kopiert.")

                if self.config.auto_paste:
                    auto_paste_text()
                    print("Auto-Paste gesendet (Ctrl+V).")
            except Exception as exc:
                print(f"Fehler: {exc}")
            finally:
                self._set_status("Bereit")

    def request_shutdown(self):
        if self._shutdown_once.is_set():
            return
        self._shutdown_once.set()

        if self.recorder.recording:
            audio = self.recorder.stop()
            threading.Thread(target=self.process_recording, args=(audio,), daemon=True).start()

        self.stop_event.set()
        if self._listener is not None:
            self._listener.stop()

        hook = self._shutdown_hook
        if hook is not None:
            try:
                hook()
            except Exception:
                pass

    def on_press(self, key):
        if key == keyboard.Key.esc:
            self.request_shutdown()
            return False

        if key != keyboard.Key.f8:
            return

        if self.recorder.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def run_listener_loop(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            self._listener = listener
            while not self.stop_event.is_set():
                time.sleep(0.1)
            listener.stop()

    def start_listener_thread(self):
        threading.Thread(target=self.run_listener_loop, daemon=True).start()

    def print_startup_banner(self):
        print("Windows Blitztext gestartet.")
        print("F8 = Aufnahme Start/Stop")
        print("ESC = Beenden")
        if self.config.offline:
            print(f"Modus: Offline (faster-whisper, Modell: {self.config.offline_model})")
        else:
            print("Modus: Online (OpenAI whisper-1)")
        if self.config.rewrite:
            print(f"Rewrite: Aktiv ({self.config.rewrite_model})")
        else:
            print("Rewrite: Aus")
        if self.config.auto_paste:
            print("Auto-Paste: Aktiv (Text wird am Cursor eingefuegt)")
        else:
            print("Auto-Paste: Aus (nur Zwischenablage)")
        if self.config.tray:
            print("Tray: Aktiv (Icon im Systembereich)")
        print("Sprich in dein Standard-Mikrofon.")


def run_tray(runtime: BlitztextRuntime):
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        print("Tray-Modus benoetigt pystray + pillow. Starte ohne Tray.")
        runtime.run_listener_loop()
        return

    def create_icon_image():
        image = Image.new("RGB", (64, 64), (32, 32, 32))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=(0, 153, 255))
        draw.rectangle((30, 18, 34, 46), fill=(255, 255, 255))
        draw.ellipse((24, 40, 40, 56), fill=(255, 255, 255))
        return image

    def status_label(item):
        return f"Status: {runtime.status_text}"

    def start_action(icon, item):
        runtime.start_recording()

    def stop_action(icon, item):
        runtime.stop_recording()

    def quit_action(icon, item):
        runtime.request_shutdown()
        icon.stop()

    menu = pystray.Menu(
        pystray.MenuItem(status_label, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Aufnahme starten", start_action, enabled=lambda item: not runtime.recorder.recording),
        pystray.MenuItem("Aufnahme stoppen", stop_action, enabled=lambda item: runtime.recorder.recording),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Beenden", quit_action),
    )

    icon = pystray.Icon("blitztext", create_icon_image(), "Blitztext", menu)
    runtime.set_shutdown_hook(icon.stop)
    runtime.start_listener_thread()
    icon.run()
    runtime.request_shutdown()


def main():
    config = parse_args()

    client = None
    local_transcriber = None

    if config.offline:
        local_transcriber = LocalTranscriber(config.offline_model)
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY fehlt. Bitte zuerst setzen.")
            return
        client = OpenAI(api_key=api_key)

    if config.rewrite:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("OPENAI_API_KEY fehlt. Rewrite benoetigt OpenAI.")
            return
        if client is None:
            client = OpenAI(api_key=api_key)

    runtime = BlitztextRuntime(config, client, local_transcriber)
    runtime.print_startup_banner()

    if config.tray:
        run_tray(runtime)
    else:
        runtime.run_listener_loop()


if __name__ == "__main__":
    main()
