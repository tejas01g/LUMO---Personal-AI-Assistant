import subprocess
import sys

import sounddevice as sd

from voice.stt import Microphone, Transcriber
from voice.tts import Speaker
from voice.wakeword import find_wake

print("=== 1. Mics ===")
print(sd.query_devices())
print("Default input device number:", sd.default.device[0])

print("\n=== 2. Windows TTS voices ===")
code = (
    "import pyttsx3; e = pyttsx3.init(); "
    "[print(' -', v.name) for v in e.getProperty('voices')]"
)
subprocess.run([sys.executable, "-c", code])

print("\n=== 3. Bolne ka test ===")
tts = Speaker()
tts.say("Namaste, main Lumo hoon. Meri awaaz aa rahi hai?")

print("\n=== 4. Sunne ka test ===")
mic = Microphone(tts.speaking)
mic.open()
stt = Transcriber()
stt.warm_up()
print("Ab bolo, jaise: Lumo chrome kholo (8 second tak sun raha hoon)")
audio = mic.record(timeout=8)
if audio is None:
    print("Kuch sunai nahi diya. config.py mein SPEECH_THRESHOLD_MIN kam karo ya MIC_DEVICE check karo.")
else:
    text = stt.transcribe(audio)
    print("Suna:", repr(text))
    print("Wake word + command:", find_wake(text))
mic.close()