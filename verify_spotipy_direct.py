import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def test_spotipy(query):
    print(f"Searching Spotipy for: '{query}'...")
    
    try:
        # 1. Init with keys found in spotdl config
        client_credentials_manager = SpotifyClientCredentials(
            client_id="5f573c9620494bae87890c0f08a60293",
            client_secret="212476d9b0f3472eaa762d90b19b0ba8"
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        print("✅ Spotipy Initialized")
        
        # 2. Search
        # q=query, limit=1, type='track'
        results = sp.search(q=query, limit=1, type='track')
        
        items = results['tracks']['items']
        if items:
            track = items[0]
            name = track['name']
            uri = track['uri']
            print(f"✅ Found: {name}")
            print(f"🔗 URI: {uri}")
            return uri
        else:
            print("❌ No results found.")
            return None

    except Exception as e:
        print(f"❌ Spotipy Error: {e}")
        return None

if __name__ == "__main__":
    uri = test_spotipy("blue yung kai")
    if uri:
        import subprocess
        print(f"Attempting to Play: {uri}")
        subprocess.run(["osascript", "-e", f'tell application "Spotify" to play track "{uri}"'])
