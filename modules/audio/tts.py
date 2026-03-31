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

    def speak(self, text, wake_word_engine=None, audio_stream=None, force_speak=False, allow_interruptions=True, is_hotswap_resume=False):
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
        
        if not is_hotswap_resume:
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
        cmd = ["say", "-r", str(rate)]
        
        if getattr(config, "FORCE_MAC_BUILTIN_AUDIO", False):
            try:
                out = subprocess.check_output(['say', '-a', '?'], stderr=subprocess.DEVNULL).decode()
                device_id = None
                for line in out.split('\n'):
                    if not line.strip(): continue
                    lower_line = line.lower()
                    if any(x in lower_line for x in ["macbook", "imac", "built-in", "mac mini", "speakers"]):
                        device_id = line.split()[0]
                        break
                if device_id:
                    cmd.extend(["-a", device_id])
            except Exception as e:
                logger.debug(f"Audio device check failed: {e}")
                
        cmd.append(text)

        max_retries = 2
        for attempt in range(max_retries):
            try:
                self.current_process = subprocess.Popen(
                    cmd,
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

        # Main monitoring loop
        words_per_sec = rate / 60.0
        start_time = time.time()
        
        while self.current_process and self.current_process.poll() is None:
            # Check for synchronous TTS hardware hot-swap
            if getattr(self, "needs_hotswap", False):
                self.needs_hotswap = False
                logger.info("🔄 TTS Output Hot-swap engaged! Rerouting playing audio...")
                self._kill_process()
                
                # Estimate remaining text based on elapsed playback time
                elapsed = time.time() - start_time
                words_spoken = int(elapsed * words_per_sec)
                words = text.split()
                if words_spoken < len(words):
                    remaining_text = " ".join(words[words_spoken:])
                    # Recurse synchronously into the new hardware driver with the unread words
                    return self.speak(remaining_text, wake_word_engine, audio_stream, force_speak, allow_interruptions, is_hotswap_resume=True)
                break
                
            # Check external interrupt
            if getattr(self, "is_interrupted", False): # Flag set by controller
                 self._kill_process()
                 interrupted = True
                 break

            # Check Wake Word (if provided AND interruptions allowed)
            stream_active = False
            try:
                stream_active = allow_interruptions and wake_word_engine and audio_stream and audio_stream.is_active()
            except Exception:
                pass # Hot-Swap or PyAudio stream drop in progress
                
            if stream_active:
                try:
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
                    logger.debug(f"TTS Wake check error (possibly hotwapping): {e}")
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
