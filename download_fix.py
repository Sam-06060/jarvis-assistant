from huggingface_hub import snapshot_download
import os

print("🚀 Starting Manual Download of Whisper Turbo...")
print("This may take a few minutes depending on your internet.")
print("Model: mlx-community/whisper-turbo")

try:
    path = snapshot_download(
        repo_id="mlx-community/whisper-turbo",
        repo_type="model",
        resume_download=True  # Important: Resume where we left off
    )
    print(f"\n✅ Download Complete! Files stored at: {path}")
    print(" You can now restart Jarvis.")
except Exception as e:
    print(f"\n❌ Download Failed: {e}")
