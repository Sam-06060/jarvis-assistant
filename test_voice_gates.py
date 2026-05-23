import sys
import os
import time
sys.path.append(os.getcwd())

print("Testing Cobra VAD...")
from modules.audio.cobra_vad import CobraVAD
vad = CobraVAD()
print(f"Cobra VAD init result: {'SUCCESS' if vad.cobra else 'FAILED'}")

print("\nTesting Voice ID (ECAPA-TDNN) load...")
from modules.audio.voice_id import VoiceID
vid = VoiceID()
vid.is_ready.wait(timeout=60)
print(f"Voice ID load result: {'SUCCESS' if vid.model else 'FAILED'}")

