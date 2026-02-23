import os
import time
import threading
from utils.logger import get_logger

logger = get_logger()

class AppleSpeechRecognizer:
    """
    Ultra-fast speech recognition using Apple's native Speech framework.
    Achieves <200ms latency by leveraging macOS's on-device processing.
    """
    
    def __init__(self, language="en-US", on_device=True):
        """
        Initialize Apple Speech Recognizer.
        
        Args:
            language: Language code (default: "en-US")
            on_device: Force on-device processing for speed and privacy
        """
        self.language = language
        self.on_device = on_device
        self.available = False
        self.recognizer = None
        self.recognizer = None
        self.request = None
        self.phrases = []  # Contextual hints
        self.last_error_type = None
        
        # Try to import PyObjC Speech framework
        try:
            from Foundation import NSLocale
            from Speech import (
                SFSpeechRecognizer,
                SFSpeechAudioBufferRecognitionRequest,
                SFSpeechRecognitionTaskHintDictation
            )
            from AVFoundation import (
                AVAudioEngine,
                AVAudioFormat,
                AVAudioPCMBuffer
            )
            
            self.SFSpeechRecognizer = SFSpeechRecognizer
            self.SFSpeechAudioBufferRecognitionRequest = SFSpeechAudioBufferRecognitionRequest
            self.SFSpeechRecognitionTaskHintDictation = SFSpeechRecognitionTaskHintDictation
            self.AVAudioEngine = AVAudioEngine
            self.AVAudioFormat = AVAudioFormat
            self.AVAudioPCMBuffer = AVAudioPCMBuffer
            self.NSLocale = NSLocale
            
            self._initialize_recognizer()
            
        except ImportError as e:
            logger.error(f"❌ Apple Speech Framework not available: {e}")
            logger.info("💡 Install with: pip install pyobjc-framework-Speech pyobjc-framework-AVFoundation")
            self.available = False
    
    def _initialize_recognizer(self):
        """Initialize the speech recognizer"""
        try:
            # Create locale
            locale = self.NSLocale.alloc().initWithLocaleIdentifier_(self.language)
            
            # Create recognizer
            self.recognizer = self.SFSpeechRecognizer.alloc().initWithLocale_(locale)
            
            if not self.recognizer:
                logger.error("❌ Failed to create SFSpeechRecognizer")
                self.available = False
                return
            
            # Check availability
            if not self.recognizer.isAvailable():
                logger.warning("⚠️ Speech recognition not available on this system")
                self.available = False
                return
            
            # Enable on-device recognition if supported
            if self.on_device and hasattr(self.recognizer, 'supportsOnDeviceRecognition'):
                if self.recognizer.supportsOnDeviceRecognition():
                    logger.info("✅ On-device speech recognition enabled")
                else:
                    logger.warning("⚠️ On-device recognition not supported, using cloud")
            
            # FIX: Create a custom queue to avoid blocking main thread callbacks
            from Foundation import NSOperationQueue
            self.queue = NSOperationQueue.alloc().init()
            if hasattr(self.recognizer, 'setQueue_'):
                self.recognizer.setQueue_(self.queue)
            else:
                try: self.recognizer.queue = self.queue
                except: pass

            self.available = True
            logger.info(f"✅ Apple Speech Recognizer initialized ({self.language})")
            
            self.available = True
            logger.info(f"✅ Apple Speech Recognizer initialized ({self.language})")
            
            # Print debug status on init
            self.debug_status()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize recognizer: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.available = False

    def debug_status(self):
        """Print detailed debug info about speech subsystem"""
        try:
            logger.info("--- 🍎 Apple Speech Debug ---")
            logger.info(f"Available: {self.available}")
            if self.recognizer:
                logger.info(f"Recognizer Created: Yes")
                logger.info(f"Supports On-Device: {self.recognizer.supportsOnDeviceRecognition()}")
                logger.info(f"Is Available: {self.recognizer.isAvailable()}")
                # logger.info(f"Locale: {self.recognizer.locale().localeIdentifier()}")
            else:
                logger.info("Recognizer Created: No")
            
            # Check Authorization Status explicitly
            SFSpeechRecognizer = self.SFSpeechRecognizer
            status = SFSpeechRecognizer.authorizationStatus()
            status_map = {
                0: "Not Determined",
                1: "Denied",
                2: "Restricted",
                3: "Authorized"
            }
            logger.info(f"Auth Status: {status} ({status_map.get(status, 'Unknown')})")
            logger.info("-----------------------------")
        except Exception as e:
            logger.error(f"Failed to get debug status: {e}")

    def set_phrases(self, phrases: list[str]):
        """Set contextual phrases to improve recognition accuracy"""
        self.phrases = phrases
        # logger.debug(f"📝 Apple Speech Context: {len(phrases)} phrases loaded")
    
    def transcribe_file(self, audio_file, timeout=3):
        """
        Transcribe an audio file using Apple Speech Recognition.
        
        Args:
            audio_file: Path to WAV audio file
            timeout: Maximum time to wait for result (seconds) - reduced to 3s for speed
            
        Returns:
            Transcribed text (lowercase) or None
        """
        if not self.available:
            logger.debug("Apple Speech not available, skipping")
            return None
        
        if not os.path.exists(audio_file):
            logger.warning(f"Audio file not found: {audio_file}")
            return None
        
        try:
            self.last_error_type = None
            from Foundation import NSURL
            from Speech import SFSpeechURLRecognitionRequest
            
            # Create URL from file path
            file_url = NSURL.fileURLWithPath_(audio_file)
            
            # Create recognition request
            request = SFSpeechURLRecognitionRequest.alloc().initWithURL_(file_url)
            
            if not request:
                logger.error("❌ Failed to create SFSpeechURLRecognitionRequest")
                return None

            # Enable on-device if supported (Let OS decide for now to fix empty results)
            # if self.on_device and hasattr(request, 'setRequiresOnDeviceRecognition_'):
            #    request.setRequiresOnDeviceRecognition_(True)
            
            # Apply Contextual Strings (Hints)
            if self.phrases and hasattr(request, 'setContextualStrings_'):
                request.setContextualStrings_(self.phrases)
            
            # Set task hint for dictation (optimizes for command recognition)
            # if hasattr(request, 'setTaskHint_'):
            #    request.setTaskHint_(self.SFSpeechRecognitionTaskHintDictation)
            
            start_time = time.time()
            logger.debug(f"🍎 Starting recognition task for {audio_file}...")
            
            # Result container - track partial results for speed
            result_container = {"text": None, "done": False, "error": None, "partial": None}
            
            # Completion handler - captures BOTH partial and final results
            def completion_handler(result, error):
                if error:
                    err_str = str(error)
                    # Ignore "Speech recognition was active for too long" error if we have a result
                    if "MainThread" not in err_str: # Avoid excessive logging
                         logger.debug(f"🍎 Callback Error: {err_str}")
                    
                    result_container["error"] = err_str
                    if "No speech detected" in err_str or "Code=1110" in err_str:
                        self.last_error_type = "no_speech"
                    else:
                        self.last_error_type = "engine_error"
                    result_container["done"] = True
                    return
                
                if result:
                    # Capture partial results immediately (for speed)
                    transcription = result.bestTranscription().formattedString()
                    # logger.debug(f"🍎 Partial: {transcription}")
                    result_container["partial"] = transcription
                    
                    # Mark as done when final
                    if result.isFinal():
                        transcription = result.bestTranscription().formattedString()
                        logger.debug(f"🍎 Final Result Received: '{transcription}'")
                        if not transcription:
                             logger.warning("🍎 Final result returned empty string!")
                        
                        result_container["text"] = transcription
                        result_container["done"] = True
            
            # Start recognition task
            task = self.recognizer.recognitionTaskWithRequest_resultHandler_(
                request, 
                completion_handler
            )
            
            if not task:
                logger.error("❌ Failed to create recognition task")
                return None
            
            # Wait for completion with aggressive timeout and partial result capture
            poll_start = time.time()
            last_partial = None
            partial_stable_count = 0
            
            logger.debug("🍎 Waiting for results...")
            
            while not result_container["done"]:
                elapsed = time.time() - poll_start
                
                # Check timeout
                if elapsed > timeout:
                    # If we have a stable partial result, use it!
                    if result_container["partial"] and partial_stable_count >= 3:
                        logger.info(f"⚡ Using partial result after {elapsed:.2f}s")
                        text = result_container["partial"]
                        if task:
                            task.cancel()
                        break
                    else:
                        logger.warning(f"⏱️ Transcription timeout ({timeout}s), no stable result")
                        self.last_error_type = "timeout"
                        if task:
                            task.cancel()
                        return None
                
                # Track partial stability (if same result 3 times, it's probably final)
                if result_container["partial"]:
                    if result_container["partial"] == last_partial:
                        partial_stable_count += 1
                    else:
                        partial_stable_count = 0
                        last_partial = result_container["partial"]
                
                time.sleep(0.01)  # 10ms polling
            else:
                # Normal completion
                text = result_container["text"]
            
            # Check for errors
            if result_container["error"]:
                logger.error(f"❌ Transcription error: {result_container['error']}")
                return None
            
            # Get text and post-process
            if text:
                text = text.strip().lower()
                latency = int((time.time() - start_time) * 1000)
                logger.info(f"✅ Apple Speech: '{text}' ({latency}ms)")
                self.last_error_type = "ok"
                return text
            
            self.last_error_type = "empty_result"
            return None
            
        except Exception as e:
            logger.error(f"❌ Apple Speech transcription failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.last_error_type = "engine_error"
            return None
    
    def transcribe_buffer(self, audio_data, sample_rate=16000, timeout=5):
        """
        Transcribe audio from a buffer (for streaming).
        
        Args:
            audio_data: Raw PCM audio bytes
            sample_rate: Audio sample rate
            timeout: Maximum wait time
            
        Returns:
            Transcribed text or None
        """
        if not self.available:
            return None
        
        try:
            import wave
            import tempfile
            
            # Save buffer to temporary WAV file
            # (Apple Speech works best with file-based recognition)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_path = tmp_file.name
                
                # Write WAV file
                with wave.open(tmp_path, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data)
            
            # Transcribe the file
            result = self.transcribe_file(tmp_path, timeout=timeout)
            
            # Cleanup
            try:
                os.remove(tmp_path)
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Buffer transcription failed: {e}")
            return None
    
    def is_available(self):
        """Check if Apple Speech Recognition is available"""
        return self.available
    
    def get_supported_languages(self):
        """Get list of supported languages"""
        if not self.available:
            return []
        
        try:
            locales = self.SFSpeechRecognizer.supportedLocales()
            return [str(locale.localeIdentifier()) for locale in locales]
        except:
            return []
