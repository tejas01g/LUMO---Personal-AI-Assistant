import os
import queue
import re
import subprocess
import threading
import time

from config import SPEAK_MAX_CHARS, TTS_RATE, TTS_VOICE_HINT

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# Windows ki built-in awaaz (System.Speech). Text environment variable se jaata hai,
# isliye quotes ya special characters ka koi jhanjhat nahi.
PS_SCRIPT = "; ".join([
    "Add-Type -AssemblyName System.Speech",
    "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer",
    "$s.Rate = [int]$env:LUMO_RATE",
    "if ($env:LUMO_VOICE) { foreach ($v in $s.GetInstalledVoices()) { "
    "if ($v.VoiceInfo.Name -like ('*' + $env:LUMO_VOICE + '*')) { "
    "$s.SelectVoice($v.VoiceInfo.Name); break } } }",
    "$s.Speak($env:LUMO_TEXT)",
])


def clean(text: str) -> str:
    """Bolne layak text banata hai: paths, markdown hata do, lamba jawab chhota karo."""
    text = re.sub(r"[A-Za-z]:\\\S+", "file", text)
    text = re.sub(r"[*#`_]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > SPEAK_MAX_CHARS:
        cut = text[:SPEAK_MAX_CHARS]
        end = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))
        text = cut[: end + 1] if end > 60 else cut
    return text


class Speaker:
    """Ek alag thread jawab bolta hai, taaki reminder bhi bina atke bol sake."""

    def __init__(self):
        self.speaking = threading.Event()   # jab tak bol raha hai, mic ignore hoga
        self._q = queue.Queue()
        self._pending = 0
        self._lock = threading.Lock()
        # TTS_RATE 175 = normal. SAPI ki range -10 (dheema) se +10 (tez) hoti hai
        self._rate = max(-10, min(10, round((TTS_RATE - 175) / 15)))
        threading.Thread(target=self._worker, daemon=True).start()

    def _speak_now(self, text: str) -> None:
        env = os.environ.copy()
        env["LUMO_TEXT"] = text
        env["LUMO_RATE"] = str(self._rate)
        env["LUMO_VOICE"] = TTS_VOICE_HINT or ""
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                 "-Command", PS_SCRIPT],
                env=env, capture_output=True, text=True, errors="replace",
                timeout=60, creationflags=NO_WINDOW,
            )
            if res.returncode != 0:
                print("TTS error:", (res.stderr or res.stdout).strip()[:300])
        except Exception as e:
            print("TTS error:", e)

    def _worker(self) -> None:
        while True:
            text, done = self._q.get()
            try:
                self._speak_now(text)
            finally:
                time.sleep(0.25)  # speaker ki goonj khatam hone do
                with self._lock:
                    self._pending -= 1
                    if self._pending == 0:
                        self.speaking.clear()
                done.set()

    def say(self, text: str, wait: bool = True) -> None:
        text = clean(text)
        if not text:
            return
        print("Lumo:", text)
        done = threading.Event()
        with self._lock:
            self._pending += 1
            self.speaking.set()
        self._q.put((text, done))
        if wait:
            done.wait(timeout=60)