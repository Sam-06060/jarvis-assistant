import subprocess
import os
import time

# --- CONFIGURATION ---
# Define the paths to your sound effects here.
# Ensure these files exist in your 'assets' folder.
SOUND_MAP = {
    "listening": "assets/listening.wav",   # Quick "Ping"
    "processing": "assets/processing.wav", # "Computing" Hum
    "success": "assets/success.wav",       # "Ding"
    "error": "assets/error.wav",           # "Thud"
    "idle": "/System/Library/Sounds/Pop.aiff",
    "interrupt": "/System/Library/Sounds/Funk.aiff"
}

SYSTEM_SOUND_FALLBACK = {
    "listening": "/System/Library/Sounds/Glass.aiff",
    "processing": "/System/Library/Sounds/Tink.aiff",
    "success": "/System/Library/Sounds/Glass.aiff",
    "error": "/System/Library/Sounds/Basso.aiff",
    "idle": "/System/Library/Sounds/Pop.aiff",
    "interrupt": "/System/Library/Sounds/Funk.aiff"
}

def play_sound(state):
    """
    Plays a sound effect asynchronously (non-blocking) on macOS.
    Does not wait for the sound to finish.
    """
    sound_path = SOUND_MAP.get(state)
    if (not sound_path or not os.path.exists(sound_path)) and state in SYSTEM_SOUND_FALLBACK:
        sound_path = SYSTEM_SOUND_FALLBACK[state]
    
    # Validation: Don't crash if file is missing
    if not sound_path or not os.path.exists(sound_path):
        return

    try:
        # 'afplay' is the native macOS command line audio player
        subprocess.Popen(
            ["afplay", sound_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def get_system_volume():
    """Gets the current system volume (0-100) using AppleScript."""
    try:
        result = subprocess.check_output(
            ["osascript", "-e", "output volume of (get volume settings)"]
        )
        return int(result.strip())
    except:
        return 50 # Default fallback

def set_system_volume(level):
    """Sets the system volume instantly."""
    try:
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {level}"],
            stderr=subprocess.DEVNULL
        )
    except:
        pass

def get_running_media_app():
    """Detects if 'Spotify', 'Music', 'TV', or 'VLC' is running."""
    apps = ["Spotify", "Music", "TV", "VLC"]
    try:
        cmd = ["pgrep", "-x"] + apps
        # pgrep -x names... doesn't work well multi-arg on mac strictly, loop is safer
        for app in apps:
             res = subprocess.run(["pgrep", "-x", app], stdout=subprocess.DEVNULL)
             if res.returncode == 0:
                 return app
    except:
        pass
    return None

def get_active_browser():
    """Detects active browser (Chrome, Safari, Brave, Arc, Edge)."""
    browsers = ["Google Chrome", "Safari", "Brave Browser", "Arc", "Microsoft Edge"]
    try:
        cmd = 'tell application "System Events" to name of first application process whose frontmost is true'
        result = subprocess.check_output(["osascript", "-e", cmd]).decode().strip()
        if result in browsers:
            return result
    except: 
        pass
    return None

def get_app_volume(app_name):
    """Gets volume for a specific app via AppleScript."""
    try:
        cmd = f'tell application "{app_name}" to sound volume'
        result = subprocess.check_output(["osascript", "-e", cmd])
        return int(result.strip())
    except:
        return 80 # Default assumption

def set_app_volume(app_name, level):
    """Sets volume for a specific app via AppleScript."""
    try:
        cmd = f'tell application "{app_name}" to set sound volume to {level}'
        subprocess.run(["osascript", "-e", cmd], stderr=subprocess.DEVNULL)
    except:
        pass

def duck_browser_volume(browser_name, level=0.2):
    """
    Injects JavaScript to lower volume of all <video/audio> tags in the active tab.
    Target level is float (0.0 - 1.0).
    """
    js_code = f"""
    document.querySelectorAll('video, audio').forEach(el => el.volume = {level});
    """
    
    try:
        if browser_name == "Safari":
            script = f"""
            tell application "Safari"
                do JavaScript "{js_code}" in document 1
            end tell
            """
        elif browser_name == "Google Chrome" or browser_name == "Brave Browser" or browser_name == "Arc" or browser_name == "Microsoft Edge":
            script = f"""
            tell application "{browser_name}"
                execute front window active tab javascript "{js_code}"
            end tell
            """
        else:
            return False

        subprocess.run(["osascript", "-e", script], stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def duck_audio(target_app_level=12, target_sys_level=25):
    """
    AGGRESSIVE HYBRID DUCKING:
    1. Check Media Apps (Spotify/Music) -> Duck Specific App. (Sys Vol stays High)
    2. Check Browsers (Chrome/Safari) -> Inject JS to quiet Video. (Sys Vol stays High)
    3. Fallback -> Duck System Volume. (Universal Silence)
    
    Returns: State dict to restore later.
    """
    # 1. Check Media Apps
    app = get_running_media_app()
    if app:
        current_vol = get_app_volume(app)
        if current_vol > target_app_level:
            set_app_volume(app, target_app_level)
            return {"type": "app", "app": app, "volume": current_vol}
            
    # 2. Check Browsers (Active Tab only)
    browser = get_active_browser()
    if browser:
        # We blindly set it to 20%. We can't "read" previous JS volume easily without complex callbacks.
        # We'll just define restoration as setting it back to 1.0 (100%) or 0.8? 
        # Let's assume 1.0 for restoration to be safe, or just ignore restoration if user adjusted it manually?
        # Better: Restore to 1.0. Most people keep web player volume at 100%.
        if duck_browser_volume(browser, 0.2):
             return {"type": "browser", "app": browser, "volume": 1.0}
    
    # 3. Fallback: System Ducking 
    # DISABLED BY USER REQ: Jarvis must never lower system volume (which lowers his own voice).
    # If we can't find a specific app to duck, we do nothing.
    # original_vol = get_system_volume()
    # if original_vol > target_sys_level:
    #     set_system_volume(target_sys_level)
    #     return {"type": "system", "volume": original_vol}
        
    return None

def restore_audio(state):
    """Restores volume based on the saved state."""
    if not state:
        return

    type = state.get("type")
    
    if type == "app":
        set_app_volume(state["app"], state["volume"])
        
    elif type == "browser":
        # Restore Video Elements to 100%
        duck_browser_volume(state["app"], 1.0)
    
    elif type == "system":
        set_system_volume(state["volume"])
