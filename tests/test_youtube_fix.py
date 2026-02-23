import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from modules.skills.music_skill import MusicSkill
from modules.speech import SpeechEngine
from modules.system_info import SystemInfo

# Mock App Context
class MockSpeech:
    def speak(self, text):
        print(f"🗣️ [MOCK SPEECH]: {text}")

class MockSystem:
    def check_network(self):
        return True

app_context = {
    'system': MockSystem(),
    'music': None # Not needed for YouTube explicit handle
}

def main():
    print("--- TEST: YouTube Search Logic ---")
    skill = MusicSkill(app_context)
    
    # Inject mock speech
    skill.speech = MockSpeech()
    
    command = "play kala chasma on youtube"
    print(f"Command: '{command}'")
    
    print("\nExecuting handler...")
    try:
        # We access the internal handler directly or via handle()
        # handle() calls _handle_youtube() if it sees "on youtube"
        result = skill.handle(command)
        
        if result:
            print("\n✅ Handler returned True")
        else:
            print("\n❌ Handler returned False")
            
    except Exception as e:
        print(f"\n❌ CRASH: {e}")

if __name__ == "__main__":
    main()
