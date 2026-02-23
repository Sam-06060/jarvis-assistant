import sys
import os

sys.path.append(os.getcwd())
import config
from modules.brain import AIBrain

print("🧠 Testing AIBrain...")

try:
    brain = AIBrain()
    print(f"✅ Brain Initialized. Model: {brain.local_model}")
    
    online_status = brain.is_online
    print(f"✅ is_online check: {online_status}")
    
    # We won't test full generation to avoid slow Ollama waits, 
    # but strictly checking the attribute existence is what failed before.
    
except Exception as e:
    print(f"❌ Brain Failed: {e}")
    sys.exit(1)
