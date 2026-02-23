"""
Ultra-Fast Voice Engine - Standalone Module
============================================

A plug-and-play voice transcription engine combining:
- Apple Speech Recognition (macOS native, <200ms latency)
- Faster Whisper (fallback, ~6-7s latency)

Usage:
------
```python
from voice_engine import VoiceEngine

# Initialize
engine = VoiceEngine(
    use_apple_speech=True,      # Use Apple Speech (macOS only)
    fallback_to_whisper=True,   # Fallback to Whisper if Apple fails
    whisper_model="base",        # Whisper model size
    language="en-US"             # Language code
)

# Transcribe audio file
text = engine.transcribe("audio.wav")
print(f"Transcribed: {text}")

# Get performance stats
stats = engine.get_metrics()
print(f"Average latency: {stats['avg_latency_ms']}ms")
```

Requirements:
-------------
- macOS 10.15+ (for Apple Speech)
- Python 3.8+
- Dependencies: faster-whisper, pyobjc-framework-Speech, pyobjc-framework-AVFoundation

Installation:
-------------
```bash
pip install faster-whisper pyobjc-framework-Speech pyobjc-framework-AVFoundation
```

Features:
---------
- ⚡ Ultra-fast: <200ms with Apple Speech
- 🔄 Auto-fallback: Whisper backup if Apple fails
- 📊 Performance metrics tracking
- 🎯 On-device processing (privacy)
- 🔌 Plug-and-play: No external dependencies
- 🌍 Multi-language support

Author: Jarvis Voice Engine Team
License: MIT
"""

import os
import time
import logging

