import os
import config
from utils.logger import get_logger

logger = get_logger()

class Transcriber:
    def __init__(self, model_size=None):
        """
        Initialize Faster Whisper transcriber.
        Args:
            model_size: Model size ("tiny", "base", "small", etc.)
        """
        self.model_size = model_size or getattr(config, "WHISPER_MODEL_SIZE", "base")
        self.device = getattr(config, "WHISPER_DEVICE", "cpu")
        self.compute_type = getattr(config, "WHISPER_COMPUTE_TYPE", "int8")
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the voice engine (Apple Speech + Whisper fallback)"""
        try:
            import config
            
            # Check if we should use the new ultra-fast voice engine
            use_apple_speech = getattr(config, "USE_APPLE_SPEECH", True)
            
            if use_apple_speech:
                # NEW: Use VoiceEngine (Apple Speech + Whisper fallback)
                logger.info("🚀 Loading Ultra-Fast Voice Engine...")
                from modules.audio.voice_engine import VoiceEngine
                
                self.model = VoiceEngine(
                    use_apple_speech=True,
                    fallback_to_whisper=True
                )
                logger.info("✅ Voice Engine Ready (Apple Speech + Whisper fallback)")
            else:
                # LEGACY: Use Faster Whisper only
                logger.info("🔄 Loading Faster Whisper (legacy mode)...")
                from faster_whisper import WhisperModel
                
                self.model = WhisperModel(
                    self.model_size, 
                    device=self.device, 
                    compute_type=self.compute_type
                )
                logger.info(f"✅ Transcriber Ready (faster-whisper {self.model_size})")
                
        except Exception as e:
            logger.critical(f"❌ Failed to load transcription engine: {e}")
            self.model = None

    def transcribe(self, filename):
        """
        Transcribe audio file using the voice engine.
        Automatically uses Apple Speech (fast) or Whisper (fallback).
        Returns: Lowercase text string or None.
        """
        if not os.path.exists(filename):
            logger.warning(f"Transcribe called on missing file: {filename}")
            return None

        if not self.model:
            logger.error("❌ Voice engine not loaded")
            return None

        try:
            # Check if using VoiceEngine or legacy Whisper
            if hasattr(self.model, 'transcribe'):
                # VoiceEngine or WhisperModel - both have transcribe()
                text = self.model.transcribe(filename)
                
                # VoiceEngine handles post-processing internally
                # Legacy Whisper needs manual processing
                if text is None:
                    return None
                    
                if isinstance(text, str):
                    # VoiceEngine returned clean text
                    return text
                else:
                    # Legacy Whisper returns (segments, info)
                    segments, info = text
                    text = " ".join([segment.text for segment in segments]).strip()
                    return self._post_process(text, filename)
            else:
                logger.error("❌ Invalid transcription model")
                return None

        except Exception as e:
            logger.error(f"❌ Transcription Error: {e}")
            # Cleanup file on error
            if os.path.exists(filename):
                try: os.remove(filename)
                except: pass
            return None

    def _post_process(self, text, filename):
        """Filters hallucinations and cleans text"""
        text_clean = text.lower().strip()
        
        # Cleanup file
        if os.path.exists(filename): 
            try: os.remove(filename)
            except: pass

        if not text_clean: 
            return None
            
        # Hallucination Filter
        hallucinations = [
            "thank you", "thanks", "subtitles by", "watching", 
            "you", "ok", "bye", "amara", "copyright", "text"
        ]
        
        if text_clean in hallucinations:
            return None
        
        if any(text_clean.startswith(h) for h in ["subtitles by", "captioned by", "transcribed by"]):
            return None
            
        if len(text_clean) < 2:
            return None

        return text_clean
