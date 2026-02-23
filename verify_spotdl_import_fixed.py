from spotdl.utils.spotify import SpotifyClient
from spotdl.utils.search import get_search_results
import logging

# Suppress Logs
logging.basicConfig(level=logging.CRITICAL)

def test_spotdl_search(query):
    print(f"Searching SpotDL (Python API) for: '{query}'...")
    
    # 1. Initialize Client with Default Keys found in config.py
    # These are public keys used by the spotdl project
    try:
        SpotifyClient.init(
            client_id="5f573c9620494bae87890c0f08a60293",
            client_secret="212476d9b0f3472eaa762d90b19b0ba8",
            user_auth=False,
            no_cache=True, 
            headless=True
        )
        print("✅ SpotifyClient Initialized")
    except Exception as e:
        print(f"⚠️ Init Warning (might be already init): {e}")

    # 2. Search
    try:
        results = get_search_results(query)
        if results:
            first_song = results[0]
            print(f"✅ Found: {first_song.display_name}")
            print(f"🔗 URL: {first_song.url}")
            return first_song.url
        else:
            print("❌ No results found.")
            return None
    except Exception as e:
        print(f"❌ Search Error: {e}")
        return None

if __name__ == "__main__":
    url = test_spotdl_search("blue yung kai")
    if url:
        # Convert to URI
        # https://open.spotify.com/track/ID -> spotify:track:ID
        if "track/" in url:
            track_id = url.split("track/")[1].split("?")[0]
            uri = f"spotify:track:{track_id}"
            print(f"🎯 URI: {uri}")
            
            import subprocess
            print("▶️ Playing...")
            subprocess.run(["osascript", "-e", f'tell application "Spotify" to play track "{uri}"'])
