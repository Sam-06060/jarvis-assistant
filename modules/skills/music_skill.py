from .base import Skill
import re
import webbrowser
import subprocess
import time

class MusicSkill(Skill):
    def get_phrases(self) -> list:
        return [
            "play some music", "play a random song", "play music", "music",
            "next track", "skip track", "previous track", "go back",
            "pause music", "stop music", "resume music", "continue music",
            "shuffle my playlist", "play on spotify", "play on apple music",
            "what is playing", "what song is this"
        ]

    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        triggers = ["music", "song", "spotify", "track", "play", "playing", "next", "previous", "skip", "pause", "resume", "shuffle"]
        return any(re.search(r'\b' + t + r'\b', cmd) for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        music_controller = self.app.get('music')
        
        # 1. YOUTUBE PLAYBACK (Explicit)
        if "play" in cmd and "youtube" in cmd:
            return self._handle_youtube(cmd)

        # 2. MUSIC CONTROLLER (Spotify/Apple Music)
        if not music_controller:
            return False

        # EXPLICIT APP SELECTION ("Play X on Y")
        if re.search(r'\bon\b', cmd) and re.search(r'\bplay\b', cmd):
            try:
                parts = re.split(r'\bon\b', cmd, maxsplit=1)
                if len(parts) >= 2:
                    song_request = parts[0].replace("play", "").strip()
                    target_app = parts[1].strip()
                    
                    self.speech.speak(f"Requesting {target_app}...")
                    result = music_controller.play_on_specific_app(song_request, target_app)
                    self.speech.speak(result)
                    return True
            except Exception as e:
                self.logger.error(f"Music on specific app error: {e}")
                self.speech.speak(f"I couldn't play that on {target_app}.")
                return True
        
        # STANDARD CONTROLS
        # STANDARD CONTROLS
        try:
            if "next" in cmd or "skip" in cmd:
                self.speech.speak(music_controller.next_track())
                return True
            elif "previous" in cmd or "go back" in cmd or "track back" in cmd:
                self.speech.speak(music_controller.previous_track())
                return True
            elif "pause" in cmd or "stop" in cmd:
                self.speech.speak(music_controller.pause())
                return True
            elif "resume" in cmd or "continue" in cmd:
                self.speech.speak(music_controller.play())
                return True
            elif "random" in cmd or "shuffle my playlist" in cmd:
                self.speech.speak(music_controller.play_random())
                return True
            elif "play some music" in cmd or "play music" in cmd:
                self.speech.speak(music_controller.play_soothing())
                return True
            elif "play" in cmd:
                # Check if it's a specific song request (more than just "play" or "play music")
                clean_cmd = cmd.replace("play", "").strip()
                if clean_cmd and clean_cmd not in ["music", "some music", "spotify", "songs"]:
                    # Assumption: Specific query resolving broad terms (mood/genre) to songs to avoid playlists
                    song_request = self._resolve_broad_query(clean_cmd)
                    
                    if song_request != clean_cmd:
                        self.speech.speak(f"Picking a track for your {clean_cmd} request: {song_request}...")
                    else:
                        self.speech.speak(f"Searching Spotify for {clean_cmd}...")
                        
                    music_controller.play_on_specific_app(song_request, "Spotify")
                else:
                    # Just Resume
                    self.speech.speak(music_controller.play())
                return True
            elif "what" in cmd and "playing" in cmd:
                self.speech.speak(music_controller.get_current_track())
                return True
        except Exception as e:
            self.logger.error(f"Music control error: {e}")
            self.speech.speak("I'm having trouble controlling the music player.")
            return True
            
        return False

    def _resolve_broad_query(self, query):
        """
        Detects broad terms (genres, moods) and resolves them to a specific song 
        to avoid Spotify Playlist landing pages which break automation.
        """
        # 1. Broad Detection Heuristics
        broad_terms = [
            "music", "jazz", "lofi", "study", "relax", "upbeat", "sad", "happy", 
            "workout", "chill", "classical", "pop", "rock", "metal", "blues", "focus"
        ]
        
        is_broad = any(term == query.lower() for term in broad_terms) or \
                   len(query.split()) < 3 and not any(x in query.lower() for x in ["by", "artist", "track"])
        
        if not is_broad:
            return query
            
        # 2. Resolve via Brain
        brain = self.app.get('brain')
        if not brain:
            return query
            
        try:
            # Stage 10: Specificity prompt
            prompt = f"The user wants to hear '{query}'. To ensure it plays on Spotify without hitting a playlist page, give me a single specific popular song title and artist that fits this mood or genre. Return ONLY the format: 'Song Title by Artist Name'."
            resolved = brain.ask(prompt)
            
            # Clean up response (some models add fluff)
            resolved = resolved.replace('"', '').replace("'", "").strip()
            if "by" in resolved.lower() and len(resolved) < 60:
                print(f"🎵 Resolved broad query '{query}' to specific track: '{resolved}'")
                return resolved
        except:
            pass
            
        return query

    def _handle_youtube(self, cmd):
        system = self.app.get('system')
        # Online check
        if system and not system.check_network():
             self.speech.speak("Internet is off.")
             return True

        song = cmd.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
        if song:
            self.speech.speak(f"Playing {song} on YouTube.")
            try:
                import pywhatkit
                # To fix the "paused video" issue, we get the URL first without opening it,
                # append the autoplay parameter, and then open it manually.
                video_url = pywhatkit.playonyt(song, open_video=False)
                
                if video_url:
                    # WORKAROUND v4: COMBO BREAKER
                    # 1. Start at 2s + Autoplay (URL)
                    # 2. Wait 3s
                    # 3. Simulate 'k' (just in case URL fails)
                    params = "&autoplay=1&t=2s"
                    
                    if "?" in video_url:
                        video_url += params
                    else:
                        video_url += "?" + params.replace("&", "", 1)
                    
                    self.logger.info(f"▶️ Playing YouTube: {video_url}")
                    # Target the YouTube Web App (Dock Application) if it exists, fallback to Safari
                    yt_app_path = "/Users/samsonganta/Applications/YouTube.app"
                    import os
                    if os.path.exists(yt_app_path):
                        subprocess.run(["open", "-a", yt_app_path, video_url])
                    else:
                        subprocess.run(["open", "-a", "Safari", video_url])
                    
                    # Force Play with Keyboard - COMMENTED OUT AS PER USER REQUEST
                    # YouTube's autoplay=1 logic is usually sufficient and this was toggling pause
                    # from pynput.keyboard import Key, Controller
                    # import time
                    # 
                    # time.sleep(3.0) 
                    # 
                    # keyboard = Controller()
                    # keyboard.press('k')
                    # keyboard.release('k')
                    
                else:
                    self.speech.speak(f"Could not find {song} on YouTube.")
                    
                return True
            except Exception as e:
                self.speech.speak("Could not play video.")
                self.logger.error(f"YouTube Error: {e}")
                
                # Fallback: Just open search results
                try:
                    import urllib.parse
                    query = urllib.parse.quote(song)
                    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                except:
                    pass
            
            return True 
        return False
