import sys
import os
import time
import threading

# Add root to path
sys.path.append(os.getcwd())

# Mock Imports where we want to avoid side effects (e.g. playing audio)
class MockSpeech:
    def __init__(self):
        self.hud_queue = None
        self.is_interrupted = False
        
    def speak(self, text):
        print(f"🗣️ [JARVIS]: {text}")

    def listen_command(self, duration=5):
        return None

# Import Real Processors
from modules.commands import CommandProcessor

# Mock Sub-Systems (we only need the ones that have external side effects)
class MockSystem:
    def check_network(self): return True

class MockMimic:
    def start_recording(self): return "Recording started..."
    def stop_and_save(self, name): return f"Saved macro: {name}"

class MockDeadDrop:
    def execute_transfer(self): print("🚀 [DEAD DROP]: Transfer initiated")

def test_integration():
    print("\n🔮 --- STARTING SYSTEM INTEGRATION TEST ---")
    
    # 1. Setup Context
    speech = MockSpeech()
    brain = None # We will mock the brain response in the processor if needed or let it fail gracefully
    files = "MockFiles"
    sys_info = MockSystem()
    
    # Initialize Command Processor with real logic but injected mocks for dangerous tools
    commander = CommandProcessor(
        speech_engine=speech,
        ai_brain=brain,
        file_manager=files,
        system_info=sys_info
    )
    
    # Inject our Mocks into the commander's internal slots
    commander.mimic = MockMimic()
    commander.dead_drop = MockDeadDrop()
    # Re-build app context because it was built in __init__
    commander.app_context['mimic'] = commander.mimic
    commander.app_context['dead_drop'] = commander.dead_drop
    
    # 2. Define Test Scenario
    test_commands = [
        ("toggle internet", "Internet disconnected"), # Internet Skill
        ("toggle internet", "Internet restored"),     # Internet Skill
        ("watch this", "Recording started"),          # Automation Skill (Mimic)
        ("set this as integration_test", "Saved macro"), # Automation Skill (Mimic)
        ("drop this file", "Initializing portal")     # File Skill (Dead Drop)
    ]
    
    # 3. specific Override for manual_online_status to ensure toggle works
    commander.manual_online_status = True 

    # 4. Run Loop
    for cmd, expected_partial in test_commands:
        print(f"\n👤 [USER]: '{cmd}'")
        result = commander.process(cmd)
        
        if result:
            print(f"✅ Command Handled (Result: {result})")
        else:
            print("❌ Command Failed")

    print("\n✨ SYSTEM INTEGRATION TEST COMPLETE")

if __name__ == "__main__":
    test_integration()
