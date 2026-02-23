from duckduckgo_search import DDGS
from googlesearch import search as google_search
import traceback

print("--- TESTING DUCKDUCKGO ---")
try:
    ddgs = DDGS()
    # Test default/auto backend
    print("Attempting DDGS default...")
    results = list(ddgs.text("test query", max_results=3))
    print(f"DDGS Default Results: {len(results)}")
    for r in results:
        print(r)
except Exception:
    traceback.print_exc()

print("\n--- TESTING GOOGLE ---")
try:
    print("Attempting Google Search...")
    # Try simple iterator
    g_results = google_search("test query", num_results=3, advanced=True)
    results = list(g_results)
    print(f"Google Results: {len(results)}")
    for r in results:
        print(r)
except Exception:
    traceback.print_exc()
