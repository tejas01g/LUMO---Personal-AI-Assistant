from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "lumo.db"

ASSISTANT_NAME = "Lumo"
WAKE_WORDS = ["lumo", 'lumu', 'loomo', 'lemo', 'lummo']

MODEL = 'qwen2.5:7b'
NUM_CTX = 4096
HISTORY_LOAD = 12
MAX_STORED_MESSAGES = 500 