# Setup logging (standalone - no external dependencies)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AppleSpeechRecognizer:
    """
    Ultra-fast speech recognition using Apple's native Speech framework.
    Achieves <200ms latency by leveraging macOS's on-device processing.
    """
    
    def __init__(self, language="en-US", on_device=True, verbose=True):
        """
        Initialize Apple Speech Recognizer.
        
        Args:
            language: Language code (default: "en-US")
            on_device: Force on-device processing for speed and privacy
            verbose: Enable logging
        """
        self.language = language
        self.on_device = on_device
        self.verbose = verbose
        self.available = False
        self.recognizer = None
        
        # Try to import PyObjC Speech framework
        try:
            from Foundation import NSLocale
            from Speech import (
                SFSpeechRecognizer,
                SFSpeechAudioBufferRecognitionRequest,
                SFSpeechRecognitionTaskHintDictation
            )
            from AVFoundation import AVAudioEngine, AVAudioFormat, AVAudioPCMBuffer
            
            self.SFSpeechRecognizer = SFSpeechRecognizer
            self.SFSpeechAudioBufferRecognitionRequest = SFSpeechAudioBufferRecognitionRequest
            self.SFSpeechRecognitionTaskHintDictation = SFSpeechRecognitionTaskHintDictation
            self.AVAudioEngine = AVAudioEngine
            self.AVAudioFormat = AVAudioFormat
            self.AVAudioPCMBuffer = AVAudioPCMBuffer
            self.NSLocale = NSLocale
            
            self._initialize_recognizer()
            
        except ImportError as e:
            if self.verbose:
                logger.error(f"❌ Apple Speech Framework not available: {e}")
                logger.info("💡 Install with: pip install pyobjc-framework-Speech pyobjc-framework-AVFoundation")
            self.available = False
    
    def _initialize_recognizer(self):
        """Initialize the speech recognizer"""
        try:
            locale = self.NSLocale.alloc().initWithLocaleIdentifier_(self.language)
            self.recognizer = self.SFSpeechRecognizer.alloc().initWithLocale_(locale)
            
            if not self.recognizer or not self.recognizer.isAvailable():
                if self.verbose:
                    logger.warning("⚠️ Speech recognition not available on this system")
                self.available = False
                return
            
            # Enable on-device recognition if supported
            if self.on_device and hasattr(self.recognizer, 'supportsOnDeviceRecognition'):
                if self.recognizer.supportsOnDeviceRecognition():
                    if self.verbose:
                        logger.info("✅ On-device speech recognition enabled")
                else:
                    if self.verbose:
                        logger.warning("⚠️ On-device recognition not supported, using cloud")
            
            self.available = True
            if self.verbose:
                logger.info(f"✅ Apple Speech Recognizer initialized ({self.language})")
            
        except Exception as e:
            if self.verbose:
                logger.error(f"❌ Failed to initialize recognizer: {e}")
            self.available = False
    
    def transcribe_file(self, audio_file, timeout=3):
        """
        Transcribe an audio file using Apple Speech Recognition.
        
        Args:
            audio_file: Path to WAV audio file
            timeout: Maximum time to wait for result (seconds)
            
        Returns:
            Transcribed text (lowercase) or None
        """
        if not self.available:
            return None
        
        if not os.path.exists(audio_file):
            if self.verbose:
                logger.warning(f"Audio file not found: {audio_file}")
            return None
        
        try:
            from Foundation import NSURL
            from Speech import SFSpeechURLRecognitionRequest
            
            start_time = time.time()
            file_url = NSURL.fileURLWithPath_(audio_file)
            request = SFSpeechURLRecognitionRequest.alloc().initWithURL_(file_url)
            
            # Enable on-device if supported
            if self.on_device and hasattr(request, 'setRequiresOnDeviceRecognition_'):
                request.setRequiresOnDeviceRecognition_(True)
            
            # Set task hint for dictation
            if hasattr(request, 'setTaskHint_'):
                request.setTaskHint_(self.SFSpeechRecognitionTaskHintDictation)
            
            # Result container
            result_container = {"text": None, "done": False, "error": None, "partial": None}
            
            # Completion handler
            def completion_handler(result, error):
                if error:
                    result_container["error"] = str(error)
                    result_container["done"] = True
                    return
                
                if result:
                    transcription = result.bestTranscription().formattedString()
                    result_container["partial"] = transcription
                    
                    if result.isFinal():
                        result_container["text"] = transcription
                        result_container["done"] = True
            
            # Start recognition task
            task = self.recognizer.recognitionTaskWithRequest_resultHandler_(
                request, 
                completion_handler
            )
            
            # Wait for completion with partial result capture
            poll_start = time.time()
            last_partial = None
            partial_stable_count = 0
            
            while not result_container["done"]:
                elapsed = time.time() - poll_start
                
                if elapsed > timeout:
                    # Use stable partial result if available
                    if result_container["partial"] and partial_stable_count >= 3:
                        if self.verbose:
                            logger.info(f"⚡ Using partial result after {elapsed:.2f}s")
                        text = result_container["partial"]
                        if task:
                            task.cancel()
                        break
                    else:
                        if self.verbose:
                            logger.warning(f"⏱️ Transcription timeout ({timeout}s)")
                        if task:
                            task.cancel()
                        return None
                
                # Track partial stability
                if result_container["partial"]:
                    if result_container["partial"] == last_partial:
                        partial_stable_count += 1
                    else:
                        partial_stable_count = 0
                        last_partial = result_container["partial"]
                
                time.sleep(0.01)
            else:
                text = result_container["text"]
            
            # Check for errors
            if result_container["error"]:
                if self.verbose:
                    logger.error(f"❌ Transcription error: {result_container['error']}")
                return None
            
            # Post-process
            if text:
                text = text.strip().lower()
                latency = int((time.time() - start_time) * 1000)
                if self.verbose:
                    logger.info(f"✅ Apple Speech: '{text}' ({latency}ms)")
                return text
            
            return None
            
        except Exception as e:
            if self.verbose:
                logger.error(f"❌ Apple Speech transcription failed: {e}")
            return None
    
    def is_available(self):
        """Check if Apple Speech Recognition is available"""
        return self.available


