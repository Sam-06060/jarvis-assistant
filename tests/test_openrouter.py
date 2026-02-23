"""
Test OpenRouter + Multi-Pass Architecture
Run: python3 tests/test_openrouter.py
"""
import sys
import os
sys.path.append(os.getcwd())

from modules.groq_client import GroqClient

def test_connectivity():
    """Test 1: Basic connectivity to OpenRouter."""
    print("=" * 50)
    print("TEST 1: OpenRouter Connectivity")
    print("=" * 50)
    
    client = GroqClient()
    
    if not client.openrouter_available:
        print("❌ FAIL: OPENROUTER_API_KEY not set in .env")
        return False
    
    result = client.generate_code("Say 'Hello Jarvis' and nothing else.")
    
    if result and len(result) > 0:
        print(f"✅ PASS: Got response: '{result[:50]}'")
        return True
    else:
        print("❌ FAIL: No response from OpenRouter.")
        return False

def test_code_generation():
    """Test 2: Generate a simple HTML page."""
    print("\n" + "=" * 50)
    print("TEST 2: Code Generation Quality")
    print("=" * 50)
    
    client = GroqClient()
    
    system_prompt = """You are a code architect. Output files in XML format:
<file name="index.html">...</file>
<file name="style.css">...</file>"""
    
    result = client.generate_code(
        prompt="Create a simple landing page with a hero section and a button. OUTPUT RAW XML ONLY.",
        system_prompt=system_prompt
    )
    
    if not result:
        print("❌ FAIL: No response.")
        return False
    
    print(f"📏 Response: {len(result)} chars")
    
    # Check for file tags
    has_html = '<file name="index.html">' in result or "<file name='index.html'>" in result
    has_css = '<file name="style.css">' in result or "<file name='style.css'>" in result
    
    if has_html and has_css:
        print("✅ PASS: Generated index.html + style.css")
        return True
    else:
        print(f"⚠️ WARN: Missing files. Has HTML: {has_html}, Has CSS: {has_css}")
        print(f"   Preview: {result[:200]}")
        return False

def test_intent_routing():
    """Test 3: Intent Router still uses Groq (Llama) — not affected by OpenRouter change."""
    print("\n" + "=" * 50)
    print("TEST 3: Intent Router (Groq Llama)")
    print("=" * 50)
    
    from modules.intent_router import IntentRouter
    router = IntentRouter()
    
    result = router.analyze("Create a new weather app", None)
    intent = result.get("intent")
    
    if intent == "ARCHITECT_NEW":
        print(f"✅ PASS: Intent = {intent} (correct)")
        return True
    else:
        print(f"❌ FAIL: Intent = {intent} (expected ARCHITECT_NEW)")
        return False

if __name__ == "__main__":
    print("🧪 OpenRouter Integration Tests\n")
    
    results = []
    results.append(("Connectivity", test_connectivity()))
    results.append(("Code Generation", test_code_generation()))
    results.append(("Intent Routing", test_intent_routing()))
    
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    
    print(f"\n🏁 Score: {passed}/{total}")
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️ Some tests failed. Check output above.")
