import subprocess
import re

def get_spotify_uri_spotdl_url(query):
    print(f"Searching SpotDL url command for: '{query}'...")
    
    try:
        # spotdl url [query]
        cmd = [
            "./.venv/bin/spotdl", 
            "url",
            query
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        # It likely prints to stdout
        output = result.stdout + result.stderr
        # print("Output:", output) 
        
        # Look for URL
        match = re.search(r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)", output)
        if match:
            track_id = match.group(1)
            uri = f"spotify:track:{track_id}"
            print(f"✅ Extracted URI: {uri}")
            return uri
            
        print("❌ No match in SpotDL URL output")
        return None

    except Exception as e:
        print(f"SpotDL Error: {e}")
        return None

if __name__ == "__main__":
    uri = get_spotify_uri_spotdl_url("blue yung kai")
    if uri:
         import subprocess
         print(f"Attempting to Play: {uri}")
         subprocess.run(["osascript", "-e", f'tell application "Spotify" to play track "{uri}"'])
