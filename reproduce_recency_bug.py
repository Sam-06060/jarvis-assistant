
import os
import sys
import unittest
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

class TestRecencyBias(unittest.TestCase):
    def test_recency_bias(self):
        print("\n🧠 Testing Recency Bias (Topic Switching)...")
        from modules.conversation_history import ConversationHistory
        from modules.brain import AIBrain
        
        # Setup Mock History: ELO -> MODI
        history = ConversationHistory("data/test_history_recency.json")
        history.current_session["exchanges"] = [
            # Exchange 1: Elon
            {"user": "Who is Elon Musk?", "assistant": "Elon Reeve Musk is a business magnate."},
            # Exchange 2: Elon follow-up
            {"user": "How old is he?", "assistant": "Elon Musk is 54 years old."},
            # Exchange 3: TOPIC SWITCH -> Modi
            {"user": "Who is Narendra Modi?", "assistant": "Narendra Modi is the Prime Minister of India."}
        ]
        
        brain = AIBrain(context_manager=history)
        if not brain.is_online:
            print("⚠️ Ollama is offline. Skipping test.")
            return

        # Trigger Query: "How old is he?" -> Should be MODI, not ELON
        user_query = "how old is he?"
        print(f"\nCONTEXT:")
        for ex in history.current_session["exchanges"]:
            print(f"  User: {ex['user']}")
            print(f"  AI:   {ex['assistant']}")
            
        print(f"\nUser Query: '{user_query}'")
        
        refined_query = brain._contextualize_query(user_query)
        print(f"Refined Query: '{refined_query}'")
        
        if "Modi" in refined_query or "Narendra" in refined_query:
            print("✅ PASS: Correctly switched context to Modi.")
        elif "Elon" in refined_query or "Musk" in refined_query:
            print("❌ FAIL: Stuck on Elon Musk (Recency Bias).")
        else:
            print("⚠️ UNCERTAIN: " + refined_query)

if __name__ == "__main__":
    test = TestRecencyBias()
    test.test_recency_bias()
