from .base import Skill
import time
import subprocess
import re
import threading

class AutomationSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = [
            "read this", "summarize this", "summarize it", "summarize that", "click", "press", # Ghost Hand
            "cursor control", "mouse control", # Cursor
            "analyze", "diagnostics", "hackerman", # Visuals
            "watch this", "stop watching", "mimic", "execute", "set this as" # Mimic
        ]
        cmd = command.lower()
        return any(t in cmd for t in triggers) or bool(re.search(r"\b(?:summari[sz]e|tldr|tl;dr)\b", cmd))

    def get_phrases(self) -> list[str]:
        return [
            "read this", "summarize this", "summarize it", "summarize that", "click", "press",
            "cursor control", "mouse control",
            "analyze", "diagnostics", "hackerman",
            "watch this", "stop watching", "mimic", "execute",
            "run macro", "do macro"
        ]

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        ghost = self.app.get('ghost')
        cursor = self.app.get('cursor')
        visuals = self.app.get('visuals')

        # --- SUMMARIZE INTENT ---
        if re.search(r"\b(?:summari[sz]e|tldr|tl;dr)\b", cmd):
            try:
                text = self._extract_inline_summary_target(command)

                # If no inline payload, try active selection/window context.
                if not text and ghost:
                    text = ghost.get_selected_text() or ghost.get_window_content()

                # Clipboard fallback for typed flows where user copied content.
                if not text:
                    clipboard = self.app.get('clipboard')
                    if clipboard and hasattr(clipboard, "get_clipboard"):
                        try:
                            clip_text = clipboard.get_clipboard()
                            if isinstance(clip_text, str) and clip_text and not clip_text.lower().startswith("could not access clipboard"):
                                text = clip_text
                        except Exception:
                            pass

                if not text or text == "ERROR_PERMISSIONS":
                    self.speech.speak("I need text to summarize. Select content or include it in your command.")
                    return True

                self.speech.speak("Summarizing...")
                brain = self.app.get('brain')
                if not brain:
                    self.speech.speak("Brain module unavailable.")
                    return True

                summary = self._summarize_with_timeout(brain, text)
                self.speech.speak(summary)
                return True
            except Exception as e:
                self.speech.speak("I couldn't summarize that.")
                self.logger.error(f"Summarize Error: {e}")
                return True
        
        # --- GHOST HAND ---
        # --- GHOST HAND ---
        if ghost:
            try:
                if "read this" in cmd or "context" in cmd:
                    text = ghost.get_selected_text()
                    if not text: text = ghost.get_window_content()
                    
                    if not text or text == "ERROR_PERMISSIONS":
                        self.speech.speak("I can't read this. Check permissions.")
                        return True
                    
                    if len(text) > 1000: # Summarize
                         self.speech.speak("Summarizing...")
                         summary = self.app.get('brain').ask("Summarize: " + text[:2000])
                         self.speech.speak(summary)
                    else:
                         self.speech.speak(f"It says: {text}")
                    return True

                if "click" in cmd or "press" in cmd:
                    target = cmd.replace("click", "").replace("press", "").replace("button", "").strip()
                    if target:
                        self.speech.speak(f"Clicking {target}")
                        ghost.click_button(target)
                    return True
            except Exception as e:
                self.speech.speak("I failed to interact with the screen.")
                self.logger.error(f"Ghost Hand Error: {e}")
                return True

        # --- CURSOR ---
        if "cursor control" in cmd or "mouse control" in cmd:
             # Lazy load cursor on demand (cooling optimization)
             cp = self.app.get('command_processor')
             cursor = cp._get_cursor() if cp else None
             if cursor:
                 self.speech.speak("Visual interface active.")
                 try:
                     cursor.start()
                     self.speech.speak("Cursor control closed.")
                 except:
                     self.speech.speak("Visual system error.")
             else:
                 self.speech.speak("Cursor module unavailable.")
             return True

        # --- VISUALS ---
        if "analyze" in cmd or "hackerman" in cmd:
             self.speech.speak("Initiating deep system analysis.")
             if visuals:
                 visuals.start_hackerman_mode(duration=5)
                 time.sleep(4)
             self.speech.speak("Analysis complete. Systems optimal.")
             return True

        # --- MIMIC (The Learning Logic) ---
        # --- MIMIC (The Learning Logic) ---
        if "watch this" in cmd:
            if not self.app.get('mimic'):
                self.speech.speak("Mimic module failed to load.")
                return True
            self.speech.speak(self.app.get('mimic').start_recording())
            return "STOP_LISTENING" # Puts Jarvis to sleep (Idle) but keeps recording
        
        elif "set this as" in cmd or "set this is" in cmd or "stop watching" in cmd:
            mimic = self.app.get('mimic')
            if mimic: 
                # Robust Regex Parsing for "set this as/is <name>"
                name = "recent_macro"
                
                # Check for naming pattern
                match = re.search(r"set this (?:as|is)\s+(.+)", cmd)
                if match:
                    name = match.group(1).strip()
                    # Remove common polite suffixes if they appear at the end
                    for suffix in ["please", "thanks", "now"]:
                        if name.endswith(" " + suffix):
                            name = name[:-len(suffix)].strip()
                
                # If name is empty or just "stop watching" was used
                if not name: name = "recent_macro"
                
                print(f"DEBUG: Mimic Save - Cmd: '{cmd}' -> Name: '{name}'")
                res = mimic.stop_and_save(name)
                self.speech.speak(res)
            return True


        elif any(trigger in cmd for trigger in ["mimic", "execute", "run", "do"]):
            mimic = self.app.get('mimic')
            if not mimic:
                self.speech.speak("Mimic module unavailable.")
                return True
            
            # Extract macro name and speed modifier
            target = None
            speed = 1.0  # Default speed (1x)
            
            # Check for speed modifiers
            if "fast" in cmd:
                speed = 2.0
                cmd = cmd.replace("fast", "").strip()
            elif "slow" in cmd or "slowly" in cmd:
                speed = 0.5
                cmd = cmd.replace("slow", "").replace("slowly", "").strip()
            
            # Extract macro name
            for trigger in ["mimic", "execute macro", "execute", "run macro", "run", "do macro", "do"]:
                if cmd.startswith(trigger):
                    target = cmd[len(trigger):].strip()
                    break
            
            if not target:
                target = "recent_macro"
            
            result = mimic.execute(target, speed_multiplier=speed)
            self.speech.speak(result)
            return True

        return False

    def _summarize_with_timeout(self, brain, text: str) -> str:
        source = (text or "").strip()
        if not source:
            return "I need text to summarize."

        source = source[:6000]
        prompt = (
            "Summarize the following text in 5 to 8 concise bullet points. "
            "Preserve key facts and avoid repetition.\n\n"
            + source
        )

        result_holder = {"text": None}

        def _run():
            try:
                result_holder["text"] = brain.ask(prompt)
            except Exception as e:
                self.logger.error(f"Summarize Brain Error: {e}")
                result_holder["text"] = None

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()
        worker.join(timeout=25)

        if worker.is_alive() or not result_holder["text"]:
            return self._extractive_summary_fallback(source)

        return result_holder["text"]

    def _extractive_summary_fallback(self, text: str) -> str:
        # Lightweight fallback so summarize never stalls.
        clean = re.sub(r"\s+", " ", text).strip()
        if not clean:
            return "I couldn't extract enough text to summarize."

        sentences = re.split(r"(?<=[.!?])\s+", clean)
        picked = []
        for sentence in sentences:
            s = sentence.strip()
            if len(s) < 25:
                continue
            picked.append(s)
            if len(picked) == 5:
                break

        if not picked:
            picked = [clean[:260] + ("..." if len(clean) > 260 else "")]

        bullets = "\n".join(f"• {line}" for line in picked)
        return f"I couldn't run full AI summarization right now, so here's a quick summary:\n{bullets}"

    def _extract_inline_summary_target(self, command: str) -> str:
        text = command.strip()

        # Pattern: "<content> summarize" or "<content> summarize this/it"
        suffix_patterns = [
            r"^(?P<content>.+?)\s*(?:,|\.)?\s*(?:please\s+)?(?:summari[sz]e(?:\s+(?:this|it|that))?|tldr|tl;dr)\s*$",
        ]
        for pattern in suffix_patterns:
            match = re.match(pattern, text, flags=re.IGNORECASE)
            if match:
                content = match.group("content").strip()
                if content:
                    return content

        # Pattern: "summarize this: <content>"
        prefix_patterns = [
            r"^(?:please\s+)?(?:can you\s+|could you\s+)?(?:quickly\s+)?(?:summari[sz]e(?:\s+(?:this|it|that))?|tldr|tl;dr)\s*:?\s*(?P<content>.+)$",
        ]
        for pattern in prefix_patterns:
            match = re.match(pattern, text, flags=re.IGNORECASE)
            if match:
                content = match.group("content").strip()
                if content:
                    return content

        return ""
