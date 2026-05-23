#!/usr/bin/env python3
"""
Jarvis Voice Enrollment CLI
============================

Interactive tool to record voice samples and create your voice fingerprint
for Speaker Verification (Voice ID).
"""

import sys
import os
import subprocess

# Auto-relaunch in virtual environment if needed
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
venv_python = os.path.join(project_root, ".venv", "bin", "python")

if os.path.exists(venv_python) and sys.executable != venv_python:
    print("🔄 Relaunching in virtual environment...")
    os.execv(venv_python, [venv_python] + sys.argv)

import time
import wave
import struct
import math

# Add project root to path
sys.path.insert(0, project_root)


SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK = 512
FORMAT_WIDTH = 2  # 16-bit = 2 bytes per sample

# Phrases to record during enrollment
ENROLLMENT_PHRASES = [
    'Jarvis',
    'Hey Jarvis, what is the weather today?',
    'Open the browser for me',
    'Jarvis, set a timer for five minutes',
    'Good morning Jarvis',
    'Jarvis, play some music',
    'What time is it, Jarvis?',
]

MIN_SAMPLES = 5  # Minimum required
MAX_SAMPLES = 10


def print_header():
    print("\n" + "═" * 55)
    print("  🎙️  JARVIS VOICE ENROLLMENT")
    print("═" * 55)
    print()
    print("  You'll record voice samples to create your")
    print("  personal voice fingerprint for Speaker Verification.")
    print()
    print(f"  Minimum samples: {MIN_SAMPLES}")
    print(f"  Recommended:     {MAX_SAMPLES}")
    print()
    print("  Speak naturally — the system adapts to your voice.")
    print("═" * 55)
    print()


def init_audio():
    """Initialize PyAudio and find the right input device."""
    import pyaudio
    pa = pyaudio.PyAudio()

    # Try to find built-in mic (same logic as recorder.py)
    input_device = None
    try:
        import config
        if getattr(config, "FORCE_MAC_BUILTIN_AUDIO", False):
            for i in range(pa.get_device_count()):
                dev = pa.get_device_info_by_index(i)
                name = dev.get("name", "").lower()
                if ("macbook" in name or "imac" in name or "mac mini" in name or "built-in" in name) \
                        and dev.get("maxInputChannels", 0) > 0:
                    input_device = i
                    print(f"  🎤 Using: {dev.get('name')} (Index: {i})")
                    break
    except Exception:
        pass

    if input_device is None:
        default = pa.get_default_input_device_info()
        print(f"  🎤 Using default: {default.get('name')}")

    return pa, input_device


