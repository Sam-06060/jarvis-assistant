
import sys
import os
sys.path.append(os.getcwd())

from modules.intent_router import IntentRouter

def test_router():
    print("🧠 Initializing Intent Router...\n")
    router = IntentRouter()
    
    # --- STAGE 8: Semantic Subject Comparison Tests ---
    # These simulate REAL scenarios where the LLM must compare 
    # the user's request against the active project's SUBJECT.
    
    test_cases = [
        # ============ NEW PROJECT (No Context) ============
        ("Create a flappy bird game", None, "ARCHITECT_NEW"),
        ("Build a calculator app in python", None, "ARCHITECT_NEW"),
        
        # ============ NEW PROJECT (WITH Context — Different Subject) ============
        # This is THE critical test. Context is a Portfolio, but user wants a GAME.
        ("Create a flappy bird game", "/tmp/Beautiful_Portfolio_Website_20260219", "ARCHITECT_NEW"),
        ("Build a calculator app", "/tmp/Flappy_Bird_Game_20260219_125600", "ARCHITECT_NEW"),
        
        # ============ UPDATE (Same Subject) ============
        ("Make the background blue", "/tmp/Beautiful_Portfolio_Website_20260219", "ARCHITECT_UPDATE_MINOR"),
        ("Add a score counter", "/tmp/Flappy_Bird_Game_20260219_125600", "ARCHITECT_UPDATE_MINOR"),
        
        # ============ MAJOR UPDATE (Same Subject, Redesign) ============
        ("Redesign the portfolio with glassmorphism", "/tmp/Beautiful_Portfolio_Website_20260219", "ARCHITECT_UPDATE_MAJOR"),
        ("Recreate the entire UI", "/tmp/Flappy_Bird_Game_20260219_125600", "ARCHITECT_UPDATE_MAJOR"),
        
        # ============ NON-ARCHITECT ============
        ("Who is the CEO of Apple?", None, "WEB_SEARCH"),
        ("Turn up the volume", None, "SYSTEM_CONTROL"),
        ("Hello Jarvis", None, "GENERAL_CONVERSATION"),
    ]
    
    score = 0
    total = len(test_cases)
    
    for cmd, context, expected in test_cases:
        print(f"\n🧪 Testing: '{cmd}'")
        print(f"   Context: {os.path.basename(context) if context else 'None'}")
        
        result = router.analyze(cmd, context)
        intent = result.get("intent")
        confidence = result.get("confidence")
        thought = result.get("thought", "N/A")
        
        if intent == expected:
            print(f"   ✅ PASS: {intent} ({confidence})")
            score += 1
        else:
            print(f"   ❌ FAIL: Expected {expected}, Got {intent}")
            print(f"   💭 Thought: {thought[:100]}")
            
    print(f"\n{'='*50}")
    print(f"🏁 Score: {score}/{total}")
    if score == total:
        print("🎉 PERFECT SCORE! Semantic Intent Resolution is working.")
    else:
        print(f"⚠️ {total - score} test(s) failed.")
    print(f"{'='*50}")

if __name__ == "__main__":
    test_router()
