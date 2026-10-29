import collections
import time

import numpy as np
import sounddevice as sd

from config import (
    GOOGLE_LANGUAGE, MAX_UTTERANCE_SECONDS, MIC_DEVICE, SAMPLE_RATE, SILENCE_SECONDS,
    SPEECH_THRESHOLD_MIN, STT_ENGINE, WHISPER_LANGUAGE, WHISPER_MODEL, WHISPER_PROMPT,
)

CHUNK_SEC = 0.03
CHUNK = int(SAMPLE_RATE * CHUNK_SEC)


class Microphone:
    def __init__(self, speaking_flag):
        self.speaking = speaking_flag   # Speaker.speaking: Lumo bol raha ho to mic ignore
        self.stream = None
        self.threshold = SPEECH_THRESHOLD_MIN
        self._last_read = time.time()

    def open(self) -> None:
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE, channels=1, dtype="int16",
            blocksize=CHUNK, device=MIC_DEVICE,
        )
        self.stream.start()
        self.calibrate()

    def close(self) -> None:
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()

    def _read(self):
        data, _ = self.stream.read(CHUNK)
        self._last_read = time.time()
        return data[:, 0].copy()

    @staticmethod
    def _rms(chunk) -> float:
        return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2))) / 32768.0

    def calibrate(self, seconds: float = 0.8) -> None:
        """Kamre ka shor naapo, uske hisaab se bolne ki threshold set karo."""
        levels = [self._rms(self._read()) for _ in range(int(seconds / CHUNK_SEC))]
        noise = float(np.median(levels))
        self.threshold = max(SPEECH_THRESHOLD_MIN, noise * 3.0)
        print(f"Mic ready. Shor level: {noise:.4f}, threshold: {self.threshold:.4f}")

    def flush(self) -> None:
        """Processing/bolne ke dauraan jama hui purani awaaz hata do."""
        try:
            n = self.stream.read_available
            if n > 0:
                self.stream.read(n)
        except Exception:
            pass

    def record(self, timeout=None):
        """Bolna shuru hone ka wait, phir chup hone tak record. float32 audio ya None."""
        if time.time() - self._last_read > 0.3:
            self.flush()

        pre = collections.deque(maxlen=int(0.3 / CHUNK_SEC))   # shuruaat ka hissa na kate
        frames = []
        started = False
        loud = silent = 0
        waited = 0.0
        end_silence = int(SILENCE_SECONDS / CHUNK_SEC)
        max_chunks = int(MAX_UTTERANCE_SECONDS / CHUNK_SEC)

        while True:
            chunk = self._read()

            if self.speaking.is_set():   # Lumo khud bol raha hai
                pre.clear()
                frames, started, loud, silent = [], False, 0, 0
                waited += CHUNK_SEC
                if timeout is not None and waited >= timeout:
                    return None
                continue

            level = self._rms(chunk)
            if not started:
                waited += CHUNK_SEC
                if timeout is not None and waited >= timeout:
                    return None
                pre.append(chunk)
                if level > self.threshold:
                    loud += 1
                    if loud >= 2:
                        started = True
                        frames = list(pre)
                        silent = 0
                else:
                    loud = 0
            else:
                frames.append(chunk)
                silent = 0 if level > self.threshold else silent + 1
                if silent >= end_silence or len(frames) >= max_chunks:
                    break

        audio = np.concatenate(frames).astype(np.float32) / 32768.0
        if len(audio) < SAMPLE_RATE * 0.4:   # click ya khaansi, ignore
            return None
        return audio


class Transcriber:
    def __init__(self):
        self._model = None

    def _load(self) -> None:
        if self._model is None:
            from faster_whisper import WhisperModel

            print(f"Whisper '{WHISPER_MODEL}' load ho raha hai (pehli baar download hoga)...")
            self._model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")

    def warm_up(self) -> None:
        if STT_ENGINE == "whisper":
            self._load()
            self.transcribe(np.zeros(SAMPLE_RATE, dtype=np.float32))

    def transcribe(self, audio) -> str:
        if STT_ENGINE == "google":
            return self._google(audio)
        self._load()
        segments, _ = self._model.transcribe(
            audio,
            language=WHISPER_LANGUAGE or None,
            initial_prompt=WHISPER_PROMPT,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        return " ".join(s.text.strip() for s in segments).strip()

    @staticmethod
    def _google(audio) -> str:
        import speech_recognition as sr

        pcm = np.clip(audio * 32767, -32768, 32767).astype(np.int16).tobytes()
        data = sr.AudioData(pcm, SAMPLE_RATE, 2)
        try:
            return sr.Recognizer().recognize_google(data, language=GOOGLE_LANGUAGE)
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print("Google STT error:", e)
            return ""