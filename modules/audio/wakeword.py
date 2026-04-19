import pvporcupine
import struct
import os
import sys
import config
from utils.logger import get_logger

logger = get_logger()

class WakeWordEngine:
    def __init__(self):
        self.porcupine = None
        self.frame_length = 512 # Default setup
        self._setup()

    def _setup(self):
        try:
            self.porcupine = pvporcupine.create(
                access_key=config.PICOVOICE_API_KEY,
                keywords=['jarvis'],
                sensitivities=[0.5] 
            )
            self.frame_length = self.porcupine.frame_length
            self.sample_rate = self.porcupine.sample_rate
            logger.debug(f"✅ Porcupine Initialized (Frame: {self.frame_length}, Rate: {self.sample_rate})")
        except Exception as e:
            logger.critical(f"❌ Porcupine Error: {e}")
            logger.critical("Check your PICOVOICE_API_KEY in config.py")
            # We don't exit here, we let the caller decide, but we mark failure
            self.porcupine = None

    def process(self, pcm_data):
        """
        Process a chunk of audio PCM data.
        Returns: True if wake word detected, False otherwise.
        """
        if not self.porcupine:
            return False
            
        try:
            if not pcm_data:
                return False
                
            # Unpack bytes to shorts (required by Porcupine)
            # Ensure proper length
            num_samples = len(pcm_data) // 2
            if num_samples != self.frame_length:
                # logger.warning(f"WakeFrame Size Mismatch: {num_samples} vs {self.frame_length}")
                return False
                
            pcm_unpacked = struct.unpack_from("h" * self.frame_length, pcm_data)
            keyword_index = self.porcupine.process(pcm_unpacked)
            
            return keyword_index >= 0
        except Exception as e:
            logger.error(f"Wake Engine Process Error: {e}")
            return False

    def play_wake_sound(self):
        """Plays a system sound to acknowledge wake word"""
        os.system("afplay /System/Library/Sounds/Tink.aiff &")
    
    def play_interrupt_sound(self):
        """Sound to confirm force interrupt"""
        os.system("afplay /System/Library/Sounds/Basso.aiff &")

    def cleanup(self):
        if self.porcupine:
            self.porcupine.delete()
