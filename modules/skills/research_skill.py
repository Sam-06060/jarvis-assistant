from .base import Skill
import wikipedia
from wikipedia import DisambiguationError, PageError
import threading
import re
from utils.logger import get_logger

logger = get_logger()

class ResearchSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        if any(t in cmd for t in ["wikipedia", "wiki", "vicky"]):
            return True
        return self._is_video_study_command(cmd)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        assassin = self.app.get('assassin')
        brain = self.app.get('brain')
        clipboard = self.app.get('clipboard')

        # WIKIPEDIA
        if "wikipedia" in cmd or "wiki" in cmd or "vicky" in cmd:
            try:
                query = cmd.replace("wikipedia", "").replace("wiki", "").replace("vicky", "").strip()
                if not query:
                     self.speech.speak("What would you like me to research?")
                     return True

                result = wikipedia.summary(query, sentences=2)
                self.speech.speak(result)
            except DisambiguationError as e:
                options = e.options[:3]
                self.speech.speak(f"Ambiguous term. Could be {', '.join(options)}, or others.")
            except PageError:
                self.speech.speak(f"Wiki article '{query}' not found.")
            except Exception as e:
                print(f"Wikipedia Error: {e}")
                self.speech.speak("Error accessing Wikipedia.")
            return True

        # CONTENT ASSASSIN
        if assassin and self._is_video_study_command(cmd):
            def run_assassin():
                self._emit_hud_stage("FETCHING SUBTITLES", "Fetching subtitles...")
                url = self._extract_youtube_url(command)
                if not url:
                    clip_text = self._get_clipboard_text(clipboard)
                    url = self._extract_youtube_url(clip_text)

                if not url:
                    self._emit_hud_stage("IDLE", "Standing By")
                    self.speech.speak("No YouTube URL found. Copy the link and say study this video.")
                    return

                title, transcript = assassin.extract_script(url)
                if not transcript:
                    self._emit_hud_stage("IDLE", "Standing By")
                    self.speech.speak("Could not extract subtitles from that video.")
                    return
                
                self._emit_hud_stage("ANALYZING VIDEO", "Analyzing video...")
                
                prompt = (f"You are a Senior Developer. Analyze this video transcript. "
                          f"Extract all code snippets and summarize patterns.\n\n{transcript}")
                
                try:
                    summary = brain.ask(prompt) 
                except Exception as e:
                    logger.error(f"ResearchSkill brain error: {e}")
                    summary = "Error: Brain module failed."

                self._emit_hud_stage("WRITING NOTES", "Writing notes...")
                filename = assassin.create_notes(title, summary)
                self.speech.speak(f"Study notes ready: {filename}")
                self._emit_hud_stage("IDLE", "Standing By")

            threading.Thread(target=run_assassin, daemon=True).start()
            return True
            
        return False

    def _is_video_study_command(self, cmd: str) -> bool:
        patterns = [
            r"\bstudy\s+(this\s+)?video\b",
            r"\banaly[sz]e\s+(this\s+)?video\b",
            r"\bsummarize\s+(this\s+)?video\b",
            r"\bextract\s+(code|notes|transcript)\b.*\bvideo\b",
            r"\bcontent\s+assassin\b",
            r"\bstudy\s+youtube\b",
            r"\byoutube\s+(analysis|summary|notes)\b",
            r"(youtube\.com|youtu\.be)/",
        ]
        return any(re.search(pattern, cmd) for pattern in patterns)

    def _extract_youtube_url(self, text: str) -> str:
        if not text:
            return ""
        match = re.search(
            r"(https?://(?:www\.)?(?:youtube\.com/(?:watch\?v=|shorts/|embed/)[\w\-]+[^\s]*|youtu\.be/[\w\-]+[^\s]*))",
            text,
        )
        return match.group(1) if match else ""

    def _get_clipboard_text(self, clipboard):
        if clipboard and hasattr(clipboard, "get_clipboard"):
            try:
                text = clipboard.get_clipboard()
                if isinstance(text, str):
                    return text
            except Exception as e:
                logger.warning(f"ResearchSkill clipboard manager unavailable: {e}")

        try:
            import pyperclip
            return pyperclip.paste() or ""
        except Exception:
            return ""

    def _emit_hud_stage(self, header: str, detail: str):
        try:
            registry = self.app.get("registry")
            logger.debug(f"ResearchSkill HUD Stage -> {header}: {detail}")

            # Prefer app-level HUD API so socket broadcast + [HUD] logs remain consistent.
            app_obj = registry.get("app") if registry else None
            if app_obj and hasattr(app_obj, "_update_hud"):
                app_obj._update_hud(header, detail)
                return

            hud = registry.get("hud") if registry else None
            if hud:
                hud.put((header, detail))
        except Exception as e:
            logger.debug(f"ResearchSkill HUD update failed: {e}")