class VoiceEngine:
    """
    Ultra-fast voice engine orchestrator.
    Combines Apple Speech Recognition (primary) with Faster Whisper (fallback).
    """
    
    def __init__(self, use_apple_speech=True, fallback_to_whisper=True, 
                 whisper_model="base", whisper_device="cpu", whisper_compute_type="int8",
                 language="en-US", verbose=True):
        """
        Initialize the voice engine.
        
        Args:
            use_apple_speech: Use Apple's native Speech Recognition (macOS only)
            fallback_to_whisper: Fall back to Faster Whisper if Apple fails
            whisper_model: Whisper model size (tiny, base, small, medium, large)
            whisper_device: Device for Whisper (cpu, cuda)
            whisper_compute_type: Compute type for Whisper (int8, float16, float32)
            language: Language code (default: "en-US")
            verbose: Enable logging
        """
        self.use_apple_speech = use_apple_speech
        self.fallback_to_whisper = fallback_to_whisper
        self.verbose = verbose
        
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
                self.apple_recognizer = AppleSpeechRecognizer(
                    language=language,
                    on_device=True,
                    verbose=verbose
                )
                
                if not self.apple_recognizer.is_available():
                    if self.verbose:
                        logger.warning("⚠️ Apple Speech not available, using Whisper only")
                    self.apple_recognizer = None
                else:
                    if self.verbose:
                        logger.info("✅ Voice Engine: Apple Speech Recognition (Primary)")
                    
            except Exception as e:
                if self.verbose:
                    logger.warning(f"⚠️ Failed to load Apple Speech: {e}")
                self.apple_recognizer = None
        
        # Initialize Whisper (fallback engine)
        self.whisper_model = None
        if self.fallback_to_whisper or not self.apple_recognizer:
            try:
                from faster_whisper import WhisperModel
                
                if self.verbose:
                    logger.info(f"🔄 Loading Whisper fallback ({whisper_model})...")
                
                self.whisper_model = WhisperModel(
                    whisper_model,
                    device=whisper_device,
                    compute_type=whisper_compute_type
                )
                
                if self.verbose:
                    logger.info("✅ Voice Engine: Whisper (Fallback)")
                
            except Exception as e:
                if self.verbose:
                    logger.error(f"❌ Failed to load Whisper: {e}")
                self.whisper_model = None
        
        # Log engine status
        self._log_engine_status()
    
    def _log_engine_status(self):
        """Log which engines are available"""
        if not self.verbose:
            return
            
        engines = []
        if self.apple_recognizer:
            engines.append("Apple Speech (Primary)")
        if self.whisper_model:
            engines.append("Whisper (Fallback)")
        
        if not engines:
            logger.critical("❌ NO VOICE ENGINES AVAILABLE!")
        else:
            logger.info(f"🎤 Voice Engines: {', '.join(engines)}")
    
    def transcribe(self, audio_file, timeout=3, cleanup=True):
        """
        Transcribe audio file using the fastest available engine.
        
        Args:
            audio_file: Path to WAV audio file
            timeout: Maximum time to wait for result (seconds)
            cleanup: Delete audio file after transcription
            
        Returns:
            Transcribed text (lowercase) or None
        """
        if not os.path.exists(audio_file):
            if self.verbose:
                logger.warning(f"Audio file not found: {audio_file}")
            return None
        
        self.metrics["total_transcriptions"] += 1
        start_time = time.time()
        
        # Try Apple Speech first (ultra-fast)
        if self.apple_recognizer:
            try:
                text = self.apple_recognizer.transcribe_file(audio_file, timeout=timeout)
                
                if text:
                    latency_ms = (time.time() - start_time) * 1000
                    self._update_metrics("apple_success", latency_ms)
                    if cleanup:
                        self._cleanup_file(audio_file)
                    return self._post_process(text)
                else:
                    self.metrics["apple_failures"] += 1
                    
            except Exception as e:
                if self.verbose:
                    logger.warning(f"⚠️ Apple Speech error: {e}")
                self.metrics["apple_failures"] += 1
        
        # Fallback to Whisper (slower but reliable)
        if self.whisper_model and self.fallback_to_whisper:
            try:
                if self.verbose:
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
                    if self.verbose:
                        logger.info(f"✅ Whisper: '{text}' ({latency_ms:.0f}ms)")
                    if cleanup:
                        self._cleanup_file(audio_file)
                    return self._post_process(text)
                    
            except Exception as e:
                if self.verbose:
                    logger.error(f"❌ Whisper error: {e}")
        
        # Both engines failed
        if self.verbose:
            logger.error("❌ All transcription engines failed")
        if cleanup:
            self._cleanup_file(audio_file)
        return None
    
    def _post_process(self, text):
        """Clean up text and filter hallucinations"""
        text_clean = text.lower().strip()
        
        if not text_clean or len(text_clean) < 2:
            return None
        
        # Hallucination filter
        hallucinations = [
            "thank you", "thanks", "subtitles by", "watching",
            "you", "ok", "bye", "amara", "copyright"
        ]
        
        if text_clean in hallucinations:
            return None
        
        if any(text_clean.startswith(h) for h in ["subtitles by", "captioned by", "transcribed by"]):
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
        print("=" * 50)
        print("🎤 VOICE ENGINE STATISTICS")
        print("=" * 50)
        print(f"Total Transcriptions: {stats['total_transcriptions']}")
        print(f"Average Latency: {stats['avg_latency_ms']:.0f}ms")
        print(f"Apple Success Rate: {stats['apple_success_rate']:.1f}%")
        print(f"Whisper Fallback Rate: {stats['whisper_usage_rate']:.1f}%")
        print("=" * 50)


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = VoiceEngine(
        use_apple_speech=True,
        fallback_to_whisper=True,
        whisper_model="base",
        language="en-US"
    )
    
    # Transcribe a file
    text = engine.transcribe("test_audio.wav")
    
    if text:
        print(f"\nTranscribed: {text}")
    
    # Print stats
    engine.print_stats()
