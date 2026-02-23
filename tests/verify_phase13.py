import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jarvis import JarvisApp
from core.schemas import JarvisCommand
import logging

# Mock ServiceRegistry and components
class MockRegistry:
    @staticmethod
    def get(name):
        return None

class MockCommander:
    def process(self, command, web_search=False):
        print(f"Commander received: {command} [Web: {web_search}]")
        return True

# Monkey patch ServiceRegistry
import core.registry
core.registry.ServiceRegistry = MockRegistry

def test_handle_text_command():
    print("🧪 Testing Phase 13 Type Safety...")
    
    app = JarvisApp(None)
    # Mock things that would break without initialization
    app._update_hud = lambda x, y: print(f"HUD: [{x}] {y}")
    
    # 1. Test Legacy String
    print("\n--- Test 1: Legacy String ---")
    commander = MockCommander()
    app._handle_text_command("hello world", commander, None)
    
    # 2. Test Typed Dict (Simulating Socket Server)
    print("\n--- Test 2: Pydantic Dict ---")
    cmd = JarvisCommand(text="deploy integration", web_search=True, source="test_script")
    app._handle_text_command(cmd.dict(), commander, None)
    
    print("\n✅ Verification Complete: No Crashes observed.")

if __name__ == "__main__":
    test_handle_text_command()
