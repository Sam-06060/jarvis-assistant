"""
Quick Start Example - Standalone Voice Engine
==============================================

This example shows how to use the standalone voice engine
in any Python project (no Jarvis dependencies required).
"""

from voice_engine import VoiceEngine
import time

def main():
    print("🎤 Initializing Voice Engine...")
    
    # Create engine with default settings
    engine = VoiceEngine(
        use_apple_speech=True,      # Use Apple Speech (macOS only)
        fallback_to_whisper=True,   # Fallback to Whisper if needed
        whisper_model="base",        # Whisper model size
        language="en-US",            # Language
        verbose=True                 # Show logs
    )
    
    print("\n" + "="*50)
    print("Ready! Place your audio file as 'test.wav'")
    print("="*50 + "\n")
    
    # Example: Transcribe an audio file
    audio_file = "test.wav"
    
    if not os.path.exists(audio_file):
        print(f"❌ Audio file not found: {audio_file}")
        print("💡 Create a test.wav file or change the filename above")
        return
    
    print(f"🎙️ Transcribing: {audio_file}")
    start = time.time()
    
    text = engine.transcribe(audio_file, timeout=3, cleanup=False)
    
    elapsed = time.time() - start
    
    if text:
        print(f"\n✅ Result: '{text}'")
        print(f"⏱️ Time: {elapsed*1000:.0f}ms")
    else:
        print("\n❌ Transcription failed")
    
    # Show performance stats
    print("\n" + "="*50)
    engine.print_stats()
    print("="*50)


if __name__ == "__main__":
    import os
    main()
