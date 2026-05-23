import sys, os
print("Importing torch...")
import torch
print("Importing torchaudio...")
import torchaudio
print("Importing speechbrain...")
try:
    from speechbrain.inference.speaker import EncoderClassifier
    print("SUCCESS importing speechbrain")
except Exception as e:
    print(f"FAILED: {e}")
