from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "lumo.db"

SCREENSHOT_DIR = DATA_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

ASSISTANT_NAME = "Lumo"
# Whisper "Lumo" ko alag alag likh sakta hai, isliye saari spellings
WAKE_WORDS = ["lumo", "lumu", "loomo", "lemo", "lummo", "lomo", "lumos",
              "लूमो", "लुमो", "लमो", "लोमो"]

MODEL = "qwen2.5:7b"
NUM_CTX = 4096          # chhota rakho taaki 6 GB VRAM mein fit ho
HISTORY_LOAD = 12       # restart pe kitne pichle messages wapas load hon
MAX_STORED_MESSAGES = 500
EXAMPLES_IN_PROMPT = 3  # kitne purane corrections prompt mein dikhane hain

# Lumo sirf in folders mein files dhundh/khol sakta hai. Apne hisaab se badlo.
HOME = Path.home()
FILE_SEARCH_DIRS = [HOME / "Documents", HOME / "Downloads", HOME / "Desktop"]

SHELL_TIMEOUT = 30      # seconds

# ------------------------------------------------------------ Voice (Phase 3)
STT_ENGINE = "whisper"      # "whisper" (offline) ya "google" (cloud, audio Google ko jaata hai)
WHISPER_MODEL = "small"     # "base" = tez par kam accurate, "small" = better Hinglish
WHISPER_LANGUAGE = "hi"     # accuracy kharab ho to "en" try karo
WHISPER_PROMPT = "Lumo, chrome kholo. Volume badha do. Time kya hua? Reminder set karo. Screenshot lo."
GOOGLE_LANGUAGE = "en-IN"   # sirf STT_ENGINE = "google" ke liye

SAMPLE_RATE = 16000
MIC_DEVICE = None           # None = default mic. Alag mic ke liye voice_test.py se number dekho
SPEECH_THRESHOLD_MIN = 0.004 # bolne ki minimum awaaz. Shor zyada ho to badhao (0.02)
SILENCE_SECONDS = 0.9       # itni der chup raho to samjho baat khatam
MAX_UTTERANCE_SECONDS = 15
FOLLOWUP_SECONDS = 8        # jawab ke baad kitni der bina "Lumo" bole sunna hai

TTS_RATE = 175              # bolne ki speed
TTS_VOICE_HINT = ""         # voice naam ka hissa, jaise "zira" ya "hindi". Khaali = default
SPEAK_MAX_CHARS = 250       # isse lamba jawab bolne mein chhota kar diya jayega

# Voice se shell command: STT ki galti se galat command ban sakta hai, isliye default band
VOICE_SHELL_ENABLED = False