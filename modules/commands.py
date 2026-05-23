import datetime
import os
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
from .registrar import SkillRegistrar

class _LiveContext(dict):
    """
    App-context dict that falls back to the live ServiceRegistry for any key
    that was None at CommandProcessor init time.

    This fixes the timing race where optional services (weather, music, news,
    alarms, etc.) are registered AFTER CommandProcessor.__init__() finishes,
    leaving their slots permanently None in a plain dict snapshot.
    """
    def __init__(self, registry, static_data: dict):
        super().__init__(static_data)
        self._registry = registry

    def get(self, key, default=None):
        val = super().get(key)
        if val is not None:
            return val
        # Live fallback — catches services registered after our init
        # Map context keys that differ from registry keys
        _KEY_MAP = {
            'email_manager': 'email',
            'alarm_manager': 'alarms',
        }
        registry_key = _KEY_MAP.get(key, key)
        live_val = self._registry.get(registry_key)
        if live_val is not None:
            # Cache so future lookups are instant
            self[key] = live_val
        return live_val if live_val is not None else default


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

        # 3. Parallel Skills Initialization (Nuclear Startup Phase 10)
        from concurrent.futures import ThreadPoolExecutor
        self.skills = []
        self.memory_vault = {} 
        self._tools_ready = threading.Event()
        self.tools = {}

        # Safe sentinel defaults — set before background threads so process()
        # never raises AttributeError if a command arrives before init completes.
        self.architect_skill = None
        self.command_phrases = []
        self.intent_router = None  # Replaced by real IntentRouter below
        
        # Build App Context — uses _LiveContext so late-registered services
        # (weather, music, alarms, etc.) are discovered on first use, not at boot.
        _static = {
            'registry': self.registry,
            'speech': self.registry.get('speech'),
            'brain': self.registry.get('brain'),
            'files': self.registry.get('files'),
            'system': self.registry.get('system'),
            'config': config,
            'ghost': self.registry.get('ghost') or self.ghost,
            'cursor': None,
            'visuals': self.registry.get('visuals') or self.visuals,
            'assassin': self.registry.get('assassin') or self.assassin,
            'dead_drop': self.registry.get('dead_drop') or self.dead_drop,
            'command_processor': self,
            'mimic': self.registry.get('mimic') or self.mimic,
        }
        self.app_context = _LiveContext(self.registry, _static)

        # Background: Intent Router (Start ASAP)
        def init_intent_bg():
            from modules.intent_router import IntentRouter
            self.intent_router = IntentRouter()
        threading.Thread(target=init_intent_bg, daemon=True, name="IntentInit").start()

        # Parallel Skill Loading — fault-isolated, custom-skill-aware
        def _load_all_skills():
            from core.skill_loader import load_all_skills
            _project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            instances = load_all_skills(self.app_context, _project_root)
            self.skills.extend(instances)
            # Reference specifically needed for intent router
            from modules.skills import ArchitectSkill
            self.architect_skill = next(
                (s for s in self.skills if isinstance(s, ArchitectSkill)), None
            )
            # Build speech phrase index
            threading.Thread(
                target=self._deferred_speech_context, daemon=True, name="SpeechContext"
            ).start()

        threading.Thread(target=_load_all_skills, daemon=True, name="SkillsInit").start()

        # 4. Agentic Tooling (Background)
        self.registrar = SkillRegistrar(os.path.join(os.getcwd(), "modules/agent_skills"))
        threading.Thread(target=self._deferred_tool_setup, daemon=True, name="ToolBootstrap").start()

    def _deferred_speech_context(self):
        """Builds command index and updates speech engine without blocking boot."""
        try:
            self.command_phrases = []
            for skill in self.skills:
                if hasattr(skill, 'get_phrases'):
                    phrases = skill.get_phrases()
                    if phrases: self.command_phrases.extend(phrases)
            
            self.command_phrases = sorted(list(set(self.command_phrases)))
            speech = self.registry.get('speech')
            if speech and hasattr(speech, 'set_phrases'):
                speech.set_phrases(self.command_phrases)
                logger.info(f"✅ Speech Context Primed: {len(self.command_phrases)} phrases")
        except Exception as e:
            logger.error(f"⚠️ Speech context indexing failed: {e}")

    def _deferred_tool_setup(self):
        """Background thread: loads agentic tools, UnifiedSkillRegistry, and MCPServer."""
        try:
            self._setup_tools()
            self._tools_ready.set()
            logger.info("⚡ Agentic tooling ready (background)")
        except Exception as e:
            logger.error(f"❌ Background tool setup failed: {e}")
            self.tools = {}
            self._tools_ready.set()  # Unblock waiters even on failure

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

    def _find_skill(self, skill_class_name: str):
        """
        Find a loaded skill instance by its class name.
        Used by SkillBridgeTools to invoke command skills from the agent loop.
        Example: self.cp._find_skill('CommunicationSkill')
        """
        for skill in self.skills:
            if skill.__class__.__name__ == skill_class_name:
                return skill
        return None

    def execute_tool(self, tool_name: str, tool_input: dict) -> str:
        """
        Execute a registered agent tool by name.
        Called by AgentCore._execute_action() — this is the single execution gateway.
        """
        self._tools_ready.wait(timeout=30)  # Wait for background tool loading
        tool = self.tools.get(tool_name)
        if not tool:
            return f"[!] Tool '{tool_name}' not found."
        try:
            return tool.run(tool_input)
        except Exception as e:
            logger.error(f"❌ Tool '{tool_name}' raised: {e}")
            return f"Error running '{tool_name}': {str(e)}"


    def process(self, command_text, web_search=False, from_routine=False):
        """
        Main Entry Point for Command Processing.
        Delegates all logic to the Skill System.

        Args:
            from_routine: If True, this command is a sub-step of a shortcut/routine.
                          Suppresses "switch to agentic mode" hints.
        """
        # ── LOCK SCREEN GUARD ─────────────────────────────────────────────────
        # If the Mac screen is locked, Jarvis is completely deaf.
        # No command processing, no spoken response (audible to anyone nearby).
        try:
            from modules.lock_screen_monitor import is_screen_locked
            if is_screen_locked():
                logger.debug("🔒 Command blocked — screen is locked.")
                return False
        except Exception:
            pass  # If the monitor fails to import, don't block normal operation
        # ─────────────────────────────────────────────────────────────────────

        # Store web_search flag for AI brain fallback
        self.current_web_search = web_search
        self._from_routine = from_routine
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
        Multi-signal complexity classifier.
        Returns True only when the request genuinely requires multi-step agentic execution.
        False positives send simple tasks through the expensive agent loop.
        False negatives drop complex tasks silently to brain.ask() with no tools.
        """
        text_lower = text.lower()
        word_count = len(text.split())

        # DEFINITE YES — explicit sequential/multi-step language
        multi_step_signals = [
            " and then ", " after that ", " followed by ",
            " then ", " afterwards ", " next, ", " finally, ",
        ]
        if sum(1 for s in multi_step_signals if s in text_lower) >= 1:
            return True

        # DEFINITE YES — compound question across multiple skill domains
        # e.g. "what is the time AND what is the weather in London?"
        # Detect: two or more topic nouns from different domains joined by "and"
        multi_topic_domains = [
            ("time", "date", "clock"),
            ("weather", "temperature", "forecast", "rain", "humidity"),
            ("news", "headline", "trending"),
            ("stock", "price", "market"),
            ("email", "message", "whatsapp"),
            ("reminder", "alarm", "schedule"),
        ]
        if " and " in text_lower:
            matching_domains = sum(
                1 for domain_keywords in multi_topic_domains
                if any(kw in text_lower for kw in domain_keywords)
            )
            if matching_domains >= 2:
                return True

        # DEFINITE YES — two or more distinct action verbs targeting different things
        action_verbs = [
            "search", "find", "get", "fetch", "look up",
            "email", "send", "write", "create", "generate",
            "open", "play", "calculate", "translate", "summarize",
            "analyze", "compare", "research", "book", "schedule",
        ]
        found_verbs = [v for v in action_verbs if f" {v} " in f" {text_lower} "]
        # Guard: "search and play X" is a music command, not multi-step agentic work
        music_guard = {"play", "song", "music", "spotify", "track", "album"}
        if len(found_verbs) >= 2 and not (music_guard & set(text_lower.split())):
            return True

        # DEFINITE YES — long prompt with embedded structure (likely a task, not a question)
        if word_count >= 20 and ("\n" in text or ":" in text):
            return True

        # DEFINITE YES — explicit research/analysis/report language + substance
        research_signals = [
            "compare ", "analyze ", "analyse ", "research ", "investigate ",
            "summarize this", "write a report", "make a plan",
            "pros and cons", "best options", "top options",
        ]
        if any(s in text_lower for s in research_signals) and word_count >= 8:
            return True

        # DEFINITE NO — short commands are never genuinely multi-step
        if word_count < 8:
            return False

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

        # 0.4 Agentic Force Route — intent-driven
        if config.ENABLE_AGENTIC_MODE:
            intent = intent_data.get("intent", "")

            # ── SMARTTHINGS PRIORITY BYPASS ───────────────────────────────────────
            # Hardware commands (AC on/off/temp) MUST execute via SmartThingsSkill.
            # They are NOT shell commands and must NEVER enter the agentic loop.
            # Check this BEFORE the SYSTEM_CONTROL → AgentCore gate.
            _st_skill = next(
                (s for s in self.skills if s.__class__.__name__ == "SmartThingsSkill"), None
            )
            if _st_skill and _st_skill.can_handle(cmd):
                try:
                    result = _st_skill.handle(cmd)
                    if result not in (None, False):
                        self._log_analytics(cmd, "SmartThingsSkill", True, time.time() - start_time)
                        return True
                except Exception as e:
                    logger.error(f"⚠️ SmartThings priority bypass error: {e}")
                    # Don’t fall through to AgentCore on hardware errors — return handled
                    return True
            # ────────────────────────────────────────────────────────────

            # Explicit shell execution phrasing always goes to AgentCore
            # NOTE: SYSTEM_CONTROL is intentionally excluded — hardware commands
            # (AC, SmartThings) are caught above; SYSTEM_CONTROL reaching here
            # means it’s a true OS-level command (lock screen, volume, etc.) that
            # the skill system handles better than AgentCore.
            _is_shell_cmd = bool(
                re.search(r"^(?:run|execute)\s+the\s+(?:command|script|code|shell|terminal|bash|zsh)\b", cmd.lower())
                or re.search(r"\bpython3?\b|\bnpm\b|\bnode\b|\bbash\b|\bzsh\b|\bsh\b|\bls\b|\bpip\b|\bgit\b", cmd.lower())
            )

            # Route to AgentCore if: shell command, AGENTIC_TASK intent, or architect intent
            if _is_shell_cmd or intent == "AGENTIC_TASK" or intent in ("ARCHITECT_NEW", "ARCHITECT_UPDATE_MINOR", "ARCHITECT_UPDATE_MAJOR"):
                logger.info(f"🤖 Routing to AgentCore — intent={intent}: '{cmd}'")
                return "USE_AI_BRAIN"

        try:
            # Direct Routing to Architect
            # ── AGENTIC BYPASS: When agentic mode is ON, AgentCore owns ALL complex
            # requests — the Architect skill is only active in standard mode.
            # Without this check, ARCHITECT_NEW was firing BEFORE the agentic gate
            # and hijacking every "build/create" request.
            architect_intents = [
                "ARCHITECT_NEW",
                "ARCHITECT_UPDATE_MINOR",
                "ARCHITECT_UPDATE_MAJOR"
            ]

            if not config.ENABLE_AGENTIC_MODE:
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
            else:
                intent = intent_data.get("intent")
                if intent in architect_intents:
                    logger.info(f"🤖 Agentic mode ON — Architect NLP route skipped, routing to AgentCore directly.")
                    return "USE_AI_BRAIN"
        except Exception as e:
            logger.error(f"⚠️ NLP Architect Route Error: {e}")

        # 0.45 Standard Mode graceful degradation — hint Agentic Mode for complex tasks
        # Skip this hint when executing sub-commands inside a routine/shortcut
        if not config.ENABLE_AGENTIC_MODE and not getattr(self, '_from_routine', False) and self._is_complex_query(cmd):
            speech = self.registry.get('speech')
            if speech:
                speech.speak(
                    "This task involves multiple steps and is better suited for Agentic Mode. "
                    "Please switch to Agentic Mode for full execution, sir."
                )
                logger.info(f"💡 Standard Mode: graceful agentic-hint for complex query: '{cmd}'")
            return True  # Handled (with explanation)

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
                # Tighten cutoff based on command length to prevent weak mis-matches:
                # - Very short (< 5 chars): 0.75 — very strict, almost exact match required
                # - Medium (5-20 chars):    0.80 — strict enough to block 'hello jarvis' → 'hello jarvis custom'
                # - Long (> 20 chars):      0.65 — longer commands have more signal, looser OK
                if len(cmd) < 5:
                    cutoff = 0.75
                elif len(cmd) <= 20:
                    cutoff = 0.80
                else:
                    cutoff = 0.65
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
        # GUARD: Do NOT steal shell-execution phrasing — those go to AgentCore (SYSTEM_CONTROL).
        # e.g. "run the command 'ls -la'", "execute python3 script.py", "do pip install ..."
        _is_shell_phrasing = bool(
            re.search(r"^(?:run|execute)\s+the\s+(?:command|script|code|shell|terminal|bash|zsh)\b", cmd)
            or re.search(r"\bpython3?\b|\bnpm\b|\bnode\b|\bbash\b|\bzsh\b|\bsh\b|\bls\b|\bcd\b|\bpip\b|\bgit\b", cmd)
        )
        if not _is_shell_phrasing:
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
        """
        Dynamically builds the tool registry by scanning modules/agent_skills via Registrar.
        """
        try:
            import sys
            import types
            import importlib
            import importlib.util

            # ── Step 0: Ensure modules.agent_skills package is in sys.modules ──
            # Without this, 'from .base import AgentTool' has no anchor package.
            skills_dir_abs = os.path.abspath(self.registrar.skills_dir)

            if "modules" not in sys.modules:
                mod_pkg = types.ModuleType("modules")
                mod_pkg.__path__ = [os.path.dirname(skills_dir_abs)]
                mod_pkg.__package__ = "modules"
                sys.modules["modules"] = mod_pkg

            if "modules.agent_skills" not in sys.modules:
                try:
                    # Happy path: __init__.py exists → just import normally
                    importlib.import_module("modules.agent_skills")
                except ImportError:
                    # Fallback: create a stub package so relative imports resolve
                    skills_pkg = types.ModuleType("modules.agent_skills")
                    skills_pkg.__path__ = [skills_dir_abs]
                    skills_pkg.__package__ = "modules.agent_skills"
                    sys.modules["modules.agent_skills"] = skills_pkg
                    logger.debug("🛠️ Stub package 'modules.agent_skills' registered in sys.modules")

            # ── Step 1: Scan for metadata ───────────────────────────────────
            self.registrar.scan_and_index()
            indexed_tools = self.registrar.get_tools()

            # ── Step 2: Load each tool with proper package context ──────────
            _module_cache: dict = {}  # path → already-loaded module (multi-tool files)

            for tool_name, meta in indexed_tools.items():
                try:
                    path = meta["path"]
                    class_name = meta["class_name"]

                    # Build the canonical module name from the filename
                    # e.g. .../agent_skills/research_tools.py → modules.agent_skills.research_tools
                    basename = os.path.basename(path).replace(".py", "")
                    module_name = f"modules.agent_skills.{basename}"

                    # Reuse cached module if this file was already loaded
                    # (handles files that define multiple tool classes)
                    if module_name in _module_cache:
                        module = _module_cache[module_name]
                    elif module_name in sys.modules:
                        module = sys.modules[module_name]
                    else:
                        spec = importlib.util.spec_from_file_location(
                            module_name, path,
                            submodule_search_locations=[],
                        )
                        module = importlib.util.module_from_spec(spec)
                        module.__package__ = "modules.agent_skills"
                        # Register BEFORE exec so that relative imports during
                        # module execution can find the package immediately
                        sys.modules[module_name] = module
                        try:
                            spec.loader.exec_module(module)
                        except Exception as exec_err:
                            # The module failed to load (e.g. missing import at class body).
                            # Remove the poisoned entry so sibling tools in the same file
                            # don't silently load from a broken module object.
                            sys.modules.pop(module_name, None)
                            _module_cache.pop(module_name, None)
                            raise exec_err
                        _module_cache[module_name] = module

                    # Instantiate the tool class with CommandProcessor as context
                    tool_class = getattr(module, class_name)
                    tool_instance = tool_class(self)
                    self.tools[tool_name] = tool_instance

                except Exception as e:
                    logger.error(f"❌ Failed to load tool '{tool_name}': {e}")

            loaded_count = len(self.tools)
            total_count = len(indexed_tools)
            logger.info(f"🛠️ Agentic ToolsRegistry: {loaded_count}/{total_count} tools loaded.")

            # ── Critical Tool Health Check ─────────────────────────────────
            # Warn loudly if any mission-critical tool failed to load.
            # This surfaces import errors immediately rather than causing
            # mysterious "tool not available" failures mid-task.
            CRITICAL_TOOLS = {
                "send_email":      "skill_bridge_tools.py (check imports)",
                "write_file":      "sandbox_tools.py",
                "get_market_data": "market_data_tools.py",
                "web_search":      "web_tools.py",
            }
            missing_critical = [
                f"'{t}' ({hint})" for t, hint in CRITICAL_TOOLS.items()
                if t not in self.tools
            ]
            if missing_critical:
                logger.critical(
                    f"⚠️  CRITICAL TOOLS MISSING — agentic tasks will fail silently:\n"
                    + "\n".join(f"   • {m}" for m in missing_critical)
                )



            # ── Elite Architecture: UnifiedSkillRegistry + MCPServer ──────
            try:
                from modules.skill_registry import UnifiedSkillRegistry, SKILL_METADATA
                skill_registry = UnifiedSkillRegistry()

                # Register command skills
                for skill in self.skills:
                    cname = skill.__class__.__name__
                    meta = SKILL_METADATA.get(cname, {})
                    skill_registry.register_skill(
                        id=cname.lower().replace("skill", "").strip("_"),
                        name=cname,
                        skill_obj=skill,
                        skill_type="command_skill",
                        description=getattr(skill, "description", cname),
                        domain=meta.get("domain", "general"),
                        tags=meta.get("tags", []),
                        cost_tier=meta.get("cost_tier", 1),
                        requires_network=meta.get("requires_network", False),
                        side_effects=meta.get("side_effects", []),
                    )

                # Register agent tools
                for tool_name, tool_obj in self.tools.items():
                    meta = SKILL_METADATA.get(tool_name, {})
                    skill_registry.register_skill(
                        id=tool_name,
                        name=tool_name,
                        skill_obj=tool_obj,
                        skill_type="agent_tool",
                        description=getattr(tool_obj, "description", tool_name),
                        domain=meta.get("domain", "general"),
                        tags=meta.get("tags", []),
                        cost_tier=meta.get("cost_tier", 1),
                        requires_network=meta.get("requires_network", False),
                        side_effects=meta.get("side_effects", []),
                    )

                self.registry.register("skill_registry", skill_registry)
                logger.info(
                    f"📚 UnifiedSkillRegistry: {len(skill_registry.get_by_type('command_skill'))} command skills + "
                    f"{len(skill_registry.get_by_type('agent_tool'))} agent tools registered."
                )

                # Bootstrap MCPServer from the registry
                from core.mcp import build_mcp_server_from_registry
                speech = self.registry.get("speech")
                mcp_server = build_mcp_server_from_registry(skill_registry, speech_service=speech)
                self.registry.register("mcp_server", mcp_server)
                logger.info("🔌 MCPServer bootstrapped and registered.")

            except Exception as e:
                logger.warning(f"⚠️ UnifiedSkillRegistry/MCPServer init failed: {e}")


        except Exception as e:
            logger.error(f"⚠️ Error auto-loading agent tools via Registrar: {e}")


    def get_tools_description(self) -> str:
        """Returns a string description of all available tools for the agent's prompt."""
        self._tools_ready.wait(timeout=30)  # Wait for background tool loading
        descs = []
        for name, tool in self.tools.items():
            descs.append(f"- {name}: {tool.description}")
        return "\n".join(descs)

    def get_playbooks_description(self) -> str:
        """Returns a summarized description of top playbooks for the agent's prompt."""
        self._tools_ready.wait(timeout=30)  # Wait for background tool loading
        descs = []
        playbooks = self.registrar.get_playbooks()
        
        # Limit to top 12 playbooks as "Featured Experts" to save context
        count = 0
        for name, meta in playbooks.items():
            descs.append(f"- @{name}: {meta.get('summary', '---')}")
            count += 1
            if count >= 12: break
            
        if len(playbooks) > 12:
            descs.append(f"\n... and {len(playbooks) - 12} more specialized Experts available. Use `search_awesome_skills` to discover more.")
            
        return "\n".join(descs)

    def execute_tool(self, name: str, params: Dict[str, Any]) -> str:
        """
        Dispatches tool execution with 3-tier permission-based gating.
        
        Permission tiers:
          "safe"        — Auto-execute, no prompt (read-only / internal ops)
          "write"       — Auto-execute with logging (file creation, state changes)
          "destructive" — Requires HITL approval via socket UI (irreversible actions)
        """
        self._tools_ready.wait(timeout=30)  # Wait for background tool loading
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        
        tool = self.tools[name]
        permission = getattr(tool, "permission", "safe")
        
        # ── BACKWARD COMPAT: Honor legacy tier=2 if permission wasn't explicitly set ──
        if permission == "safe" and getattr(tool, "tier", 1) == 2:
            permission = "destructive"
        
        if permission == "destructive":
            # Skip voice gate if the tool handles its OWN approval flow
            # (e.g. run_command shows the socket-based "Approve & Run" UI).
            # Asking voice AND socket confirmation is a redundant double-prompt.
            if not getattr(tool, "self_approving", False):
                speech = self.registry.get("speech")
                if speech:
                    prompt = f"I am about to use the {name.replace('_', ' ')} tool. Shall I proceed, sir?"
                    confirmed = speech.listen_confirmation(prompt)

                    if confirmed is False:
                        return "Action cancelled by user."
                    if confirmed is None:
                        return "Action cancelled: No confirmation received within timeout."
        elif permission == "write":
            # Log-only: record the action but auto-execute
            logger.info(f"📝 [WRITE] Auto-executing: {name} with {params}")
        # else: "safe" — execute silently, no logging needed
        
        try:
            logger.info(f"🚀 Executing Agent Tool: {name} with {params}")
            return tool.run(params)
        except Exception as e:
            logger.error(f"❌ Tool Execution failed ({name}): {e}")
            return f"Error executing tool {name}: {str(e)}"
