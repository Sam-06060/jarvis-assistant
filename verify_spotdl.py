import subprocess
import re

def get_spotify_uri_spotdl(query):
    print(f"Searching SpotDL for: '{query}'...")
    
    try:
        # spotdl [query] --print-errors --dry-run
        # We want to see what URL it finds
        cmd = [
            "./.venv/bin/spotdl", 
            query,
            "--dry-run",
            "--print-errors"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout + result.stderr
        # print(output) # Debug
        
        # Look for https://open.spotify.com/track/...
        match = re.search(r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)", output)
        if match:
            track_id = match.group(1)
            uri = f"spotify:track:{track_id}"
            print(f"✅ Extracted URI: {uri}")
            return uri
        else:
            print("❌ No match in SpotDL output")
            return None

    except Exception as e:
        print(f"SpotDL Error: {e}")
        return None

if __name__ == "__main__":
    uri = get_spotify_uri_spotdl("blue yung kai")
    if uri:
         import subprocess
         print(f"Attempting to Play: {uri}")
         subprocess.run(["osascript", "-e", f'tell application "Spotify" to play track "{uri}"'])
