import subprocess
import re

def get_spotify_uri_spotdl_meta(query):
    print(f"Searching SpotDL Meta for: '{query}'...")
    
    try:
        # spotdl meta [query]
        cmd = [
            "./.venv/bin/spotdl", 
            "meta",
            query
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        # print("Output:", output[:500]) # Debug
        
        # Look for the URL in the output
        # It usually prints "Found X songs" then lists them with URL
        match = re.search(r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)", output)
        if match:
            track_id = match.group(1)
            uri = f"spotify:track:{track_id}"
            print(f"✅ Extracted URI: {uri}")
            return uri
        else:
            print("❌ No match in SpotDL Meta output")
            return None

    except Exception as e:
        print(f"SpotDL Error: {e}")
        return None

if __name__ == "__main__":
    uri = get_spotify_uri_spotdl_meta("blue yung kai")
    if uri:
         import subprocess
         print(f"Attempting to Play: {uri}")
         subprocess.run(["osascript", "-e", f'tell application "Spotify" to play track "{uri}"'])