def record_sample(pa, input_device, phrase_num, total, phrase):
    """Record a single voice sample with silence detection."""
    print(f"\n  [{phrase_num}/{total}] Say: \"{phrase}\"")
    print("         Press ENTER to start recording...")
    input()
    print("         🔴 Recording... (speak now)")

    stream = pa.open(
        rate=SAMPLE_RATE,
        channels=CHANNELS,
        format=pa.get_format_from_width(FORMAT_WIDTH),
        input=True,
        input_device_index=input_device,
        frames_per_buffer=CHUNK,
    )

    frames = []
    start_time = time.time()
    speech_started = False
    silence_duration = 0.0
    chunk_duration = CHUNK / SAMPLE_RATE

    # Calibrate noise floor (first 0.3s)
    noise_samples = []
    calibrated = False

    while True:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        elapsed = time.time() - start_time

        # Compute RMS
        pcm = struct.unpack_from(f"{CHUNK}h", data)
        rms = math.sqrt(sum(s * s for s in pcm) / len(pcm))

        # Calibration phase
        if not calibrated:
            noise_samples.append(rms)
            if elapsed >= 0.3:
                noise_floor = sum(noise_samples) / len(noise_samples) if noise_samples else 500
                speech_threshold = max(noise_floor * 2.5, 800)
                calibrated = True
            continue

        # Speech detection
        if rms > speech_threshold:
            if not speech_started:
                speech_started = True
            silence_duration = 0.0
        elif speech_started:
            silence_duration += chunk_duration

        # End conditions
        if speech_started and silence_duration >= 0.8:
            break
        if not speech_started and elapsed > 7.0:
            print("         ⚠️ No speech detected. Try again.")
            stream.stop_stream()
            stream.close()
            return None
        if elapsed > 15.0:
            break

    stream.stop_stream()
    stream.close()

    duration = time.time() - start_time

    # Save WAV
    samples_dir = os.path.join(project_root, "data", "voice_id", "samples")
    os.makedirs(samples_dir, exist_ok=True)
    filename = os.path.join(samples_dir, f"enrollment_{phrase_num:02d}.wav")

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(FORMAT_WIDTH)
    wf.setframerate(SAMPLE_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    print(f"         ✅ Saved ({duration:.1f}s)")
    return filename


def run_enrollment(wav_files):
    """Run the actual SpeechBrain enrollment."""
    print("\n" + "─" * 55)
    print("  🧠 Creating voice fingerprint...")
    print("─" * 55)

    from modules.audio.voice_id import VoiceID

    voice_id = VoiceID()

    # Wait for model to load
    print("  ⏳ Loading ECAPA-TDNN model (first time may download ~100MB)...")
    voice_id.is_ready.wait(timeout=300)

    if voice_id._load_failed or voice_id.model is None:
        print("\n  ❌ Failed to load the Voice ID model.")
        print("     Check your internet connection for first-time download.")
        return None

    print("  ✅ Model loaded!")

    # Enroll
    success = voice_id.enroll_from_files(wav_files)

    if not success:
        print("\n  ❌ Enrollment failed. Please try again with clearer audio.")
        return None

    return voice_id


def run_self_test(voice_id, test_file):
    """Verify the enrollment works with one of the recorded samples."""
    print("\n" + "─" * 55)
    print("  🧪 Running self-verification test...")
    print("─" * 55)

    is_match, score = voice_id.verify_file(test_file)

    if is_match:
        print(f"     Score: {score:.3f} ✅ MATCH (threshold: {voice_id.threshold})")
    else:
        print(f"     Score: {score:.3f} ❌ NO MATCH (threshold: {voice_id.threshold})")
        print("     Consider lowering VOICE_ID_THRESHOLD in config.py")

    return is_match


def main():
    print_header()

    # Confirm microphone
    pa, input_device = init_audio()

    print(f"\n  Recording {MIN_SAMPLES}–{MAX_SAMPLES} samples.")
    print("  You can stop after {MIN_SAMPLES} by typing 'done'.\n")

    wav_files = []
    total = len(ENROLLMENT_PHRASES)

    for i, phrase in enumerate(ENROLLMENT_PHRASES, 1):
        # Allow early stop after minimum
        if i > MIN_SAMPLES:
            response = input(f"\n  Record another? ({i}/{total}) [Enter=yes, 'done'=finish]: ").strip().lower()
            if response == 'done':
                break

        filename = record_sample(pa, input_device, i, total, phrase)
        if filename:
            wav_files.append(filename)
        else:
            # Retry once on failure
            print("         Retrying...")
            filename = record_sample(pa, input_device, i, total, phrase)
            if filename:
                wav_files.append(filename)

    pa.terminate()

    if len(wav_files) < MIN_SAMPLES:
        print(f"\n  ❌ Need at least {MIN_SAMPLES} samples. Got {len(wav_files)}.")
        print("     Please run the script again.")
        sys.exit(1)

    print(f"\n  📁 Recorded {len(wav_files)} samples")

    # Run enrollment
    voice_id = run_enrollment(wav_files)
    if voice_id is None:
        sys.exit(1)

    # Self-test with the first sample
    run_self_test(voice_id, wav_files[0])

    # Final summary
    print("\n" + "═" * 55)
    print("  🎉 VOICE ID ENROLLMENT COMPLETE!")
    print("═" * 55)
    print(f"  Samples:      {len(wav_files)}")
    print(f"  Embedding:    192-dimensional ECAPA-TDNN vector")
    print(f"  Voiceprint:   data/voice_id/samson_voiceprint.pt")
    print(f"  Threshold:    {voice_id.threshold}")
    print()
    print("  Enable Voice ID in config.py:")
    print("    ENABLE_VOICE_ID = True")
    print()
    print("  Or toggle it in the Jarvis app Settings sidebar.")
    print("═" * 55)
    print()


if __name__ == "__main__":
    main()
