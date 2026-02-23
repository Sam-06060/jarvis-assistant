import subprocess
import time

def check_playing():
    try:
        res = subprocess.run(["osascript", "-e", 'tell application "Spotify" to player state'], capture_output=True, text=True)
        return "playing" in res.stdout.strip()
    except:
        return False

def try_key(name, script):
    print(f"👉 Trying: {name}")
    subprocess.run(["osascript", "-e", script])
    time.sleep(2)
    if check_playing():
        print(f"✅ SUCCESS! '{name}' started playback.")
        return True
    return False

def brute_force_album_play():
    print("Testing Album Page Playback Triggers...")
    
    if check_playing():
        print("⚠️ Music is already playing. Pausing first...")
        subprocess.run(["osascript", "-e", 'tell application "Spotify" to pause'])
        time.sleep(1)

    # 1. Just Enter
    script_enter = '''
    tell application "System Events"
        tell process "Spotify"
            set frontmost to true
            key code 36 -- Enter
        end tell
    end tell
    '''
    if try_key("Enter", script_enter): return

    # 2. Tab + Enter
    script_tab_enter = '''
    tell application "System Events"
        tell process "Spotify"
            set frontmost to true
            key code 48
            delay 0.1
            key code 36
        end tell
    end tell
    '''
    if try_key("Tab + Enter", script_tab_enter): return

    # 3. Tab + Tab + Enter
    script_2tab = '''
    tell application "System Events"
        tell process "Spotify"
            set frontmost to true
            key code 48
            delay 0.1
            key code 48
            delay 0.1
            key code 36
        end tell
    end tell
    '''
    if try_key("Tab + Tab + Enter", script_2tab): return

    print("❌ All attempts failed.")

if __name__ == "__main__":
    brute_force_album_play()
