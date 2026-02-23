import os
import time
from utils.logger import get_logger

logger = get_logger()

class VoiceEngine:
    """
    Ultra-fast voice engine orchestrator.
    Combines Apple Speech Recognition (primary) with Faster Whisper (fallback).
    Achieves <200ms latency for instant voice command processing.
    """
    
    def __init__(self, use_apple_speech=True, fallback_to_whisper=True):
        """
        Initialize the voice engine.
        
        Args:
            use_apple_speech: Use Apple's native Speech Recognition (fast)
            fallback_to_whisper: Fall back to Faster Whisper if Apple fails
        """
        self.use_apple_speech = use_apple_speech
        self.fallback_to_whisper = fallback_to_whisper
        
        # Performance metrics
        self.metrics = {
            "apple_success": 0,
            "apple_failures": 0,
            "whisper_fallbacks": 0,
            "total_transcriptions": 0,
            "avg_latency_ms": 0
        }
        
        # Initialize Apple Speech (primary engine)
        self.apple_recognizer = None
        if self.use_apple_speech:
            try:
                from modules.audio.apple_speech_recognizer import AppleSpeechRecognizer
                self.apple_recognizer = AppleSpeechRecognizer(
                    language="en-US",
                    on_device=True
                )
                
                if self.apple_recognizer.is_available():
                    logger.info("✅ Voice Engine: Apple Speech Recognition (Primary)")
                else:
                    logger.warning("⚠️ Apple Speech not available, using Whisper only")
                    self.apple_recognizer = None
                    
            except Exception as e:
                logger.warning(f"⚠️ Failed to load Apple Speech: {e}")
                self.apple_recognizer = None
        
        # Initialize Whisper (fallback engine) — can be lazy-loaded for cooling
        self.whisper_model = None
        import config as _cfg
        self._lazy_whisper = getattr(_cfg, 'LAZY_LOAD_WHISPER', False)
        
        if self._lazy_whisper and self.apple_recognizer:
            logger.info("❄️ Whisper deferred (LAZY_LOAD_WHISPER=True, Apple Speech available)")
        elif self.fallback_to_whisper or not self.apple_recognizer:
            self._load_whisper_now()
        
        # Log engine status
        self._log_engine_status()
    
    def _log_engine_status(self):
        """Log which engines are available"""
        engines = []
        if self.apple_recognizer:
            engines.append("Apple Speech (Primary)")
        if self.whisper_model:
            engines.append("Whisper (Fallback)")
        
        if not engines:
            logger.critical("❌ NO VOICE ENGINES AVAILABLE!")
        else:
            logger.info(f"🎤 Voice Engines: {', '.join(engines)}")
    
    def _load_whisper_now(self):
        """Actually load the Whisper model into memory"""
        try:
            from faster_whisper import WhisperModel
            import config
            
            model_size = getattr(config, "WHISPER_MODEL_SIZE", "base")
            device = getattr(config, "WHISPER_DEVICE", "cpu")
            compute_type = getattr(config, "WHISPER_COMPUTE_TYPE", "int8")
            
            logger.info(f"🔄 Loading Whisper fallback ({model_size})...")
            self.whisper_model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type
            )
            logger.info("✅ Voice Engine: Whisper (Fallback)")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper: {e}")
            self.whisper_model = None
    
    def _ensure_whisper(self):
        """Lazy-load Whisper on demand (only when Apple Speech fails)"""
        if self.whisper_model is not None:
            return True
        logger.info("❄️ Apple Speech failed — lazy-loading Whisper now...")
        self._load_whisper_now()
        return self.whisper_model is not None

    def set_phrases(self, phrases: list[str]):
        """Pass contextual phrases to the underlying recognizer"""
        if self.apple_recognizer and self.use_apple_speech:
             if hasattr(self.apple_recognizer, 'set_phrases'):
                 self.apple_recognizer.set_phrases(phrases)
                 # logger.info(f"✅ Voice Engine: Loaded {len(phrases)} command phrases")
    
    def transcribe(self, audio_file, timeout=3):
        """
        Transcribe audio file using the fastest available engine.
        
        Args:
            audio_file: Path to WAV audio file
            timeout: Maximum time to wait for result
            
        Returns:
            Transcribed text (lowercase) or None
        """
        if not os.path.exists(audio_file):
            logger.warning(f"Audio file not found: {audio_file}")
            return None
        
        self.metrics["total_transcriptions"] += 1
        start_time = time.time()
        
        # Try Apple Speech first (ultra-fast)
        if self.apple_recognizer:
            try:
                logger.debug("🍎 Trying Apple Speech...")
                text = self.apple_recognizer.transcribe_file(audio_file, timeout=timeout)
                
                if text:
                    latency_ms = (time.time() - start_time) * 1000
                    self._update_metrics("apple_success", latency_ms)
                    logger.info(f"✅ Apple Speech: '{text}' ({latency_ms:.0f}ms)")
                    return self._post_process(text, audio_file)
                else:
                    logger.debug("⚠️ Apple Speech returned no result")
                    self.metrics["apple_failures"] += 1
                    # Fast-path: do not retry/fallback when Apple explicitly reports silence.
                    if getattr(self.apple_recognizer, "last_error_type", None) == "no_speech":
                        logger.debug("🛑 Apple reported no speech; skipping retry/fallback")
                        self._cleanup_file(audio_file)
                        return None
                    
            except Exception as e:
                logger.warning(f"⚠️ Apple Speech error: {e}")
                self.metrics["apple_failures"] += 1
        
        # RETRY Apple Speech BEFORE falling back to Whisper (cooling optimization)
        if self.apple_recognizer:
            try:
                logger.debug("🍎 Retrying Apple Speech before Whisper...")
                text = self.apple_recognizer.transcribe_file(audio_file, timeout=timeout + 1)
                if text:
                    latency_ms = (time.time() - start_time) * 1000
                    self._update_metrics("apple_success", latency_ms)
                    logger.info(f"✅ Apple Speech Retry: '{text}' ({latency_ms:.0f}ms)")
                    return self._post_process(text, audio_file)
                else:
                    self.metrics["apple_failures"] += 1
                    if getattr(self.apple_recognizer, "last_error_type", None) == "no_speech":
                        logger.debug("🛑 Apple retry confirmed no speech; skipping Whisper fallback")
                        self._cleanup_file(audio_file)
                        return None
            except Exception as e:
                logger.debug(f"⚠️ Apple Speech retry failed: {e}")
                self.metrics["apple_failures"] += 1
        
        # Last resort: Fallback to Whisper (lazy-load if needed)
        self._ensure_whisper()
        if self.whisper_model and self.fallback_to_whisper:
            try:
                logger.debug("🔄 Falling back to Whisper...")
                self.metrics["whisper_fallbacks"] += 1
                
                segments, info = self.whisper_model.transcribe(
                    audio_file,
                    beam_size=5,
                    language="en"
                )
                
                text = " ".join([segment.text for segment in segments]).strip()
                
                if text:
                    latency_ms = (time.time() - start_time) * 1000
                    self._update_metrics("whisper_success", latency_ms)
                    logger.info(f"✅ Whisper: '{text}' ({latency_ms:.0f}ms)")
                    return self._post_process(text, audio_file)
                    
            except Exception as e:
                logger.error(f"❌ Whisper error: {e}")

        logger.error("❌ All transcription engines failed")
        self._cleanup_file(audio_file)
        return None
    
    def _post_process(self, text, audio_file):
        """Clean up text and remove hallucinations"""
        text_clean = text.lower().strip()
        
        # Cleanup audio file
        self._cleanup_file(audio_file)
        
        if not text_clean:
            return None
        
        # Hallucination filter
        hallucinations = [
            "thank you", "thanks", "subtitles by", "watching",
            "you", "ok", "bye", "amara", "copyright"
        ]
        
        if text_clean in hallucinations:
            logger.debug(f"🚫 Filtered hallucination: '{text_clean}'")
            return None
        
        if any(text_clean.startswith(h) for h in ["subtitles by", "captioned by", "transcribed by"]):
            logger.debug(f"🚫 Filtered hallucination: '{text_clean}'")
            return None
        
        if len(text_clean) < 2:
            return None
        
        return text_clean
    
    def _cleanup_file(self, filename):
        """Remove temporary audio file"""
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass
    
    def _update_metrics(self, metric_type, latency_ms):
        """Update performance metrics"""
        # Update average latency
        total = self.metrics["total_transcriptions"]
        current_avg = self.metrics["avg_latency_ms"]
        self.metrics["avg_latency_ms"] = ((current_avg * (total - 1)) + latency_ms) / total
    
    def get_metrics(self):
        """Get performance statistics"""
        return {
            **self.metrics,
            "apple_success_rate": (
                self.metrics["apple_success"] / max(1, self.metrics["total_transcriptions"])
            ) * 100,
            "whisper_usage_rate": (
                self.metrics["whisper_fallbacks"] / max(1, self.metrics["total_transcriptions"])
            ) * 100
        }
    
    def print_stats(self):
        """Print performance statistics"""
        stats = self.get_metrics()
        logger.info("=" * 50)
        logger.info("🎤 VOICE ENGINE STATISTICS")
        logger.info("=" * 50)
        logger.info(f"Total Transcriptions: {stats['total_transcriptions']}")
        logger.info(f"Average Latency: {stats['avg_latency_ms']:.0f}ms")
        logger.info(f"Apple Success Rate: {stats['apple_success_rate']:.1f}%")
        logger.info(f"Whisper Fallback Rate: {stats['whisper_usage_rate']:.1f}%")
        logger.info("=" * 50)
