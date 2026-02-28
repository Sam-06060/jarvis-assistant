import datetime
import time
import config
import threading
import difflib  # For fuzzy matching
import re

# --- OPTIONAL IMPORTS (For Context Injection Only) ---
# CursorController is lazy-loaded on demand (cooling optimization)
CursorController = None  # Placeholder, loaded by _get_cursor()
try: from .dead_drop import DeadDrop
except: DeadDrop = None
try: from .mimic import TheMimic
except: TheMimic = None
try: from .content_assassin import ContentAssassin
except: ContentAssassin = None
try: from .ghost_hand import GhostHand
except: GhostHand = None
from .visuals import VisualsManager
# -----------------------------------------------------

class CommandProcessor:
    def __init__(self, registry_class):
        
        # 1. Store Dependencies via Registry (Lazy Fetching usually better, but for now we store reference)
        self.registry = registry_class
        
        # 2. Initialize Internal Modules
        self.mimic = TheMimic() if TheMimic else None
        self._cursor_instance = None  # Lazy loaded on demand (cooling optimization)
        self.visuals = VisualsManager()
        self.dead_drop = DeadDrop() if DeadDrop else None
        self.assassin = ContentAssassin() if ContentAssassin else None
        self.ghost = GhostHand() if GhostHand else None
        
        # Register local modules so skills can access them via app_context/registry.
        # Cursor registered lazily via _get_cursor()
        if self.visuals: self.registry.register("visuals", self.visuals)
        if self.mimic: self.registry.register("mimic", self.mimic)
        if self.dead_drop: self.registry.register("dead_drop", self.dead_drop)
        
        self.manual_online_status = True

        # Phase 3: Register Internal Modules (They should really be services too)
        if self.assassin: self.registry.register("assassin", self.assassin)
        if self.ghost: self.registry.register("ghost", self.ghost)

        # 3. Initialize Skills
        #    (Imports here to prevent circular dependency during startup)
        from modules.skills import (
            SystemSkill, TimeSkill, AppControlSkill, WeatherSkill,
            MusicSkill, NewsSkill, CalculatorSkill, CommunicationSkill,
            InternetSkill, FileSkill, FocusSkill, ResearchSkill,
            AutomationSkill, ShortcutsSkill, InteractionSkill, ArchitectSkill,
            ReminderSkill, AnalyticsSkill, TranslatorSkill, AlarmSkill
        )
        
        # Phase 5: NLP Intent Engine
        from modules.intent_router import IntentRouter
        self.intent_router = IntentRouter()

        self.skills = []
        
        # 4. Build App Context for Skills (Using Registry)
        # In a perfect world, skills would just take the registry. 
        # But to be backward compatible with "self.app.get('speech')", we build a dict proxy.
        self.app_context = {
            'registry': self.registry,
            'speech': self.registry.get('speech'),
            'brain': self.registry.get('brain'),
            'files': self.registry.get('files'),
            'system': self.registry.get('system'),
            'config': config,
            'analytics': self.registry.get('analytics'),
            'weather': self.registry.get('weather'),
            'fuzzy': self.registry.get('fuzzy'),
            'music': self.registry.get('music'),
            'news': self.registry.get('news'),
            'calculator': self.registry.get('calculator'),
            'email_manager': self.registry.get('email'),  
            'contacts': self.registry.get('contacts'),
            'shortcuts': self.registry.get('shortcuts'),
            'ghost': self.registry.get('ghost') or self.ghost,
            'cursor': None,  # Lazy loaded via command_processor._get_cursor()
            'visuals': self.registry.get('visuals') or self.visuals,
            'assassin': self.registry.get('assassin') or self.assassin,
            'dead_drop': self.registry.get('dead_drop') or self.dead_drop,
            'command_processor': self,
            'clipboard': self.registry.get('clipboard'),
            'focus': self.registry.get('focus'),
            'calendar': self.registry.get('calendar'),
            'reminders': self.registry.get('reminders'),
            'mimic': self.registry.get('mimic') or self.mimic, 
            'translator': self.registry.get('translator'),
            'alarm_manager': self.registry.get('alarms')
        }
        
        # 5. Register Skills (Priority Order)
        # High Priority: Interaction (Stop/Exit/Hi) & System
        self.skills.append(InteractionSkill(self.app_context))
        self.skills.append(SystemSkill(self.app_context)) 
        self.skills.append(FocusSkill(self.app_context))
        self.skills.append(InternetSkill(self.app_context))
        
        # Mid Priority: Utility & Work
        self.skills.append(TimeSkill(self.app_context))
        self.skills.append(ReminderSkill(self.app_context))  # NEW
        self.skills.append(AnalyticsSkill(self.app_context))  # NEW
        self.skills.append(TranslatorSkill(self.app_context))  # NEW
        self.skills.append(AlarmSkill(self.app_context))
        self.skills.append(WeatherSkill(self.app_context))
        self.skills.append(NewsSkill(self.app_context))
        self.skills.append(CalculatorSkill(self.app_context))
        self.skills.append(AppControlSkill(self.app_context))
        self.skills.append(FileSkill(self.app_context))
        
        # Communication (BEFORE Architect — "add contact" must not be hijacked)
        self.skills.append(CommunicationSkill(self.app_context))
        self.skills.append(ShortcutsSkill(self.app_context))
        
        # Architect (Keep reference for Intent Router)
        self.architect_skill = ArchitectSkill(self.app_context)
        self.skills.append(self.architect_skill)  # <--- NEW Reference
        
        # Low Priority: Media & Research (Complex queries)
        self.skills.append(MusicSkill(self.app_context))
        self.skills.append(ResearchSkill(self.app_context))
        self.skills.append(AutomationSkill(self.app_context))
        
        print("✅ Skills Architecture Loaded")

        # 6. Build Command Index for Fuzzy Matching & Speech Context
        self.command_phrases = []
        for skill in self.skills:
            if hasattr(skill, 'get_phrases'):
                phrases = skill.get_phrases()
                if phrases:
                    self.command_phrases.extend(phrases)
        
        # Remove duplicates and sort
        self.command_phrases = sorted(list(set(self.command_phrases)))
        
        # Pass context to Speech Engine (if supported)
        # Pass context to Speech Engine (if supported)
        speech = self.registry.get('speech')
        if speech and hasattr(speech, 'set_phrases'):
            speech.set_phrases(self.command_phrases)
            print(f"✅ Loaded {len(self.command_phrases)} Command Phrases into Speech Context")

    def _get_cursor(self):
        """Lazy-load CursorController only when needed (saves ~200MB RAM + GPU idle heat)"""
        if self._cursor_instance is None:
            try:
                from modules.cursor_control import CursorController
                self._cursor_instance = CursorController()
                self.registry.register("cursor", self._cursor_instance)
                print("🎯 Cursor Control loaded on demand")
            except Exception as e:
                print(f"⚠️ Cursor Control unavailable: {e}")
        return self._cursor_instance

    def process(self, command_text, web_search=False):
        """
        Main Entry Point for Command Processing.
        Delegates all logic to the Skill System.
        """
        # Store web_search flag for AI brain fallback
        self.current_web_search = web_search
        print(f"🔍 CommandProcessor.process() received web_search={web_search}")  # DEBUG
        
        try:
            return self._unsafe_process(command_text)
        except Exception as e:
            print(f"❌ Error handling command: {e}")
            speech = self.registry.get('speech')
            if speech: speech.speak("I encountered an error.")
            return False

    def _unsafe_process(self, command_text):
        cmd = command_text.strip()
        start_time = time.time()
        intent_data = {"intent": "GENERAL_CONVERSATION", "confidence": 0.0}
        
        # 0. NLP INTENT ROUTING (The Brain)
        # Analyze every command with NLP first, then apply deterministic regex routing.
        try:
            context_path = self.architect_skill.last_project_path if self.architect_skill else None
            intent_data = self.intent_router.analyze(cmd, context_path)
        except Exception as e:
            print(f"⚠️ Intent Router Error: {e}")

        try:
            # Direct Routing to Architect
            architect_intents = [
                "ARCHITECT_NEW",
                "ARCHITECT_UPDATE_MINOR",
                "ARCHITECT_UPDATE_MAJOR"
            ]

            intent = intent_data.get("intent")
            if intent in architect_intents and self.architect_skill:
                if (
                    intent_data.get("confidence", 0) >= 0.75
                    and self._is_explicit_architect_request(cmd, intent_data)
                ):
                    reason = intent_data.get("reason", "No reason provided")
                    print(f"🚀 Routing to Architect via NLP ({intent}). Brain: {reason}")

                    result = self.architect_skill.handle_intent(cmd, intent_data)
                    self._log_analytics(cmd, "architect_nlp", True, time.time() - start_time)
                    return result if result else True
        except Exception as e:
            print(f"⚠️ NLP Architect Route Error: {e}")

        # 0.5 Regex Route (deterministic intent extraction)
        regex_route = self._regex_pre_route(cmd, intent_data)
        if regex_route:
            route_skill = regex_route["skill"]
            routed_cmd = regex_route.get("command", cmd)
            route_reason = regex_route.get("reason", "regex_route")
            print(f"🧭 Regex Route: {route_reason} -> {route_skill} | '{routed_cmd}'")

            if route_skill:
                skill = self._find_skill(route_skill)
                if skill:
                    try:
                        result = skill.handle(routed_cmd)
                        if result == "EXIT" or result == "STOP_LISTENING":
                            return result
                        if result:
                            self._log_analytics(cmd, f"{route_skill}_regex", True, time.time() - start_time)
                            return True
                    except Exception as e:
                        print(f"⚠️ Regex Route Skill Error ({route_skill}): {e}")
                # Fall through to normal iteration if direct route failed.
                cmd = routed_cmd

        # 1. Normalize
        # (Optional: remove punctuation manually if not handled by skills)
        
        # 2. Fuzzy Match Correction
        # If the command isn't handled by any skill directly, maybe it's a typo of a known command?
        # But we must be careful not to strip arguments from commands like "execute meow" -> "execute"
        if self.command_phrases:
            matches = difflib.get_close_matches(cmd, self.command_phrases, n=1, cutoff=0.6)
            if matches:
                matched_phrase = matches[0]
                # Protection against stripping parameters:
                # If the matched phrase is a subset of the spoken command (e.g., "execute" in "execute meow")
                # AND they start with the same word, DO NOT replace the whole string.
                if matched_phrase != cmd:
                    cmd_words = cmd.split()
                    match_words = matched_phrase.split()
                    
                    if len(cmd_words) > len(match_words) and cmd_words[0] == match_words[0]:
                        print(f"🛡️ Protected parameterized command from fuzzy stripping: '{cmd}'")
                    else:
                        print(f"✨ Fuzzy Match: '{cmd}' -> '{matched_phrase}'")
                        cmd = matched_phrase

        # 3. Iterate Skills
        for skill in self.skills:
            try:
                if skill.can_handle(cmd):
                    # Execute
                    result = skill.handle(cmd)
                    
                    # Check for Control Codes
                    if result == "EXIT" or result == "STOP_LISTENING":
                        return result
                    
                    if result: # Handled Successfully
                        try:
                            self._log_analytics(cmd, skill.__class__.__name__, True, time.time() - start_time)
                        except: pass
                        return True
            except Exception as e:
                print(f"⚠️ Skill Error ({skill.__class__.__name__}): {e}")
                # Continue to next skill
                continue
        
        # 3. Fallback to AI Brain
        self._log_analytics(cmd, "ai_brain", True, time.time() - start_time)
        return "USE_AI_BRAIN"

    def _find_skill(self, skill_name):
        for skill in self.skills:
            if skill.__class__.__name__ == skill_name:
                return skill
        return None

    def _regex_pre_route(self, command_text, intent_data):
        cmd = command_text.lower()
        intent = str(intent_data.get("intent", "")).upper()

        # --- LOCK SCREEN INTENT ---
        if re.search(r"\block\b|\bscreen\s+off\b|\bdisplay\s+off\b", cmd):
            return {"skill": "SystemSkill", "command": command_text, "reason": "lock_screen_intent"}
        if re.search(r"\b(?:brb|be\s+right\s+back|stepping\s+away|going\s+away|take\s+a\s+break)\b", cmd):
            return {"skill": "SystemSkill", "command": command_text, "reason": "lock_screen_nlp"}
        if re.search(r"\bi\s*(?:am|'m)\s+going\b.*\b(?:back|minute|bit|moment|while|sec)\b", cmd):
            return {"skill": "SystemSkill", "command": command_text, "reason": "lock_screen_nlp_going"}

        # --- SHUTDOWN / EXIT INTENT ---
        if re.search(r"\bshut\s*down\b|\bpower\s+off\b|\bterminate\b|\blog\s+off\b|\bsign\s+off\b", cmd):
            return {"skill": "InteractionSkill", "command": command_text, "reason": "shutdown_nlp"}
        if re.search(r"\bi'?m\s+done\b|\bdone\s+for\s+(?:now|today)\b|\bcall\s+it\s+a\s+day\b|\bwrap\s+(?:it\s+)?up\b|\bend\s+session\b|\btime\s+to\s+go\b", cmd):
            return {"skill": "InteractionSkill", "command": command_text, "reason": "shutdown_nlp_phrase"}

        # --- VOLUME NLP INTENT (no "volume" keyword) ---
        if re.search(r"\bmake\s+it\s+(?:louder|quieter|softer|loud|silent)\b|\bturn\s+(?:it\s+)?(?:up|down)\b", cmd):
            return {"skill": "SystemSkill", "command": command_text, "reason": "volume_nlp_intent"}
        if re.search(r"\b(?:unmute|full\s+volume|max\s+volume)\b", cmd):
            return {"skill": "SystemSkill", "command": command_text, "reason": "volume_nlp_intent"}

        # Cursor control activation using natural phrasing variants.
        if re.search(r"\b(?:turn|switch|start|enable|activate|open)\b.*\b(?:cursor|mouse)\s+control\b(?:.*\bmodule\b)?", cmd):
            return {"skill": "AutomationSkill", "command": "cursor control", "reason": "cursor_control_activation"}

        # NLP-friendly route for Content Assassin / video study requests.
        if re.search(
            r"\b(study|analy[sz]e|summari[sz]e|extract)\b.*\b(video|youtube|transcript|notes|code)\b|\bcontent\s+assassin\b|(youtube\.com|youtu\.be)/",
            cmd,
        ):
            return {"skill": "ResearchSkill", "command": command_text, "reason": "content_assassin_intent"}

        # Summarization intent with phrasing variants.
        if re.search(r"\b(?:summari[sz]e|tldr|tl;dr|briefly summarize)\b", cmd):
            return {"skill": "AutomationSkill", "command": command_text, "reason": "summarization_intent"}

        # Mimic / Macro execution intent. Bypass fuzzy matcher completely for parameterized macros.
        if re.search(r"^(?:mimic|execute|run|do)\b\s+(.+)$", cmd) or re.search(r"^(?:set this as|set this is)\s+(.+)$", cmd):
            return {"skill": "AutomationSkill", "command": command_text, "reason": "mimic_macro_execution"}

        # Explicit Google request; generic search should use normal web-search flow.
        google_patterns = [
            r"\bsearch\s+(?:on\s+)?google\b",
            r"\bgoogle\s+(?:about|on|for)\b",
            r"^\s*google\b",
        ]
        if any(re.search(pattern, cmd) for pattern in google_patterns):
            return {"skill": "InternetSkill", "command": command_text, "reason": "explicit_google_search"}

        # NLP semantic hint for web search; route through AI web-search fallback.
        if intent == "WEB_SEARCH":
            return {"skill": None, "command": command_text, "reason": "nlp_web_search"}

        return None

    def _is_explicit_architect_request(self, command_text, intent_data):
        cmd = command_text.lower().strip()
        if not cmd:
            return False

        # Never route question-like factual prompts to Architect unless strongly code-specific.
        question_prefixes = ("who ", "what ", "when ", "where ", "why ", "which ", "is ", "are ")
        has_code_noun = bool(re.search(
            r"\b(app|application|website|web app|webpage|site|project|tool|dashboard|component|api|backend|frontend|script|bot|software|system|ui|layout|screen|page)\b",
            cmd,
        ))
        if cmd.startswith(question_prefixes) and not has_code_noun:
            return False

        has_build_verb = bool(re.search(
            r"\b(build|create|scaffold|develop|code|generate|implement|program|write)\b",
            cmd,
        ))
        has_update_verb = bool(re.search(
            r"\b(update|modify|change|fix|refactor|redesign|overhaul|improve|polish|optimize|add|remove)\b",
            cmd,
        ))
        has_project_context = bool(self.architect_skill and self.architect_skill.last_project_path)

        # New build intent: must clearly mention both a creation verb and software noun.
        if has_build_verb and has_code_noun:
            return True

        # Update intent: only allow if there is active project context.
        if has_project_context and has_update_verb:
            return True

        # Last safety net for intent labels from NLP.
        intent = str(intent_data.get("intent", "")).upper()
        if intent.startswith("ARCHITECT_") and has_code_noun and (has_build_verb or has_update_verb):
            return True

        return False

    def _log_analytics(self, command, command_type, success, response_time):
        analytics = self.registry.get("analytics")
        if analytics and config.ENABLE_ANALYTICS:
            analytics.log_command(command, command_type, success, response_time)
