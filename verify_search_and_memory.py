
import os
import sys
import unittest
from unittest.mock import MagicMock
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class TestSearchAndMemory(unittest.TestCase):
    def setUp(self):
        # Mock requests
        self.original_post = None
        if 'requests' in sys.modules:
            self.original_post = sys.modules['requests'].post
        
    def tearDown(self):
        if self.original_post and 'requests' in sys.modules:
            sys.modules['requests'].post = self.original_post

    def test_search_quality(self):
        print("\n🌍 Testing Web Search Quality...")
        from modules.web_search import WebSearch
        search = WebSearch()
        
        # This will actually hit the network. 
        # If network is down, we skip.
        try:
             results = search.search("Who is Elon Musk", max_results=3)
             print(f"Results Found: {len(results)}")
             for res in results:
                 print(f"  - {res[:100]}...")
                 
             # Check for garbage
             garbage = ["chatgpt", "system finger 10", "login", "sign up"]
             for res in results:
                 if any(g in res.lower() for g in garbage):
                     print(f"⚠️ WARNING: Garbage result found: {res[:50]}")
                 else:
                     print("✅ Result looks OK.")
        except Exception as e:
            print(f"⚠️ Web Search Failed (Network issue?): {e}")

    def test_brain_prompt_construction(self):
        print("\n🧠 Testing Brain Prompt Construction (No Clobbering)...")
        from modules.conversation_history import ConversationHistory
        from modules.brain import AIBrain
        import config
        
        # Setup Mock History
        history = ConversationHistory("data/test_history_v2.json")
        history.current_session["exchanges"] = [
            {"user": "My name is Tony", "assistant": "Hello Tony."}
        ]
        
        # Initialize Brain
        brain = AIBrain(context_manager=history)
        
        # Mock Web Search to return something
        brain.search_engine.search = MagicMock(return_value="Elon Musk is the CEO of SpaceX.")
        
        # Mock Requests
        import requests
        mock_post = MagicMock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "Test Response"}}
        requests.post = mock_post
        
        # Execute Ask with Web Search
        brain.ask_local_ollama("Who is Elon?", web_search=True)
        
        # Inspect Payload
        args, kwargs = mock_post.call_args
        payload = kwargs['json']
        system_msg = payload['messages'][0]['content']
        
        print(f"\nConstructed System Prompt Length: {len(system_msg)}")
        
        # Verifications
        has_persona = "Sophisticated, loyal" in system_msg # Original Persona
        has_memory = "My name is Tony" in system_msg      # Memory Injection
        has_search = "Elon Musk is the CEO of SpaceX" in system_msg # Search Injection
        
        if has_persona: print("✅ Persona PRESERVED")
        else: print("❌ Persona LOST (Clobbered)")
            
        if has_memory: print("✅ Memory PRESERVED")
        else: print("❌ Memory LOST (Clobbered)")
            
        if has_search: print("✅ Search Context INJECTED")
        else: print("❌ Search Context MISSING")

if __name__ == "__main__":
    test = TestSearchAndMemory()
    test.setUp()
    test.test_brain_prompt_construction()
    test.test_search_quality()
    test.tearDown()
    print("\n✨ Verification Complete.")
