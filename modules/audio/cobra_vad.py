"""
Picovoice Cobra Voice Activity Detection (VAD).

Same ecosystem as Porcupine — uses the same AccessKey.
Returns a voice probability [0.0, 1.0] per frame, enabling
finer-grained thresholding than WebRTC's binary detector.

Frame size: 512 samples at 16 kHz (identical to Porcupine).
"""

import struct
import config
from utils.logger import get_logger

logger = get_logger()

# Lazy import — heavy C extension
pvcobra = None


def _ensure_cobra():
    global pvcobra
    if pvcobra is None:
        import pvcobra as _pvcobra
        pvcobra = _pvcobra


class CobraVAD:
    """Picovoice Cobra Voice Activity Detection.

    Replaces WebRTC VAD with a trained neural model that shares
    the Picovoice AccessKey already used by Porcupine.

    Attributes:
        threshold: float — voice probability above which a frame is
                   considered speech. Default 0.5.
        cobra:     pvcobra.Cobra instance (or None if init failed).
    """

    def __init__(self, threshold=None):
        self.threshold = threshold or getattr(config, "COBRA_VAD_THRESHOLD", 0.5)
        self.cobra = None
        self.frame_length = 512   # sensible default matching Porcupine
        self.sample_rate = 16000
        self._setup()

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------
    def _setup(self):
        try:
            _ensure_cobra()
            self.cobra = pvcobra.create(
                access_key=config.PICOVOICE_API_KEY,
            )
            self.frame_length = self.cobra.frame_length
            self.sample_rate = self.cobra.sample_rate
            logger.info(
                f"✅ Cobra VAD Initialized "
                f"(Frame: {self.frame_length}, Rate: {self.sample_rate})"
            )
        except Exception as e:
            logger.warning(f"⚠️ Cobra VAD init failed: {e}. VAD gate disabled.")
            self.cobra = None

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------
    def voice_probability(self, pcm_unpacked) -> float:
        """Return voice probability [0.0, 1.0] for one audio frame.

        Args:
            pcm_unpacked: tuple/list of int16 samples, length == frame_length.
        """
        if not self.cobra:
            return 0.5  # Neutral fallback — never blocks
        try:
            return self.cobra.process(pcm_unpacked)
        except Exception:
            return 0.5

    def voice_probability_from_bytes(self, pcm_bytes: bytes) -> float:
        """Convenience: accept raw PCM bytes and unpack internally."""
        num_samples = len(pcm_bytes) // 2
        if num_samples != self.frame_length:
            return 0.5  # Wrong size — pass through
        pcm_unpacked = struct.unpack_from("h" * self.frame_length, pcm_bytes)
        return self.voice_probability(pcm_unpacked)

    def is_speech(self, pcm_unpacked) -> bool:
        """Binary speech / no-speech decision."""
        return self.voice_probability(pcm_unpacked) > self.threshold

    def is_speech_bytes(self, pcm_bytes: bytes) -> bool:
        """Binary decision from raw PCM bytes."""
        return self.voice_probability_from_bytes(pcm_bytes) > self.threshold

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def cleanup(self):
        if self.cobra:
            try:
                self.cobra.delete()
            except Exception:
                pass
            self.cobra = None
