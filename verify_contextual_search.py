
import os
import sys
import unittest
from unittest.mock import MagicMock
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class TestContextualSearch(unittest.TestCase):
    def test_query_contextualization(self):
        print("\n🧠 Testing Query Contextualization (Rewriting)...")
        from modules.conversation_history import ConversationHistory
        from modules.brain import AIBrain
        
        # Setup Mock History
        history = ConversationHistory("data/test_history_v3.json")
        history.current_session["exchanges"] = [
            {"user": "Who is Elon Musk?", "assistant": "Elon Reeve Musk is a business magnate."}
        ]
        
        # Initialize Brain
        brain = AIBrain(context_manager=history)
        
        # Determine if Ollama is running
        if not brain.is_online:
            print("⚠️ Ollama is offline. Skipping actual rewrite test.")
            return

        # Test Case 1: Ambiguous Query
        original_query = "how old is he?"
        print(f"\nUser Query: '{original_query}'")
        
        refined_query = brain._contextualize_query(original_query)
        print(f"Refined Query: '{refined_query}'")
        
        if "Elon Musk" in refined_query or "Elon" in refined_query:
            print("✅ Query Successfully Rewritten with Context.")
        else:
            print("❌ Query Rewrite Failed (Context Missing).")

        # Test Case 2: Unambiguous Query (Should not change much)
        original_query_2 = "What is the capital of France?"
        print(f"\nUser Query: '{original_query_2}'")
        refined_query_2 = brain._contextualize_query(original_query_2)
        print(f"Refined Query: '{refined_query_2}'")
        
        if "France" in refined_query_2:
             print("✅ Query Preserved (Correctly).")

if __name__ == "__main__":
    import requests
    test = TestContextualSearch()
    test.test_query_contextualization()
    print("\n✨ Verification Complete.")
