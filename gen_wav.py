import wave
import sys

filename = "test_audio.wav"
with wave.open(filename, 'wb') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(b'\x00' * 16000) # 1 sec silence
print(f"Created {filename}")
