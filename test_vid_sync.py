import sys
import os
sys.path.append(os.getcwd())

from modules.audio.voice_id import VoiceID, _ensure_imports

print("Loading imports...")
_ensure_imports()

print("Creating VoiceID (synchronous)...")
vid = VoiceID()

# Call the model load synchronously to get traceback
print("Calling _load_model() directly...")
try:
    from speechbrain.inference.speaker import EncoderClassifier
    model = EncoderClassifier.from_hparams(
        source="speechbrain/spkrec-ecapa-voxceleb",
        savedir="data/models/spkrec-ecapa-voxceleb",
        run_opts={"device": "cpu"}
    )
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
