import subprocess
import re

def get_spotify_uri_spotdl_dryrun(query):
    print(f"Searching SpotDL download --dry-run for: '{query}'...")
    
    try:
        # spotdl download [query] --dry-run
        cmd = [
            "./.venv/bin/spotdl", 
            "download",
            query,
            "--dry-run"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        # spotdl often prints to stderr or stdout
        output = result.stdout + result.stderr
        
        # Look for the URL
        match = re.search(r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)", output)
        if match:
            track_id = match.group(1)
            uri = f"spotify:track:{track_id}"
            print(f"✅ Extracted URI: {uri}")
            return uri
            
        print("❌ No match in SpotDL output")
        # print(output[:1000]) # Debug
        return None

    except Exception as e:
        print(f"SpotDL Error: {e}")
        return None

if __name__ == "__main__":
    uri = get_spotify_uri_spotdl_dryrun("blue yung kai")
    if uri:
         import subprocess
         print(f"Attempting to Play: {uri}")
         subprocess.run(["osascript", "-e", f'tell application "Spotify" to play track "{uri}"'])
