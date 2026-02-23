import subprocess
import os
import time
import struct
import pyaudio
import config
from utils.logger import get_logger

logger = get_logger()

class TextToSpeech:
    def __init__(self, hud_queue=None):
        self.hud_queue = hud_queue
        self.current_process = None
        self.voice_feedback_level = config.VOICE_FEEDBACK_LEVEL
        self.voice_enabled = True

    def set_feedback_level(self, level):
        valid_levels = ["verbose", "normal", "brief", "silent"]
        if level.lower() in valid_levels:
            self.voice_feedback_level = level.lower()
            return True
        return False

    def toggle_voice(self):
        self.voice_enabled = not self.voice_enabled
        return self.voice_enabled

    def speak(self, text, wake_word_engine=None, audio_stream=None, force_speak=False, allow_interruptions=True):
        """
        Speaks text using system TTS. 
        Supports "Barge-In" if wake_word_engine and audio_stream are provided.
        Returns: True if interrupted, False if completed.
        """
        # Reset Interrupt Flag from previous stops
        self.is_interrupted = False

        # 1. Feedback Level Filters
        if not force_speak and self.voice_feedback_level == "silent":
            logger.debug(f"🤖 (Silent) {config.ASSISTANT_NAME}: {text}")
            return False
        
        if self.voice_feedback_level == "brief":
            if len(text) > 100:
                text = text[:97] + "..."
        
        logger.info(f"🤖 {config.ASSISTANT_NAME}: {text}")
        
        # --- HUD UPDATE ---
        if self.hud_queue:
            # Send to Conversation Log ("JARVIS") instead of Status Header ("IDLE")
            # This ensures the text appears in the main chat box.
            self.hud_queue.put(("JARVIS", text))
        # ------------------
        
        if not self.voice_enabled:
            return False

        # 2. Rate Adjustment
        rate = config.VOICE_RATE
        if self.voice_feedback_level == "verbose":
            rate = 180
        elif self.voice_feedback_level == "brief":
            rate = 220

        # 3. Ensure Clean Slate
        self._kill_process()

        # 4. Start Process (With Retry)
        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.current_process = subprocess.Popen(
                    ["say", "-r", str(rate), text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Check for immediate failure
                time.sleep(0.05)
                if self.current_process.poll() is not None and self.current_process.returncode != 0:
                    err = self.current_process.stderr.read()
                    logger.warning(f"⚠️ TTS Attempt {attempt+1} failed: {err}")
                    self.current_process = None
                    continue # Try again
                
                break # Success
                
            except Exception as e:
                logger.error(f"❌ TTS Exec Error (Attempt {attempt+1}): {e}")
                time.sleep(0.2)
        
        if not self.current_process:
            logger.error("❌ TTS Giving up after retries.")
            return False

        interrupted = False

        # 4. Monitor Loop (for Barge-In)
        while self.current_process and self.current_process.poll() is None:
            # Check external interrupt
            if getattr(self, "is_interrupted", False): # Flag set by controller
                 self._kill_process()
                 interrupted = True
                 break

            # Check Wake Word (if provided AND interruptions allowed)
            if allow_interruptions and wake_word_engine and audio_stream and audio_stream.is_active():
                try:
                    # Non-blocking check would be ideal, but Porcupine needs frames.
                    # We only read if enough data is available to avoid blocking the loop too long?
                    # Or just read blocking? The `say` command runs in background, so blocking here is fine 
                    # as long as we check process status.
                    if audio_stream.get_read_available() >= wake_word_engine.frame_length:
                        pcm = audio_stream.read(wake_word_engine.frame_length, exception_on_overflow=False)
                        if wake_word_engine.process(pcm):
                            logger.info("⚡️ INTERRUPTION DETECTED (Barge-In)!")
                            self._kill_process()
                            wake_word_engine.play_wake_sound() # Acknowledge
                            interrupted = True
                            break
                    else:
                        time.sleep(0.02) # Yield
                except Exception as e:
                    logger.debug(f"TTS Wake check error: {e}")
            else:
                time.sleep(0.05)

        # Check for process error after loop
        if self.current_process:
            return_code = self.current_process.poll()
            if return_code is not None and return_code != 0:
                 err = self.current_process.stderr.read()
                 logger.error(f"❌ TTS 'say' command failed (Code {return_code}): {err}")

        self.current_process = None
        return interrupted

    def stop(self):
        self.is_interrupted = True # Signal the loop
        self._kill_process()

    def _kill_process(self):
        if self.current_process:
            try:
                self.current_process.kill()
                self.current_process = None
            except: pass
