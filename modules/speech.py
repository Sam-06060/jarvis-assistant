import time
import os
import threading
import re
import config
from typing import Optional
from utils.logger import get_logger

# Import New Modular Components
from modules.audio.recorder import AudioRecorder
from modules.audio.wakeword import WakeWordEngine
from modules.audio.transcriber import Transcriber
from modules.audio.tts import TextToSpeech

logger = get_logger()

class SpeechEngine:
    def __init__(self, hud_queue=None):
        self.hud_queue = hud_queue
        
        # 1. Initialize Sub-Modules
        logger.info("🎤 Initializing Audio Sub-Systems...")
        
        self.recorder = AudioRecorder()
        self.wake_engine = WakeWordEngine()
        self.transcriber = Transcriber()
        self.tts = TextToSpeech(hud_queue=self.hud_queue)
        
        # State
        self.is_interrupted = False
        self.wake_word_active = True
        self.last_listen_status = "idle"
        self.manual_sleep_requested = False
        
        # Cleanup
        import atexit
        atexit.register(self.force_stop)

        # Sync TTS voice enabled state
        self.tts.voice_enabled = getattr(self, "voice_enabled", True)
        
        self.voice_feedback_level = config.VOICE_FEEDBACK_LEVEL

    # --- DELEGATED PROPERTIES ---
    @property
    def audio_stream(self):
        return self.recorder.stream

    @property
    def porcupine(self):
        return self.wake_engine.porcupine

    @property
    def pa(self):
        return self.recorder.pa

    # --- CORE METHODS ---

    def wait_for_wake_or_text(self, input_queue):
        """
        Main Event Loop: Waits for Wake Word or Text Command.
        """
        while True:
            # 1. Ensure Stream
            stream = self.recorder.open_stream()
            if not stream:
                time.sleep(1)
                continue

            try:
                # 2. Check Text Input
                if not input_queue.empty():
                    text = input_queue.get()
                    return ("TEXT", text)

                # 3. Check Wake Word
                if self.manual_sleep_requested:
                    # Consume manual sleep request and flush stale mic frames.
                    self.manual_sleep_requested = False
                    self.is_interrupted = False
                    try:
                        available = stream.get_read_available()
                        if available > 0:
                            stream.read(available, exception_on_overflow=False)
                    except Exception:
                        pass
                    time.sleep(0.15)

                if self.is_interrupted:
                    time.sleep(0.5); self.is_interrupted = False

                if not self.wake_word_active:
                    time.sleep(0.1)
                    continue

                # Read Frame
                pcm = self.recorder.read_chunk()
                if pcm and self.wake_engine.process(pcm):
                    self.wake_engine.play_wake_sound()
                    return ("VOICE", None)

                time.sleep(0.01)

            except Exception as e:
                logger.error(f"Wait Loop Error: {e}")
                time.sleep(1)

    def listen_command(self, duration=5, use_vad=None):
        """
        Records and Transcribes audio.
        """
        # Record
        if self.hud_queue: self.hud_queue.put(("LISTENING", "Listening..."))
        
        wav_file = self.recorder.record_until_silence(
            max_duration=15, 
            silence_threshold=0.8,
            hud_queue=self.hud_queue
        )
        
        if not wav_file:
            self.last_listen_status = getattr(self.recorder, "last_record_status", "no_speech")
            return None

        # Transcribe
        if self.hud_queue: self.hud_queue.put(("PROCESSING", "Transcribing..."))
        text = self.transcriber.transcribe(wav_file)
        
        if text:
             normalized_text = self._normalize_transcript(text)
             if not self._is_valid_transcript(normalized_text):
                logger.info(f"🚫 Rejected low-quality transcript: '{normalized_text}'")
                self.last_listen_status = "no_speech"
                return None

             logger.info(f"📝 Recognized: '{normalized_text}'")
             self.last_listen_status = "ok"
             text = normalized_text
             # Duplicate removal: jarvis.py handles the UI update for USER input
             # if self.hud_queue: self.hud_queue.put(("USER", text))
        else:
            self.last_listen_status = "transcribe_failed"
        
        return text

    def listen_confirmation(self, prompt: str, timeout: int = 10) -> Optional[bool]:
        """
        Speaks a prompt and waits for 'yes' or 'no' confirmation.
        Returns:
            True if 'yes', False if 'no', None if timeout/no response.
        """
        logger.info(f"❓ Requesting confirmation: {prompt}")
        self.speak(prompt, allow_interruptions=False)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            text = self.listen_command()
            if not text:
                continue
            
            # Simple confirmation logic
            yes_patterns = [r"\byes\b", r"\byeah\b", r"\byup\b", r"\bok\b", r"\bconfirm\b", r"\bdo it\b", r"\bproceed\b"]
            no_patterns = [r"\bno\b", r"\bnah\b", r"\bnope\b", r"\bcancel\b", r"\bstop\b", r"\bdont\b"]
            
            if any(re.search(p, text) for p in yes_patterns):
                logger.info("✅ User confirmed.")
                return True
            if any(re.search(p, text) for p in no_patterns):
                logger.info("❌ User denied.")
                return False
                
        logger.warning("🕒 Confirmation timed out.")
        return None

    def _normalize_transcript(self, text):
        if not text:
            return ""
        cleaned = re.sub(r"\s+", " ", str(text)).strip().lower()
        return cleaned

    def _is_valid_transcript(self, text):
        # Reject empty/noise-only transcripts early.
        if not text:
            return False

        if len(text) < 2:
            return False

        # Reject punctuation / symbol only strings.
        if not re.search(r"[a-z0-9]", text):
            return False

        tokens = text.split()
        if not tokens:
            return False

        # Typical fan/noise false positives from STT.
        noise_phrases = {
            "it's clear",
            "its clear",
            "so",
            "hmm",
            "hmmm",
            "uh",
            "umm",
            "um",
            "...",
        }
        if text in noise_phrases:
            return False

        # Reject pathological repeated token patterns like "ha ha ha ha".
        if len(tokens) >= 4 and len(set(tokens)) == 1:
            return False

        return True

    def speak(self, text, force_speak=False, allow_interruptions=True):
        """
        Delegates to TTS module, passing audio resources for barge-in.
        """
        # Pass stream and engine for barge-in detection inside TTS loop
        return self.tts.speak(
            text, 
            wake_word_engine=self.wake_engine,
            audio_stream=self.recorder.stream,
            force_speak=force_speak,
            allow_interruptions=allow_interruptions
        )

    def force_stop(self):
        logger.info("⛔️ SpeechEngine Force Stop")
        self.manual_sleep_requested = True
        self.is_interrupted = True
        self.tts.stop()
        self.recorder.interrupt()
        self.wake_engine.play_interrupt_sound()

    def check_for_interrupt_passive(self):
        """
        Checks for wake word passively (e.g. while thinking).
        """
        # Quick poll of stream
        stream = self.recorder.open_stream()
        if stream and stream.get_read_available() >= self.wake_engine.frame_length:
             pcm = self.recorder.read_chunk()
             if self.wake_engine.process(pcm):
                 self.wake_engine.play_wake_sound()
                 return True
        return False

    # --- PROXY METHODS (Compatibility) ---
    def set_feedback_level(self, level):
        if self.tts.set_feedback_level(level):
             self.voice_feedback_level = level
             return f"Level set to {level}"
        return "Invalid level"

    def toggle_voice(self):
        res = self.tts.toggle_voice()
        return f"Voice {'enabled' if res else 'disabled'}"

    def play_wake_sound(self):
        self.wake_engine.play_wake_sound()
