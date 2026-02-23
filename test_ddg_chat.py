from duckduckgo_search import DDGS

try:
    print("Testing DDG Chat...")
    results = DDGS().chat("who is the current prime minister of india", model="llama-3.1-70b")
    print(f"Chat Result: {results}")
except Exception as e:
    print(f"Chat failed: {e}")
