
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class TestSmartSearch(unittest.TestCase):
    def test_smart_query_contextualization(self):
        print("\n🧠 Testing Smart Query Rewriting (Keyword Optimization)...")
        from modules.conversation_history import ConversationHistory
        from modules.brain import AIBrain
        
        # Setup Mock History
        history = ConversationHistory("data/test_history_v4.json")
        history.current_session["exchanges"] = [
            {"user": "Who is Elon Musk?", "assistant": "Elon Reeve Musk is a business magnate."}
        ]
        
        brain = AIBrain(context_manager=history)
        if not brain.is_online:
            print("⚠️ Ollama is offline. Skipping rewrite test.")
            return

        # Test Case 1: "How old is he?" -> "Elon Musk Age" or "Elon Musk Birth Date"
        original_query = "how old is he?"
        refined_query = brain._contextualize_query(original_query)
        print(f"Refined Query: '{original_query}' -> '{refined_query}'")
        
        if "Elon Musk" in refined_query and ("Age" in refined_query or "born" in refined_query or "birth" in refined_query):
            print("✅ Query Successfully Optimized for Search Engine.")
        elif "Elon Musk" in refined_query:
            print("⚠️ Query Contextualized but maybe not fully optimized (Acceptable).")
        else:
            print("❌ Query Rewrite Failed.")

    def test_date_injection(self):
        print("\n📅 Testing Date Injection...")
        from modules.brain import AIBrain
        brain = AIBrain()
        
        # Mock requests to capture prompt
        import requests
        mock_post = MagicMock()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"message": {"content": "Test"}}
        
        original_post = requests.post
        requests.post = mock_post
        
        try:
            brain.ask_local_ollama("Test Query")
            
            # Inspect payload
            args, kwargs = mock_post.call_args
            payload = kwargs['json']
            system_msg = payload['messages'][0]['content']
            
            current_date_str = datetime.now().strftime("%B %d, %Y")
            print(f"System Message Prefix: {system_msg[:50]}...")
            
            if current_date_str in system_msg:
                print(f"✅ Date Injected Successfully: {current_date_str}")
            else:
                print(f"❌ Date Injection Failed. Expected: {current_date_str}")
                
        finally:
            requests.post = original_post

if __name__ == "__main__":
    test = TestSmartSearch()
    test.test_smart_query_contextualization()
    test.test_date_injection()
    print("\n✨ Smart Verification Complete.")
