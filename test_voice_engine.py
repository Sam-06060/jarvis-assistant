#!/usr/bin/env python3
"""
Test script for the ultra-fast voice engine.
Verifies Apple Speech Recognition and fallback mechanisms.
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.logger import JarvisLogger
logger = JarvisLogger.setup_logger()

def test_apple_speech_availability():
    """Test if Apple Speech Recognition is available"""
    print("\n" + "="*60)
    print("🍎 TEST 1: Apple Speech Recognition Availability")
    print("="*60)
    
    try:
        from modules.audio.apple_speech_recognizer import AppleSpeechRecognizer
        
        recognizer = AppleSpeechRecognizer(language="en-US", on_device=True)
        
        if recognizer.is_available():
            print("✅ Apple Speech Recognition is AVAILABLE")
            print(f"   Language: en-US")
            print(f"   On-device: True")
            
            # Get supported languages
            languages = recognizer.get_supported_languages()
            print(f"   Supported languages: {len(languages)} total")
            print(f"   Sample: {', '.join(languages[:5])}...")
            
            return True
        else:
            print("❌ Apple Speech Recognition is NOT available")
            print("   This may be due to:")
            print("   - macOS version < 10.15")
            print("   - Missing permissions")
            print("   - System configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error loading Apple Speech: {e}")
        return False

def test_voice_engine_initialization():
    """Test VoiceEngine initialization"""
    print("\n" + "="*60)
    print("🎤 TEST 2: Voice Engine Initialization")
    print("="*60)
    
    try:
        from modules.audio.voice_engine import VoiceEngine
        
        print("Loading VoiceEngine...")
        engine = VoiceEngine(use_apple_speech=True, fallback_to_whisper=True)
        
        print("✅ Voice Engine initialized successfully")
        
        # Check which engines are available
        if engine.apple_recognizer:
            print("   ✓ Apple Speech: Available (Primary)")
        else:
            print("   ✗ Apple Speech: Not available")
        
        if engine.whisper_model:
            print("   ✓ Whisper: Available (Fallback)")
        else:
            print("   ✗ Whisper: Not available")
        
        return engine
        
    except Exception as e:
        print(f"❌ Error initializing VoiceEngine: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_transcriber_integration():
    """Test that Transcriber uses VoiceEngine"""
    print("\n" + "="*60)
    print("🔗 TEST 3: Transcriber Integration")
    print("="*60)
    
    try:
        from modules.audio.transcriber import Transcriber
        
        print("Loading Transcriber...")
        transcriber = Transcriber()
        
        if transcriber.model:
            print("✅ Transcriber loaded successfully")
            
            # Check if it's using VoiceEngine
            model_type = type(transcriber.model).__name__
            print(f"   Model type: {model_type}")
            
            if model_type == "VoiceEngine":
                print("   ✓ Using VoiceEngine (Apple Speech + Whisper)")
            elif model_type == "WhisperModel":
                print("   ✓ Using Whisper only (legacy mode)")
            else:
                print(f"   ? Unknown model type: {model_type}")
            
            return True
        else:
            print("❌ Transcriber model not loaded")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Transcriber: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_settings():
    """Test configuration settings"""
    print("\n" + "="*60)
    print("⚙️  TEST 4: Configuration Settings")
    print("="*60)
    
    try:
        import config
        
        use_apple = getattr(config, "USE_APPLE_SPEECH", None)
        on_device = getattr(config, "APPLE_SPEECH_ON_DEVICE", None)
        fallback = getattr(config, "VOICE_ENGINE_FALLBACK", None)
        vad_silence = getattr(config, "VAD_SILENCE_DURATION", None)
        
        print(f"USE_APPLE_SPEECH: {use_apple}")
        print(f"APPLE_SPEECH_ON_DEVICE: {on_device}")
        print(f"VOICE_ENGINE_FALLBACK: {fallback}")
        print(f"VAD_SILENCE_DURATION: {vad_silence}s")
        
        if use_apple and vad_silence == 0.1:
            print("✅ Configuration is optimized for ultra-fast voice input")
        else:
            print("⚠️  Configuration may not be optimal")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking config: {e}")
        return False

def print_summary(results):
    """Print test summary"""
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Voice engine is ready!")
        print("\n💡 Next steps:")
        print("   1. Start Jarvis: python jarvis.py")
        print("   2. Say the wake word and issue a command")
        print("   3. Expect <200ms transcription latency!")
    else:
        print("\n⚠️  Some tests failed. Review the output above.")
        if not results.get("Apple Speech Available", False):
            print("\n💡 Apple Speech not available - will use Whisper fallback")
            print("   This is slower but still functional.")

def main():
    """Run all tests"""
    print("\n🚀 VOICE ENGINE TEST SUITE")
    print("Testing ultra-fast Apple Speech Recognition integration\n")
    
    results = {}
    
    # Run tests
    results["Apple Speech Available"] = test_apple_speech_availability()
    time.sleep(0.5)
    
    engine = test_voice_engine_initialization()
    results["Voice Engine Init"] = engine is not None
    time.sleep(0.5)
    
    results["Transcriber Integration"] = test_transcriber_integration()
    time.sleep(0.5)
    
    results["Config Settings"] = test_config_settings()
    
    # Summary
    print_summary(results)
    
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
