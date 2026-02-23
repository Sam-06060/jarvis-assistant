
import os
import sys
from unittest.mock import MagicMock
from dotenv import load_dotenv

# Ensure we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    print("\n🧪 Testing Configuration Loading...")
    import config
    
    # Check if critical env vars are loaded
    if config.PICOVOICE_API_KEY == "+KL/D40l1tkfbl0WPNcQk13vHfOb6bYV9S27ANdZPcMMJ14hNthagQ==":
        print("✅ Config loaded PICOVOICE_API_KEY from .env correctly.")
    else:
        print(f"❌ Config Mismatch! Expected default key, got: {config.PICOVOICE_API_KEY}")

    if config.PHONE_MAC_ADDRESS == "14-99-3e-7a-02-b9":
        print("✅ Config loaded PHONE_MAC_ADDRESS from .env correctly.")
    else:
        print(f"❌ Config Mismatch! Expected '14-99-3e-7a-02-b9', got: {config.PHONE_MAC_ADDRESS}")

def test_memory_injection():
    print("\n🧠 Testing Memory Injection...")
    from modules.conversation_history import ConversationHistory
    from modules.brain import AIBrain
    import config
    
    # Setup Mock History
    history = ConversationHistory("data/test_history.json")
    history.current_session["exchanges"] = [
        {"user": "My name is Tony", "assistant": "Hello Tony."},
        {"user": "What is 2+2?", "assistant": "It is 4."}
    ]
    
    # Get Context Window
    ctx = history.get_context_window(limit=5)
    print(f"Stats: Generated Context Length: {len(ctx)}")
    
    if "My name is Tony" in ctx and "It is 4" in ctx:
        print("✅ ConversationHistory.get_context_window() works.")
    else:
        print("❌ ConversationHistory failed to format context.")

    # Initialize Brain with Mock History
    brain = AIBrain(context_manager=history)
    
    # We want to verified that ask_local_ollama construct the prompt correctly
    # We will mock requests.post to avoid actual API call and inspect the payload
    original_post = requests.post
    
    try:
        mock_post = MagicMock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "Test Response"}}
        requests.post = mock_post
        
        brain.ask_local_ollama("Who am I?")
        
        # Verify Payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        system_msg = payload['messages'][0]['content']
        
        # Check for Persona
        if "Sophisticated, loyal" in system_msg: 
             print("✅ Brain loaded Persona from persona.txt")
        else:
             print("❌ Brain failed to load Persona.")
             
        # Check for Memory
        if "My name is Tony" in system_msg:
            print("✅ Brain injected Memory into System Prompt.")
        else:
            print("❌ Brain failed to inject Memory.")
            
    except Exception as e:
        print(f"❌ Test Failed with Exception: {e}")
    finally:
        requests.post = original_post

if __name__ == "__main__":
    # Mock requests module for the test
    import requests
    test_config_loading()
    test_memory_injection()
    print("\n✨ Phase 3 Verification Complete.")
