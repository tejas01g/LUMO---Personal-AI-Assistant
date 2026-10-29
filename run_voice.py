import os
import re
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

from config import LOG_DIR

# pythonw (autostart) mein console nahi hota, isliye sab kuch log file mein
if sys.stdout is None or sys.stderr is None or "--log" in sys.argv:
    _log = LOG_DIR / "lumo.log"
    if _log.exists() and _log.stat().st_size > 2_000_000:
        _log.replace(LOG_DIR / "lumo.old.log")
    sys.stdout = sys.stderr = open(_log, "a", buffering=1, encoding="utf-8")

import ollama

from config import (
    ASSISTANT_NAME, FOLLOWUP_SECONDS, MODEL, NUM_CTX, VOICE_SHELL_ENABLED,
)
from core.assistant import Assistant
from tools import reminders, shell
from voice.stt import Microphone, Transcriber
from voice.tts import Speaker
from voice.wakeword import find_wake, is_exit

YES = {"haan", "han", "ha", "yes", "yeah", "yep", "ok", "okay", "kardo", "chalao", "chala"}
NO = {"nahi", "nahin", "na", "no", "nope", "mat", "ruko", "cancel", "stop"}


def log(*args) -> None:
    print(datetime.now().strftime("%H:%M:%S"), *args, flush=True)


def start_ollama_server() -> None:
    """Ollama band ho to 'ollama serve' chalane ki koshish (bina window ke)."""
    exe = shutil.which("ollama")
    if not exe:
        candidate = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
        if candidate.exists():
            exe = str(candidate)
    if not exe:
        log("ollama.exe nahi mila, Ollama ko Start menu se kholo.")
        return
    try:
        subprocess.Popen(
            [exe, "serve"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        log("Ollama khud start karne ki koshish ki.")
    except Exception as e:
        log("Ollama start nahi hua:", e)


def wait_for_ollama() -> None:
    """Boot ke baad Ollama late start hota hai (ya band hota hai), to ready hone tak wait."""
    attempt = 0
    while True:
        try:
            ollama.list()
            ollama.show(MODEL)
            break
        except Exception as e:
            attempt += 1
            if attempt == 1 or attempt % 6 == 0:
                log(f"Ollama ready nahi hai (try {attempt}):", str(e)[:120])
            if attempt in (6, 18):   # ~30 sec aur ~90 sec baad khud start karo
                start_ollama_server()
            time.sleep(5)
    try:  # model ko GPU mein pehle se load kar lo
        ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": "hi"}],
            options={"num_ctx": NUM_CTX},
            keep_alive="30m",
        )
    except Exception as e:
        log("LLM warm-up fail:", e)


def open_mic(mic: Microphone) -> None:
    while True:
        try:
            mic.open()
            return
        except Exception as e:
            log("Mic open nahi hua, 5 sec baad dobara:", e)
            time.sleep(5)


def make_voice_confirm(mic: Microphone, stt: Transcriber, tts: Speaker):
    def confirm(command: str) -> bool:
        if not VOICE_SHELL_ENABLED:
            tts.say("Voice se shell command band hai. Keyboard se chalao.")
            return False
        log("Shell command confirmation:", command)
        tts.say(f"Ye command chalaun? {command}. Haan ya na bolo.")
        audio = mic.record(timeout=7)
        if audio is None:
            return False
        tokens = set(re.findall(r"\w+", stt.transcribe(audio).lower()))
        return bool(tokens & YES) and not (tokens & NO)

    return confirm


def main() -> None:
    log("Start ho raha hai...")
    tts = Speaker()
    stt = Transcriber()
    mic = Microphone(tts.speaking)

    wait_for_ollama()
    assistant = Assistant()
    open_mic(mic)
    stt.warm_up()

    shell.confirm_fn = make_voice_confirm(mic, stt, tts)
    reminders.start_checker(lambda text: (log("[REMINDER]", text),
                                          tts.say(f"Yaad dilana tha: {text}", wait=False)))

    tts.say(f"{ASSISTANT_NAME} online hai. Bolo.")
    log("Sun raha hoon...")

    awake_until = 0.0
    while True:
        try:
            awake = time.time() < awake_until
            audio = mic.record(timeout=(awake_until - time.time()) if awake else None)
            if audio is None:
                continue

            text = stt.transcribe(audio)
            if not text:
                continue

            heard_wake, command = find_wake(text)
            if not awake and not heard_wake:
                continue   # kisi aur ki baat, na log karo na process karo

            if not heard_wake:
                command = text   # follow-up window mein wake word zaroori nahi
            log("Suna:", text)

            if not command:
                tts.say("Haan, bolo.")
                awake_until = time.time() + FOLLOWUP_SECONDS
                continue

            if is_exit(command):
                tts.say("Theek hai, bye.")
                break

            reply = assistant.handle(command)
            tts.say(reply)
            awake_until = time.time() + FOLLOWUP_SECONDS

        except KeyboardInterrupt:
            raise
        except Exception:
            log("Loop error:\n" + traceback.format_exc())
            time.sleep(2)

    mic.close()


if __name__ == "__main__":
    while True:
        try:
            main()
            break   # "Lumo band ho ja" bola to sach mein band
        except KeyboardInterrupt:
            break
        except Exception:
            log("Crash:\n" + traceback.format_exc())
            time.sleep(5)   # 5 sec baad restart