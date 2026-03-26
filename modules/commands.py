import datetime
import time
import config
import threading
import difflib  # For fuzzy matching
import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

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
        from modules.skills.smartthings_skill import SmartThingsSkill
        
        # Phase 5: NLP Intent Engine
        from modules.intent_router import IntentRouter
        self.intent_router = IntentRouter()

        self.skills = []
        self.memory_vault = {} # 🧠 Stage 6: Tool Chaining Memory
        
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
        self.skills.append(SmartThingsSkill(self.app_context))
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
        
        logger.info("✅ Skills Architecture Loaded")

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
        speech = self.registry.get('speech')
        if speech and hasattr(speech, 'set_phrases'):
            speech.set_phrases(self.command_phrases)
            logger.info(f"✅ Loaded {len(self.command_phrases)} Command Phrases into Speech Context")

        # 7. Initialize Agentic Tooling (Phase 3)
        self._setup_tools()

    def _get_cursor(self):
        """Lazy-load CursorController only when needed (saves ~200MB RAM + GPU idle heat)"""
        if self._cursor_instance is None:
            try:
                from modules.cursor_control import CursorController
                self._cursor_instance = CursorController()
                self.registry.register("cursor", self._cursor_instance)
                logger.info("🎯 Cursor Control loaded on demand")
            except Exception as e:
                logger.error(f"⚠️ Cursor Control unavailable: {e}")
        return self._cursor_instance

    def process(self, command_text, web_search=False):
        """
        Main Entry Point for Command Processing.
        Delegates all logic to the Skill System.
        """
        # Store web_search flag for AI brain fallback
        self.current_web_search = web_search
        logger.debug(f"🔍 CommandProcessor.process() received web_search={web_search}")  # DEBUG
        
        try:
            return self._unsafe_process(command_text)
        except Exception as e:
            logger.error(f"❌ Error handling command: {e}")
            speech = self.registry.get('speech')
            if speech: speech.speak("I encountered an error.")
            return False

    def _is_complex_query(self, text):
        """
        Heuristic to detect if a command is multi-step or requires planning.
        Used to bypass simple skills and route to Agentic Core.
        """
        text = text.lower()
        # 1. Conjunctions/Sequencing
        conjunctions = [" and ", " then ", " after that ", " followed by ", " also ", " as well as "]
        if any(c in text for c in conjunctions):
            return True
            
        # 2. Multiple action indicators (e.g., "search and email", "find and write")
        actions = ["search", "find", "get", "look up", "tell", "email", "send", "write", "open", "play", "calculate"]
        count = sum(1 for action in actions if action in text)
        if count >= 2:
            return True
            
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
            logger.error(f"⚠️ Intent Router Error: {e}")

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
                    logger.info(f"🚀 Routing to Architect via NLP ({intent}). Brain: {reason}")

                    result = self.architect_skill.handle_intent(cmd, intent_data)
                    self._log_analytics(cmd, "architect_nlp", True, time.time() - start_time)
                    return result if result else True
        except Exception as e:
            logger.error(f"⚠️ NLP Architect Route Error: {e}")

        # 0.4 Agentic Force Route (Multi-step requests)
        if config.ENABLE_AGENTIC_MODE and self._is_complex_query(cmd):
            logger.info(f"🤖 Complexity detected in '{cmd}'. Forcing Agentic Core.")
            return "USE_AI_BRAIN"

        # 0.5 Regex Route (deterministic intent extraction)
        regex_route = self._regex_pre_route(cmd, intent_data)
        if regex_route:
            route_skill = regex_route["skill"]
            routed_cmd = regex_route.get("command", cmd)
            route_reason = regex_route.get("reason", "regex_route")
            logger.info(f"🧭 Regex Route: {route_reason} -> {route_skill} | '{routed_cmd}'")

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
                        logger.error(f"⚠️ Regex Route Skill Error ({route_skill}): {e}")
                # Fall through to normal iteration if direct route failed.
                cmd = routed_cmd

        # 1. Normalize
        # (Optional: remove punctuation manually if not handled by skills)
        
        # Bypass Fuzzy Match if SmartThings handles it natively
        ac_skill = next((s for s in self.skills if s.__class__.__name__ == "SmartThingsSkill"), None)
        bypass_fuzzy = ac_skill and ac_skill.can_handle(cmd)

        # 2. Fuzzy Match Correction
        if self.command_phrases and not bypass_fuzzy:
            # Shield common affirmations from fuzzy stripping (prevent "yes" -> "bye")
            affirmations = ["yes", "no", "ok", "okay", "yeah", "yep", "sure", "nope", "wait"]
            if cmd in affirmations:
                logger.debug(f"🛡️ Protected affirmation token from fuzzy matching: '{cmd}'")
            else:
                # Tighten cutoff for short commands to prevent weak mis-matches
                cutoff = 0.75 if len(cmd) < 5 else 0.6
                matches = difflib.get_close_matches(cmd, self.command_phrases, n=1, cutoff=cutoff)
                if matches:
                    matched_phrase = matches[0]
                    # Protection against stripping parameters:
                    if matched_phrase != cmd:
                        cmd_words = cmd.split()
                        match_words = matched_phrase.split()
                        
                        # Protection 1: Prefix matching (e.g. "execute meow")
                        is_prefix_match = len(cmd_words) > len(match_words) and cmd_words[0] == match_words[0]
                        # Protection 2: Play commands shouldn't be overridden if they have parameters
                        is_play_param = cmd_words[0] == "play" and len(cmd_words) > 1 and cmd_words != match_words and matched_phrase in ["play music", "play some music", "play a random song"]

                        if is_prefix_match or is_play_param:
                            logger.debug(f"🛡️ Protected parameterized command from fuzzy stripping: '{cmd}'")
                        else:
                            logger.info(f"✨ Fuzzy Match: '{cmd}' -> '{matched_phrase}'")
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
                logger.error(f"⚠️ Skill Error ({skill.__class__.__name__}): {e}")
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

    # --- AGENTIC TOOLING (PHASE 3) ---

    def _setup_tools(self):
        """Builds the tool registry by wrapping existing skills/functions."""
        self.tools = {}
        
        # Helper to register
        def reg(tool_class):
            t = tool_class(self)
            self.tools[t.name] = t

        # TIER 1: Safe Tools
        class WebSearchTool:
            name = "web_search"
            description = "Search the internet for information. Input: {'query': str}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                brain = self.cp.registry.get("brain")
                if not brain: return "Brain service unavailable."
                # We use the brain's search service directly to get ACTUAL context (not just open a browser)
                return brain.search_engine.search(inp['query']) or "No results found for your query."

        class MusicTool:
            name = "play_music"
            description = "Play music, songs, or artists. Input: {'action': 'play', 'song': str, 'app': str (optional, default 'Spotify')}"
            def __init__(self, cp): self.cp = cp
            def run(self, args):
                self.music = self.cp.registry.get("music")
                if not self.music: return "Music service unavailable."
                song = args.get("song")
                # CHAINED SKILL: Leverage the "Perfect" standard skill dispatcher
                # Simplified query to match user vocal patterns exactly.
                logger.info(f"🔗 Chaining MusicTool to standard Skill: play {song}")
                self.cp.process(f"play {song}")
                return f"Successfully triggered playback for: {song}"

        class WeatherTool:
            name = "get_weather"
            description = "Get current weather or forecast. Input: {'location': str}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                weather_service = self.cp.registry.get("weather")
                if not weather_service: return "Weather service unavailable."
                return weather_service.get_weather(inp.get('location', ''))

        # TIER 2: Gated Tools (Action confirmation required)
        class EmailTool:
            name = "send_email"
            description = "Send an email. Input: {'recipient': str, 'subject': str, 'body': str}. Requires confirmation."
            tier = 2
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                email_mgr = self.cp.registry.get("email")
                if not email_mgr: return "Email manager unavailable."
                recipient = inp.get('recipient', '').lower()
                # PRIORITY RECIPIENTS: Force samson06060@gmail.com if it's 'me' or variants
                self_pattern = re.compile(r"^(me|myself|user|your|samson.*)$")
                if self_pattern.match(recipient) or not recipient or "@" not in recipient:
                    from config import USER_EMAIL
                    recipient = USER_EMAIL
                
                success = email_mgr.send_email(recipient, inp['subject'], inp['body'])
                status = str(success)
                is_sent = "sent to" in status.lower() and "failed" not in status.lower()
                return status if is_sent else f"Failed to send email: {status}"

        class FileWriteTool:
            name = "write_file"
            description = "Create or overwrite a file. Input: {'path': str, 'content': str}. For user files, use absolute paths like '~/Desktop/filename.ext'. Requires confirmation."
            tier = 2
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                file_mgr = self.cp.registry.get("files")
                if not file_mgr: return "File manager service unavailable."
                success = file_mgr.create_file(inp['path'], inp['content'])
                return f"Successfully wrote content to {inp['path']}." if "✅" in str(success) else f"Failed to write to {inp['path']}: {success}"

        class SearchContactTool:
            name = "search_contact"
            description = "Search for a contact's email or phone by name. Input: {'name': str}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                contact_mgr = self.cp.registry.get("contacts")
                if not contact_mgr: return "Contact manager unavailable."
                return contact_mgr.search_contact(inp['name'])

        class WebFetchTool:
            name = "fetch_url"
            description = "Fetch full text content from a specific URL. Input: {'url': str}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                search_service = self.cp.registry.get("brain").search_engine
                return search_service.fetch_url(inp['url'])

        class WhatsAppTool:
            name = "send_whatsapp"
            description = "Send a WhatsApp message. Input: {'name': str, 'message': str}. Requires confirmation."
            tier = 2
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                contacts = self.cp.registry.get("contacts")
                if not contacts: return "Contact manager unavailable."
                return contacts.send_whatsapp_message(inp['name'], inp['message'])

        # --- NEW STAGE 1 TOOLS ---
        class ReminderTool:
            name = "manage_reminders"
            description = "Add, list, or remove reminders. Input: {'action': 'add'|'list'|'remove', 'text': str, 'time': str (optional for add)}. Example: {'action': 'add', 'text': 'Buy milk', 'time': '5pm'}"
            def __init__(self, cp): self.cp = cp
            def run(self, args):
                self.reminders = self.cp.registry.get('reminders')
                if not self.reminders: return "Reminder manager unavailable."
                action = args.get("action", "list").lower()
                if action == "list":
                    return self.reminders.get_active_reminders()
                elif action == "add":
                    msg = args.get("text")
                    when = args.get("time")
                    return self.reminders.add_reminder(msg, when)
                elif action == "remove":
                    rem_id = args.get("id")
                    return self.reminders.cancel_reminder(rem_id)
                return "Invalid action for ReminderTool."

        class AlarmTool:
            name = "manage_alarms"
            description = "Set or list alarms. Input: {'action': 'set'|'list', 'time': str}. Example: {'action': 'set', 'time': '7am'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                alarms = self.cp.registry.get('alarms')
                if not alarms: return "Alarm manager unavailable."
                action = inp.get('action', 'list').lower()
                time_str = inp.get('time', '')
                if action == 'set':
                    success, msg = alarms.set_alarm(time_str)
                    return msg
                return alarms.get_active_reminders() # Fallback for listing

        class CalculatorTool:
            name = "calculator"
            description = "Perform math calculations. Input: {'expression': str}. Example: {'expression': 'sqrt(256) * 12'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                calc = self.cp.registry.get("calculator")
                if not calc: return "Calculator service unavailable."
                result = calc.calculate(inp['expression'])
                return f"Calculation Result: {result}"

        class ACControlTool:
            name = "control_ac"
            description = "Controls the Samsung air conditioner via SmartThings. Input: {'action': 'turn_on'|'turn_off'|'set_temperature'|'set_mode'|'get_status', 'temperature_celsius': float (optional), 'mode': str (optional: 'cool'|'heat'|'auto'|'dry'|'fanOnly')}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                try:
                    from modules.smartthings import SmartThingsManager
                    manager = getattr(self.cp, '_smartthings_manager', None)
                    if not manager:
                        self.cp._smartthings_manager = SmartThingsManager()
                        manager = self.cp._smartthings_manager
                    
                    action = inp.get("action")
                    if action == "turn_on":
                        manager.turn_on()
                        return "The AC has been turned on."
                    elif action == "turn_off":
                        manager.turn_off()
                        return "The AC has been turned off."
                    elif action == "set_temperature":
                        temp = float(inp.get("temperature_celsius", 24))
                        manager.set_temperature(temp)
                        return f"The AC temperature has been set to {temp}°C."
                    elif action == "set_mode":
                        mode = inp.get("mode", "cool")
                        manager.set_mode(mode)
                        return f"The AC mode has been set to {mode}."
                    elif action == "get_status":
                        status = manager.get_status()
                        return f"AC is {status.get('switch')}. Room temp: {status.get('temperature')}°C. Setpoint: {status.get('coolingSetpoint')}°C. Mode: {status.get('airConditionerMode')}."
                    return f"Unknown AC action: '{action}'."
                except Exception as e:
                    return f"AC control failed: {str(e)}"

        class AppControlTool:
            name = "control_app"
            description = "Open or quit macOS applications. Input: {'action': 'open'|'quit', 'app_name': str}. Example: {'action': 'open', 'app_name': 'Safari'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                action = inp.get('action', 'open').lower()
                app = inp['app_name']
                try:
                    import subprocess
                    subprocess.run(["open", "-a", app], check=True, capture_output=True)
                    return f"Successfully {action}ed {app}."
                except Exception as e:
                    return f"Failed to {action} {app}. Error: {str(e)}"

        class SystemControlTool:
            name = "system_control"
            description = "Control system volume, brightness, or lock screen. Input: {'action': 'volume_up'|'volume_down'|'mute'|'lock_screen'|'brightness_up'|'brightness_down'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                action = inp['action']
                skill = self.cp._find_skill("SystemSkill")
                if not skill: return "System Skill unavailable."
                skill.handle(action.replace('_', ' '))
                return f"Successfully executed system action: {action}"

        class TranslatorTool:
            name = "translator"
            description = "Translate text. Input: {'text': str, 'target_language': str}. Example: {'text': 'Hello', 'target_language': 'French'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                translator = self.cp.registry.get("translator")
                if not translator: return "Translator service unavailable."
                result = translator.translate(inp['text'], inp['target_language'])
                return f"Translation ({inp['target_language']}): {result}"

        class ClockTool:
            name = "get_time"
            description = "Get the current time or date."
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                from datetime import datetime
                now = datetime.now()
                return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

        class ClipboardTool:
            name = "clipboard"
            description = "Read or write to the macOS clipboard. Input: {'action': 'read'|'write', 'text': str (for write)}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                clipboard_mgr = self.cp.registry.get("clipboard")
                if not clipboard_mgr: return "Clipboard manager unavailable."
                if inp.get('action') == 'write' or inp.get('action') == 'copy':
                    return clipboard_mgr.copy(inp.get('text', ''))
                return clipboard_mgr.paste()

        # --- STAGE 5: ENVIRONMENT AWARENESS ---
        class SystemStatusTool:
            name = "get_system_status"
            description = "Get detailed information about the macOS environment (battery, CPU, memory, uptime, network)."
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                sys_info = self.cp.registry.get("system")
                if not sys_info: return "System info service unavailable."
                return sys_info.get_detailed_status()

        class NowPlayingTool:
            name = "get_now_playing"
            description = "Find out what song is currently playing on Spotify or Apple Music."
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                music = self.cp.registry.get("music")
                if not music: return "Music service unavailable."
                return music.get_current_track()

        class RunningAppsTool:
            name = "get_running_apps"
            description = "Get a list of currently open applications on this Mac."
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                sys_info = self.cp.registry.get("system")
                if not sys_info: return "System info service unavailable."
                return sys_info.get_running_apps()

        # --- STAGE 6: DATA PIPING & MEMORY ---
        class StoreMemoryTool:
            name = "save_info"
            description = "Save a key piece of information to your internal memory vault for later use in this task. Input: {'key': str, 'value': str}. Example: {'key': 'news_summary', 'value': 'Apple released a new Mac...'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                key = inp.get('key', 'default')
                val = inp.get('value', '')
                self.cp.memory_vault[key] = val
                return f"✅ Saved to memory vault under '{key}'. Use 'retrieve_info' with this key later."

        class RecallMemoryTool:
            name = "retrieve_info"
            description = "Recall a piece of information you saved earlier. Input: {'key': str}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                key = inp.get('key', 'default')
                val = self.cp.memory_vault.get(key)
                if val: return f"Memory found for '{key}':\n{val}"
                return f"Error: No information found in vault for key '{key}'."

        class ListMemoryTool:
            name = "list_memory"
            description = "List all keys currently stored in your memory vault."
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                if not self.cp.memory_vault: return "The memory vault is currently empty."
                return f"Information currently in vault: {', '.join(self.cp.memory_vault.keys())}"

        # --- STAGE 7: ARCHITECT INTEGRATION (CODEBASE ACCESS) ---
        class ReadSourceFileTool:
            name = "read_source_file"
            description = "Read the content of a file in the JARVIS codebase. Input: {'path': 'relative/path/to/file.py'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                try:
                    import os
                    rel_path = inp.get('path', '').strip()
                    if not rel_path: return "Error: No path provided."
                    # Security Guard: No absolute paths, no traveling up
                    if rel_path.startswith("/") or ".." in rel_path:
                         return "Error: Absolute paths or parent directory travel (..) are forbidden."
                    
                    full_path = os.path.join(config.ROOT_DIR, rel_path)
                    if not os.path.exists(full_path):
                        return f"Error: File not found at {rel_path}"
                    
                    with open(full_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    return f"Error reading file: {str(e)}"

        class ListSourceDirTool:
            name = "list_source_dir"
            description = "List files and directories in a JARVIS source folder. Input: {'path': 'relative/path'}"
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                try:
                    import os
                    rel_path = inp.get('path', '.').strip()
                    if rel_path.startswith("/") or ".." in rel_path:
                         return "Error: Forbidden path."
                    
                    full_path = os.path.join(config.ROOT_DIR, rel_path)
                    if not os.path.isdir(full_path):
                        return f"Error: Directory not found at {rel_path}"
                    
                    items = sorted(os.listdir(full_path))
                    return f"Contents of {rel_path}:\n" + "\n".join(items)
                except Exception as e:
                    return f"Error listing directory: {str(e)}"

        class ApplySourceChangeTool:
            name = "apply_code_change"
            description = "Overwrite a source file with new code. Input: {'path': 'relative/path', 'content': 'full file content'}. Requires confirmation."
            tier = 2
            def __init__(self, cp): self.cp = cp
            def run(self, inp):
                try:
                    import os
                    rel_path = inp.get('path', '').strip()
                    content = inp.get('content', '')
                    if not rel_path or rel_path.startswith("/") or ".." in rel_path:
                         return "Error: Invalid or forbidden path."
                    
                    full_path = os.path.join(config.ROOT_DIR, rel_path)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    return f"✅ Successfully updated source file: {rel_path}"
                except Exception as e:
                    return f"Error applying change: {str(e)}"

        # Register them
        reg(WebSearchTool)
        reg(WebFetchTool)
        reg(MusicTool)
        reg(WeatherTool)
        reg(EmailTool)
        reg(FileWriteTool)
        reg(SearchContactTool)
        reg(WhatsAppTool)
        # Register NEW Stage 1 Tools
        reg(ReminderTool)
        reg(AlarmTool)
        reg(CalculatorTool)
        reg(ACControlTool)
        reg(AppControlTool)
        reg(SystemControlTool)
        reg(TranslatorTool)
        reg(ClockTool)
        reg(ClipboardTool)
        # Register STAGE 5 Tools
        reg(SystemStatusTool)
        reg(NowPlayingTool)
        reg(RunningAppsTool)
        # Register STAGE 6 Tools
        reg(StoreMemoryTool)
        reg(RecallMemoryTool)
        reg(ListMemoryTool)
        # Register STAGE 7 Tools
        reg(ReadSourceFileTool)
        reg(ListSourceDirTool)
        reg(ApplySourceChangeTool)
        logger.info(f"🛠️ Agentic ToolsRegistry initialized with {len(self.tools)} tools.")

    def get_tools_description(self) -> str:
        """Returns a string description of all available tools for the agent's prompt."""
        descs = []
        for name, tool in self.tools.items():
            descs.append(f"- {name}: {tool.description}")
        return "\n".join(descs)

    def execute_tool(self, name: str, params: Dict[str, Any]) -> str:
        """Dispatches tool execution with confirmation logic for Tier 2."""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        
        tool = self.tools[name]
        
        # Tier 2 Confirmation Gate
        if hasattr(tool, "tier") and tool.tier == 2:
            speech = self.registry.get("speech")
            if speech:
                prompt = f"I am about to use the {name.replace('_', ' ')} tool. Shall I proceed, sir?"
                confirmed = speech.listen_confirmation(prompt)
                
                if confirmed is False:
                    return "Action cancelled by user."
                if confirmed is None:
                    return "Action cancelled: No confirmation received within timeout."
        
        try:
            logger.info(f"🚀 Executing Agent Tool: {name} with {params}")
            return tool.run(params)
        except Exception as e:
            logger.error(f"❌ Tool Execution failed ({name}): {e}")
            return f"Error executing tool {name}: {str(e)}"
