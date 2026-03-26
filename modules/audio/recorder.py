import pyaudio
import time
import wave
import struct
import threading
import config
from utils.logger import get_logger

logger = get_logger()

class AudioRecorder:
    def __init__(self):
        self.pa = None
        self.stream = None
        self.rate = 16000
        self.chunk = 512
        self.channels = 1
        self.format = pyaudio.paInt16
        
        self.is_interrupted = False
        self.last_record_status = "idle"
        self.consecutive_read_failures = 0
        
        # Initialize PyAudio
        self._init_audio()

        # VAD Setup
        self.vad = None
        if config.ENABLE_VOICE_ACTIVITY_DETECTION:
             try:
                from utils.vad_detector import VADDetector
                self.vad = VADDetector(aggressiveness=2, sample_rate=self.rate)
             except ImportError:
                 logger.warning("VAD module not found or failed to load")

    def _init_audio(self):
        for attempt in range(3):
            try:
                self.pa = pyaudio.PyAudio()
                return
            except Exception as e:
                logger.warning(f"Audio Init fail ({attempt}): {e}")
                time.sleep(1)
        logger.critical("Failed to init PyAudio")

    def _reinit_audio_system(self):
        """Completely restart PortAudio to pick up new default devices after a disconnect."""
        logger.warning("🔄 Re-initializing Audio System (Device change/disconnect detected)...")
        self.close_stream()
        if self.pa:
            try:
                self.pa.terminate()
            except Exception: pass
            self.pa = None
        time.sleep(0.5)
        self._init_audio()
        self.consecutive_read_failures = 0

    def open_stream(self):
        """Opens audio stream if not open"""
        if self.stream and self.stream.is_active():
            return self.stream

        if getattr(self, 'pa', None) is None:
            self._init_audio()

        try:
             self.stream = self.pa.open(
                rate=self.rate,
                channels=self.channels,
                format=self.format,
                input=True,
                frames_per_buffer=self.chunk
            )
             return self.stream
        except Exception as e:
            logger.error(f"Failed to open stream: {e}")
            return None

    def close_stream(self):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except: pass
            self.stream = None

    # def read_chunk(self):
    #     """Reads a single chunk from stream"""
    #     if not self.stream: self.open_stream()
    #     if not self.stream: return None

    #     try:
    #         return self.stream.read(self.chunk, exception_on_overflow=False)
    #     except Exception as e:
    #         logger.warning(f"Read error: {e}")
    #         return None

    def read_chunk(self):
        """Reads a single chunk from stream, enforcing strict buffer sizes."""
        if not self.stream: self.open_stream()
        if not self.stream:
            self.consecutive_read_failures += 1
            if self.consecutive_read_failures > 15:
                self._reinit_audio_system()
            return None

        try:
            # PyAudio read defaults to blocking
            data = self.stream.read(self.chunk, exception_on_overflow=False)

            # THE FIX: Apple Silicon CoreAudio Quirk Protection
            # 512 frames * 2 bytes (16-bit format) = 1024 bytes.
            # If CoreAudio desyncs and hands us a partial frame or empty bytes,
            # reject it and force a micro-sleep to prevent a CPU spin-loop.
            expected_bytes = self.chunk * 2 
            if not data or len(data) != expected_bytes:
                self.consecutive_read_failures += 1
                if self.consecutive_read_failures > 15:
                    self._reinit_audio_system()
                time.sleep(0.01) # Force the CPU to rest during a driver glitch
                return None

            self.consecutive_read_failures = 0
            return data

        except IOError as e:
            # Catches PortAudio buffer underflows/overflows cleanly without thrashing
            self.consecutive_read_failures += 1
            if self.consecutive_read_failures > 15:
                logger.debug(f"IOError threshold reached: {e}")
                self._reinit_audio_system()
            else:
                time.sleep(0.01)
            return None
        except Exception as e:
            logger.warning(f"Read error: {e}")
            self.consecutive_read_failures += 1
            if self.consecutive_read_failures > 15:
                self._reinit_audio_system()
            else:
                time.sleep(0.1)
            return None

    def record_until_silence(self, max_duration=30, silence_threshold=0.6, hud_queue=None):
        """
        Record audio until silence is detected or timeout.
        Uses adaptive noise floor calibration for reliable speech detection.
        Returns: Filename of recorded wav, or None.
        """
        import os
        import tempfile
        import math
        
        if not self.open_stream():
            self.last_record_status = "audio_error"
            return None

        self.is_interrupted = False
        self.last_record_status = "recording"
        frames = []
        start_time = time.time()
        
        # === Adaptive VAD State ===
        CALIBRATION_DURATION = 0.3   # Seconds to calibrate noise floor
        SILENCE_WINDOW = silence_threshold  # Seconds of silence to end recording
        SPEECH_MULTIPLIER = 2.5      # RMS must be this × noise floor to count as speech
        MIN_SPEECH_THRESHOLD = 800   # Absolute minimum RMS to count as speech
        
        noise_samples = []           # RMS values during calibration
        noise_floor = 0              # Calibrated noise floor (RMS)
        is_calibrated = False
        is_speaking = False
        speech_started = False       # True once we've detected ANY speech
        silence_dur = 0.0
        timeout_triggered = False
        chunk_duration = self.chunk / self.rate  # ~0.032s per chunk

        # Pre-flush stale audio from buffer
        try:
            if self.stream.get_read_available() > 0:
                 self.stream.read(self.stream.get_read_available(), exception_on_overflow=False)
        except: pass

        logger.debug("👂 Start Listening...")

        while True:
            # 1. Read audio chunk
            data = self.read_chunk()
            
            elapsed = time.time() - start_time
            
            if not data:
                if self.is_interrupted:
                    self.close_stream()
                    self.last_record_status = "interrupted"
                    return None
                if elapsed > max_duration or (not speech_started and elapsed > 7.0):
                    timeout_triggered = True
                    logger.debug("❌ Timeout during audio failure/recovery")
                    break
                continue

            frames.append(data)

            # 2. Check Interruption
            if self.is_interrupted:
                self.close_stream()
                self.last_record_status = "interrupted"
                return None

            # 3. Compute RMS Energy (much more stable than max amplitude)
            pcm = struct.unpack_from("h" * self.chunk, data)
            rms = math.sqrt(sum(s * s for s in pcm) / len(pcm))

            # 4. Calibration Phase — measure ambient noise
            if not is_calibrated:
                noise_samples.append(rms)
                if elapsed >= CALIBRATION_DURATION:
                    noise_floor = sum(noise_samples) / len(noise_samples) if noise_samples else 500
                    # Dynamic threshold: at least MIN_SPEECH_THRESHOLD or SPEECH_MULTIPLIER × noise
                    speech_threshold = max(noise_floor * SPEECH_MULTIPLIER, MIN_SPEECH_THRESHOLD)
                    is_calibrated = True
                    logger.debug(f"🎙️ Calibrated: noise_floor={noise_floor:.0f} RMS, threshold={speech_threshold:.0f} RMS")
                continue  # Don't process VAD until calibrated

            # 5. Speech Detection
            is_loud = rms > speech_threshold

            if is_loud:
                if not speech_started:
                    speech_started = True
                    logger.debug(f"🗣️ Speech Started (RMS: {rms:.0f}, thresh: {speech_threshold:.0f})")
                is_speaking = True
                silence_dur = 0.0
            else:
                if speech_started:
                    silence_dur += chunk_duration

            # 6. End Conditions
            if speech_started and silence_dur >= SILENCE_WINDOW:
                logger.debug(f"✅ End of Speech (Silence: {silence_dur:.2f}s, Total: {elapsed:.2f}s)")
                break
            
            if not speech_started and elapsed > 7.0:
                logger.debug("❌ Timeout (No Speech detected)")
                timeout_triggered = True
                break
        
        # 7. Save File
        if timeout_triggered:
            self.last_record_status = "no_speech"
            if hud_queue: hud_queue.put(("PARTIAL", "Cancelled (Timeout)"))
            time.sleep(0.5)
            if hud_queue: hud_queue.put(("PARTIAL", ""))
            return None
        
        filename = os.path.join(tempfile.gettempdir(), "jarvis_command.wav")
        self._save_wav(filename, frames)
        self.last_record_status = "ok"
        
        return filename

    def _save_wav(self, filename, frames):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pa.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

    def interrupt(self):
        self.is_interrupted = True

    def stop(self):
        self.close_stream()
        if self.pa: self.pa.terminate()
