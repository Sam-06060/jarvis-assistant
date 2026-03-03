import subprocess
import random
import time

class MusicController:
    """Control Apple Music and Spotify"""
    
    def __init__(self):
        # We don't cache current_app anymore, checking completely dynamically
        pass
    
    @property
    def current_app(self):
        """Dynamically detect which music app is running (Default: Spotify)"""
        try:
            # 1. Check if Spotify is running (Priority 1)
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to (name of processes) contains "Spotify"'],
                capture_output=True, text=True
            )
            if result.stdout.strip() == "true":
                return "Spotify"
            
            # 2. Check if Apple Music is running (Priority 2)
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to (name of processes) contains "Music"'],
                capture_output=True, text=True
            )
            if result.stdout.strip() == "true":
                return "Music"
            
            # 3. Default Validation: Return "Spotify" IF it exists, else "Music"
            # (Use 'mdfind' to check installation roughly or just default)
            return "Spotify"
            
        except:
            return "Spotify"

    def play_on_specific_app(self, song, app_name):
        """Play specific song on specific app"""
        app_name = app_name.lower()
        
        # --- SPOTIFY ---
        if "spotify" in app_name:
            try:
                subprocess.run(["open", "-a", "Spotify"])
                time.sleep(1) # Wait for launch
                
                # Dynamic Search & Auto-Play via AppleScript Native Play
                # Construct specific query. If " by " in song, make it stricter
                query = song
                if " by " in song:
                    parts = song.split(" by ")
                    query = f"track:{parts[0]} artist:{parts[1]}"
                
                search_uri = f"spotify:search:{query.replace(' ', '%20')}"
                
                # Open Search Page (Using 'open' prevents Spotify from auto-playing a radio mix before the keystrokes hit)
                subprocess.run(["open", search_uri])
                
                time.sleep(1.5) # Wait for UI to load
                
                # Force Play using the user's explicit UI Scripting flow
                try:
                    script_ui = '''
                    tell application "System Events"
                        tell process "Spotify"
                            set frontmost to true
                            delay 0.2
                            key code 48 -- Tab (Exit Search Bar focus)
                            delay 0.2
                            keystroke "a" using command down -- Select All
                            delay 0.2
                            key code 36 -- Enter (Navigate into Top Result)
                            delay 0.8 -- Wait 0.5-1s
                            key code 36 -- Enter (Confirm Playback)
                        end tell
                    end tell
                    '''
                    subprocess.run(["osascript", "-e", script_ui], check=True)
                    return f"Playing {song} on Spotify."
                except subprocess.CalledProcessError:
                    return f"I opened {song} on Spotify. Please grant me Accessibility permissions in System Settings so I can click play for you."
                
            except Exception as e:
                return f"Could not play on Spotify: {e}"

        # --- APPLE MUSIC ---
        elif "music" in app_name and "apple" in app_name or app_name == "music":
            try:
                subprocess.run(["open", "-a", "Music"])
                # Apple Music needs 'play track X' but reliable search is hard via script
                # We'll try a basic filter command
                script = f'''
                tell application "Music"
                    play (first track whose name contains "{song}")
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                return f"Playing {song} on Apple Music."
            except:
                return f"Could not find '{song}' in your Apple Music library."

        # --- OTHER APPS (Generic Launch or Web) ---
        else:
            # 1. Check for Common Websites (YouTube, etc)
            if "youtube" in app_name:
                 query = song.replace(' ', '+')
                 url = f"https://www.youtube.com/results?search_query={query}"
                 subprocess.run(["open", url])
                 return f"Opening search for {song} on YouTube..."
                 
            # 2. Check if app exists
            try:
                # Use mdfind to locate app bundle
                result = subprocess.run(
                    ["mdfind", f"kMDItemKind == 'Application' && kMDItemFSName == '{app_name}.app'"],
                    capture_output=True, text=True
                )
                paths = result.stdout.strip().split('\n')
                
                if paths and paths[0]:
                    subprocess.run(["open", paths[0]])
                    return f"Launched {app_name.title()}. (I cannot control playback for this app yet)."
                else:
                    return f"Could not find an app named '{app_name}'."
            except Exception as e:
                return f"Error launching {app_name}: {e}"
    
    def play(self):
        """Play music"""
        try:
            script = f'tell application "{self.current_app}" to play'
            subprocess.run(["osascript", "-e", script], check=False)
            return "Playing music."
        except Exception as e:
            return f"Could not play: {str(e)}"
    
    def pause(self):
        """Pause music"""
        try:
            script = f'tell application "{self.current_app}" to pause'
            subprocess.run(["osascript", "-e", script], check=False)
            return "Music paused."
        except Exception as e:
            return f"Could not pause: {str(e)}"
    
    def play_pause(self):
        """Toggle play/pause"""
        try:
            script = f'tell application "{self.current_app}" to playpause'
            subprocess.run(["osascript", "-e", script], check=False)
            return "Toggled play/pause."
        except Exception as e:
            return f"Could not toggle: {str(e)}"
    
    def next_track(self):
        """Skip to next track"""
        try:
            script = f'tell application "{self.current_app}" to next track'
            subprocess.run(["osascript", "-e", script], check=False)
            return "Skipped to next track."
        except Exception as e:
            return f"Could not skip: {str(e)}"
    
    def previous_track(self):
        """Smart Previous: Go to start if >3s, else go to previous"""
        try:
            # Check player position first
            script = f'tell application "{self.current_app}" to player position'
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            
            position = 0.0
            if result.returncode == 0 and result.stdout.strip():
                try: position = float(result.stdout.strip())
                except: pass
            
            # Logic: If > 3 seconds, one click goes to start. Two clicks goes to previous.
            if position > 3.0:
                script = f'''
                tell application "{self.current_app}"
                    previous track
                    delay 0.1
                    previous track
                end tell
                '''
            else:
                script = f'tell application "{self.current_app}" to previous track'
                
            subprocess.run(["osascript", "-e", script], check=False)
            return "Playing previous track."
        except Exception as e:
            return f"Could not go back: {str(e)}"
    
    def play_random(self):
        """Play a random song (Shuffle + Next)"""
        try:
            if self.current_app == "Spotify":
                script = '''
                tell application "Spotify"
                    activate
                    set shuffling to true
                    play
                    next track
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                
                # Check if it actually started playing
                check_script = 'tell application "Spotify" to get player state'
                res = subprocess.run(["osascript", "-e", check_script], capture_output=True, text=True)
                
                if "playing" not in res.stdout.lower():
                    # Fallback: Play a random popular playlist if queue was empty
                    genres = [
                        "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M", # Today's Top Hits
                        "spotify:playlist:37i9dQZF1DX0XUsuxWHRQd", # RapCaviar
                        "spotify:playlist:37i9dQZF1DX4sWSpwq3LiO", # Peaceful Piano
                        "spotify:playlist:37i9dQZF1DWZeKCadgRdKQ", # Deep Focus
                        "spotify:playlist:37i9dQZF1DWWQRwui0ExPn"  # Lofi Beats
                    ]
                    random_uri = random.choice(genres)
                    play_script = f'tell application "Spotify" to play track "{random_uri}"'
                    subprocess.run(["osascript", "-e", play_script], check=False)
                    return "Playing a random playlist."
                
                return "Playing a random song."
            else:
                script = '''
                tell application "Music"
                    set shuffle enabled to true
                    play
                    next track
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                return "Playing a random song."
        except Exception as e:
            return f"Error playing random: {str(e)}"
            
    def shuffle_playlist(self):
        """Shuffle current context"""
        return self.play_random()
    
    def play_soothing(self):
        """Play soothing music on Spotify/Music (Direct URIs)"""
        try:
            if self.current_app == "Spotify":
                moods = [
                    "spotify:playlist:37i9dQZF1DWZeKCadgRdKQ", # Deep Focus
                    "spotify:playlist:37i9dQZF1DWWQRwui0ExPn", # Lofi Beats
                    "spotify:playlist:37i9dQZF1DX4sWSpwq3LiO", # Peaceful Piano
                    "spotify:playlist:37i9dQZF1DX8Uebhn9wzrS", # Chill Lofi Study Beats
                    "spotify:playlist:37i9dQZF1DX3Ogo9pFvBkY"  # Ambient Study
                ]
                
                random_uri = random.choice(moods)
                
                script = f'''
                tell application "Spotify"
                    activate
                    set shuffling to true
                    play track "{random_uri}"
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                return "Playing soothing music."
            else:
                # Apple Music Fallback
                script = '''
                tell application "Music"
                    activate
                    play playlist "Chill"
                end tell
                '''
                subprocess.run(["osascript", "-e", script], check=False)
                return "Playing soothing music on Apple."
            
        except Exception as e:
            return f"Could not play soothing music: {str(e)}"

    def get_current_track(self):
        """Get currently playing track info"""
        try:
            if self.current_app == "Spotify":
                script = '''
                tell application "Spotify"
                    set trackName to name of current track
                    set artistName to artist of current track
                    return trackName & " by " & artistName
                end tell
                '''
            else:  # Apple Music
                script = '''
                tell application "Music"
                    set trackName to name of current track
                    set artistName to artist of current track
                    return trackName & " by " & artistName
                end tell
                '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return f"Now playing: {result.stdout.strip()}"
            return "No track is currently playing."
            
        except Exception as e:
            return f"Could not get track info: {str(e)}"
    
    def set_volume(self, level):
        """Set music volume (0-100)"""
        try:
            level = max(0, min(100, int(level)))
            script = f'tell application "{self.current_app}" to set sound volume to {level}'
            subprocess.run(["osascript", "-e", script], check=False)
            return f"Music volume set to {level}%."
        except Exception as e:
            return f"Could not set volume: {str(e)}"
    
    def volume_up(self):
        """Increase volume"""
        return self.set_volume(75)
    
    def volume_down(self):
        """Decrease volume"""
        return self.set_volume(40)
    
    def shuffle_on(self):
        """Enable shuffle"""
        try:
            if self.current_app == "Spotify":
                script = 'tell application "Spotify" to set shuffling to true'
                subprocess.run(["osascript", "-e", script], check=False)
                return "Shuffle enabled."
            elif self.current_app == "Music":
                script = 'tell application "Music" to set shuffle enabled to true'
                subprocess.run(["osascript", "-e", script], check=False)
                return "Shuffle enabled."
            return "Shuffle control failed."
        except Exception as e:
            return f"Could not enable shuffle: {str(e)}"
    
    def shuffle_off(self):
        """Disable shuffle"""
        try:
            if self.current_app == "Spotify":
                script = 'tell application "Spotify" to set shuffling to false'
                subprocess.run(["osascript", "-e", script], check=False)
                return "Shuffle disabled."
            elif self.current_app == "Music":
                script = 'tell application "Music" to set shuffle enabled to false'
                subprocess.run(["osascript", "-e", script], check=False)
                return "Shuffle disabled."
            return "Shuffle control failed."
        except Exception as e:
            return f"Could not disable shuffle: {str(e)}"
    
    def repeat_on(self):
        """Enable repeat"""
        try:
            if self.current_app == "Spotify":
                 script = 'tell application "Spotify" to set repeating to true'
                 subprocess.run(["osascript", "-e", script], check=False)
                 return "Repeat enabled."
            elif self.current_app == "Music":
                script = 'tell application "Music" to set song repeat to all'
                subprocess.run(["osascript", "-e", script], check=False)
                return "Repeat enabled."
            return "Repeat control failed."
        except Exception as e:
            return f"Could not enable repeat: {str(e)}"
    
    def repeat_off(self):
        """Disable repeat"""
        try:
            if self.current_app == "Spotify":
                 script = 'tell application "Spotify" to set repeating to false'
                 subprocess.run(["osascript", "-e", script], check=False)
                 return "Repeat disabled."
            elif self.current_app == "Music":
                script = 'tell application "Music" to set song repeat to off'
                subprocess.run(["osascript", "-e", script], check=False)
                return "Repeat disabled."
            return "Repeat control failed."
        except Exception as e:
            return f"Could not disable repeat: {str(e)}"