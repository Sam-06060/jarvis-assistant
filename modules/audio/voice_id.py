"""
Voice ID — Speaker Verification using SpeechBrain ECAPA-TDNN.

Creates a 192-dimensional voice fingerprint from enrollment samples
and verifies live audio against it using cosine similarity.

Model: speechbrain/spkrec-ecapa-voxceleb (ECAPA-TDNN, trained on VoxCeleb)
"""

import os
import struct
import threading
import numpy as np
from utils.logger import get_logger

logger = get_logger()

# Lazy imports — these are heavy (PyTorch + SpeechBrain)
torch = None
torchaudio = None
EncoderClassifier = None


def _ensure_imports():
    """Lazy-load PyTorch and SpeechBrain to avoid blocking startup."""
    global torch, torchaudio, EncoderClassifier
    if torch is None:
        import torch as _torch
        torch = _torch
    if torchaudio is None:
        import torchaudio as _torchaudio
        torchaudio = _torchaudio
    if EncoderClassifier is None:
        from speechbrain.inference.speaker import EncoderClassifier as _EC
        EncoderClassifier = _EC


class VoiceID:
    """Speaker Verification engine.

    Lifecycle:
        1. Instantiate (lightweight — no model load)
        2. Call _load_model() in background thread
        3. After enrollment, verify() compares live audio to stored fingerprint

    Graceful degradation:
        - If no enrollment exists → verify() always returns (True, 1.0)
        - If model fails to load  → verify() always returns (True, 1.0)
    """

    # Default HuggingFace model source
    MODEL_SOURCE = "speechbrain/spkrec-ecapa-voxceleb"
    # Embedding dimensionality for ECAPA-TDNN
    EMBEDDING_DIM = 192
    # Expected sample rate
    SAMPLE_RATE = 16000

    def __init__(self, threshold=0.25, embeddings_dir=None, model_dir=None):
        self.threshold = threshold
        self.enabled = True  # Can be toggled live from Swift Settings
        self.embeddings_dir = embeddings_dir or os.path.join("data", "voice_id")
        self.model_dir = model_dir or os.path.join("data", "models", "spkrec-ecapa-voxceleb")
        self.voiceprint_path = os.path.join(self.embeddings_dir, "samson_voiceprint.pt")

        self.model = None
        self.enrolled_embedding = None  # torch.Tensor shape (EMBEDDING_DIM,)
        self.is_ready = threading.Event()
        self._load_failed = False

        # Ensure directories exist
        os.makedirs(self.embeddings_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)

        # Start background model loading
        threading.Thread(
            target=self._load_model, daemon=True, name="VoiceID-ModelLoad"
        ).start()

    # ------------------------------------------------------------------
    # Model Lifecycle
    # ------------------------------------------------------------------

    def _load_model(self):
        """Load the ECAPA-TDNN model and any existing enrollment.

        Runs in background thread. Sets is_ready when complete.
        """
        try:
            logger.info("🔒 Loading Voice ID model (ECAPA-TDNN)...")
            _ensure_imports()
            self.model = EncoderClassifier.from_hparams(
                source=self.MODEL_SOURCE,
                savedir=self.model_dir,
                run_opts={"device": "cpu"},  # M-series Mac — CPU is fast enough
            )
            self._load_enrollment()
            
            # PRE-WARM the PyTorch model to eliminate cold-start latency on the first wake word
            try:
                dummy_signal = torch.zeros(1, self.SAMPLE_RATE, dtype=torch.float32)
                self.model.encode_batch(dummy_signal)
                logger.debug("🔥 Voice ID model pre-warmed")
            except Exception as e:
                logger.debug(f"⚠️ Voice ID pre-warm skipped: {e}")

            logger.info("✅ Voice ID model loaded successfully")
        except Exception as e:
            logger.error(f"❌ Voice ID model load failed: {e}")
            self._load_failed = True
        finally:
            self.is_ready.set()

    def _load_enrollment(self):
        """Load existing voiceprint from disk if available."""
        if os.path.exists(self.voiceprint_path):
            try:
                _ensure_imports()
                self.enrolled_embedding = torch.load(
                    self.voiceprint_path, map_location="cpu", weights_only=True
                )
                logger.info(
                    f"🔓 Voiceprint loaded: {self.voiceprint_path} "
                    f"(dim: {self.enrolled_embedding.shape})"
                )
            except Exception as e:
                logger.warning(f"⚠️ Failed to load voiceprint: {e}")
                self.enrolled_embedding = None

    def _save_enrollment(self):
        """Persist the averaged embedding to disk."""
        if self.enrolled_embedding is not None:
            _ensure_imports()
            torch.save(self.enrolled_embedding, self.voiceprint_path)
            logger.info(f"💾 Voiceprint saved: {self.voiceprint_path}")

    # ------------------------------------------------------------------
    # Enrollment
    # ------------------------------------------------------------------

    def is_enrolled(self) -> bool:
        """Check if a voiceprint has been created."""
        return self.enrolled_embedding is not None

    def enroll_from_files(self, wav_files: list) -> bool:
        """Create voice fingerprint by averaging embeddings from WAV files.

        Args:
            wav_files: List of paths to 16kHz mono WAV files.

        Returns:
            True if enrollment succeeded.
        """
        if not self.model:
            logger.error("❌ Cannot enroll — model not loaded")
            return False

        _ensure_imports()
        import wave
        embeddings = []
        for filepath in wav_files:
            try:
                # Read via standard wave module to bypass torchaudio backend issues on macOS
                with wave.open(filepath, 'rb') as wf:
                    fs = wf.getframerate()
                    num_channels = wf.getnchannels()
                    pcm_bytes = wf.readframes(wf.getnframes())
                
                # Convert to tensor
                num_samples = len(pcm_bytes) // 2
                pcm_ints = struct.unpack(f"{num_samples}h", pcm_bytes)
                signal = torch.tensor(pcm_ints, dtype=torch.float32) / 32768.0
                signal = signal.unsqueeze(0) # (1, num_samples)

                # Resample if needed
                if fs != self.SAMPLE_RATE:
                    resampler = torchaudio.transforms.Resample(fs, self.SAMPLE_RATE)
                    signal = resampler(signal)
                
                # Ensure mono (if recorded in stereo)
                if num_channels > 1:
                    signal = signal.view(1, num_channels, -1).mean(dim=1)

                # Extract embedding
                emb = self.model.encode_batch(signal)
                embeddings.append(emb.squeeze())
                logger.debug(f"  ✅ Embedded: {os.path.basename(filepath)}")
            except Exception as e:
                logger.warning(f"  ⚠️ Skipped {filepath}: {e}")

        if not embeddings:
            logger.error("❌ No valid embeddings extracted")
            return False

        # Average all embeddings into a single fingerprint
        self.enrolled_embedding = torch.stack(embeddings).mean(dim=0)
        self._save_enrollment()
        logger.info(
            f"✅ Enrollment complete: {len(embeddings)} samples "
            f"→ {self.EMBEDDING_DIM}-dim voiceprint"
        )
        return True

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(self, pcm_bytes: bytes, sample_rate: int = 16000) -> tuple:
        """Verify speaker identity from raw PCM audio bytes.

        Args:
            pcm_bytes: Raw 16-bit PCM audio data.
            sample_rate: Sample rate of the audio (default 16000).

        Returns:
            (is_match: bool, similarity_score: float)
            - is_match: True if score >= threshold
            - similarity_score: cosine similarity [-1.0, 1.0]
        """
        # Bypass conditions
        if not self.enabled:
            return True, 1.0
        if self.enrolled_embedding is None:
            return True, 1.0  # No enrollment = bypass (graceful degradation)
        if self.model is None or self._load_failed:
            return True, 1.0  # Model not available = bypass

        try:
            _ensure_imports()
            signal = self._pcm_to_tensor(pcm_bytes, sample_rate)

            # Skip if audio is too short (< 0.3 seconds)
            min_samples = int(self.SAMPLE_RATE * 0.3)
            if signal.shape[-1] < min_samples:
                logger.debug("⚠️ Voice ID: Audio too short for verification")
                return True, 1.0  # Pass through — not enough audio

            embedding = self.model.encode_batch(signal).squeeze()

            similarity = torch.nn.functional.cosine_similarity(
                embedding.unsqueeze(0),
                self.enrolled_embedding.unsqueeze(0),
            ).item()

            is_match = similarity >= self.threshold
            return is_match, similarity

        except Exception as e:
            logger.error(f"❌ Voice ID verification error: {e}")
            return True, 1.0  # Fail open — don't block on errors

    def verify_file(self, wav_path: str) -> tuple:
        """Verify speaker from a WAV file. Useful for testing.

        Returns:
            (is_match: bool, similarity_score: float)
        """
        if not self.model or self.enrolled_embedding is None:
            return True, 1.0

        try:
            _ensure_imports()
            import wave
            with wave.open(wav_path, 'rb') as wf:
                fs = wf.getframerate()
                num_channels = wf.getnchannels()
                pcm_bytes = wf.readframes(wf.getnframes())

            num_samples = len(pcm_bytes) // 2
            pcm_ints = struct.unpack(f"{num_samples}h", pcm_bytes)
            signal = torch.tensor(pcm_ints, dtype=torch.float32) / 32768.0
            signal = signal.unsqueeze(0)

            if fs != self.SAMPLE_RATE:
                signal = torchaudio.transforms.Resample(fs, self.SAMPLE_RATE)(signal)
            if num_channels > 1:
                signal = signal.view(1, num_channels, -1).mean(dim=1)

            embedding = self.model.encode_batch(signal).squeeze()
            similarity = torch.nn.functional.cosine_similarity(
                embedding.unsqueeze(0),
                self.enrolled_embedding.unsqueeze(0),
            ).item()

            return similarity >= self.threshold, similarity
        except Exception as e:
            logger.error(f"❌ Voice ID file verification error: {e}")
            return True, 1.0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _pcm_to_tensor(pcm_bytes: bytes, sample_rate: int = 16000):
        """Convert raw 16-bit PCM bytes to a torch tensor suitable for SpeechBrain.

        Returns: torch.Tensor of shape (1, num_samples), float32, range [-1, 1].
        """
        _ensure_imports()
        num_samples = len(pcm_bytes) // 2
        pcm_ints = struct.unpack(f"{num_samples}h", pcm_bytes)
        signal = torch.tensor(pcm_ints, dtype=torch.float32) / 32768.0
        return signal.unsqueeze(0)  # (1, num_samples) — batch dim for SpeechBrain
