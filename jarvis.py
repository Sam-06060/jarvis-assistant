import sys
import time
import threading
import multiprocessing
import os
import io
import signal
import queue
import json
import atexit

# --- 1. SETUP LOGGING (Critical First Step) ---
# Must happen before other major imports to capture import-time errors
from utils.logger import JarvisLogger
logger = JarvisLogger.setup_logger()

# Phase 4: Smart Proxy
from core.proxy import ServiceProxy

logger.info("🚀 Starting Jarvis System...")

import subprocess
import re
import config
from core.registry import ServiceRegistry
from core.events import EventManager

# --- MODULE IMPORTS ---
try:
    from modules.speech import SpeechEngine
    from modules.brain import AIBrain
    from modules.file_manager import FileManager
    from modules.system_info import SystemInfo
    from modules.commands import CommandProcessor
    from modules.health_checker import HealthChecker
    from modules.analytics import Analytics
    from modules.conversation_history import ConversationHistory
    from modules.hotkey_manager import HotkeyManager
    from utils.context_manager import ContextManager
    from utils.fuzzy_matcher import FuzzyMatcher
    from utils.offline_cache import OfflineCache
    from utils.audio_manager import play_sound, duck_audio, restore_audio

    # HUD & Sockets
    from modules.socket_server import JarvisSocketServer
except ImportError as e:
    logger.critical(f"❌ Critical Import Error: {e}")
    sys.exit(1)

# --- OPTIONAL MODULES (Graceful Degradation) ---
def safe_import(module_name, class_name, config_flag=None):
    """Refactored safe import helper with logging"""
    if config_flag is not None and not config_flag:
        logger.debug(f"ℹ️ Module skipped (Config Disabled): {module_name}")
        return None
    
    try:
        # Dynamic import logic could go here, but for now we stick to explicit imports
        # to ensure static analysis tools work. 
        # This function is just a placeholder for the logic below.
        pass
    except Exception as e:
        logger.warning(f"⚠️ Failed to load optional module {module_name}: {e}")
        return None

# (Imports remain similar but we will instantiate them safely in the class)

class JarvisApp:
    def __init__(self, hud_queue):
        self.hud_queue = hud_queue
        # Register queue with logger so logs can flow to HUD
        JarvisLogger.register_hud_queue(hud_queue)
        
        self.is_running = True
        self.api_server = None
        self._last_hud_header = None
        self._last_state_cue_at = 0.0
        
        # Phase 2: Register Core Config/Status
        ServiceRegistry.register("hud", hud_queue)
        ServiceRegistry.register("app", self)
        
        self.agent = None
        
    def initialize_systems(self):
        """Initialize all subsystems with error handling"""
        logger.info("🔧 Initializing Subsystems...")
        
        # 🔐 Check all macOS permissions FIRST (before any module needs them)
        try:
            from utils.permission_checker import check_all_permissions
            check_all_permissions()
        except Exception as e:
            logger.warning(f"⚠️ Permission checker failed: {e}")
        
        self._update_hud("BOOTING", "Initializing Modules")
        
        try:
            # 1. Core Systems
            # Initialize & Register via Registry
            speech = SpeechEngine(hud_queue=self.hud_queue)
            ServiceRegistry.register("speech", speech)
            
            context = ContextManager()
            ServiceRegistry.register("context", context)

            if config.ENABLE_FUZZY_MATCHING:
                fuzzy = FuzzyMatcher()
                ServiceRegistry.register("fuzzy", fuzzy)
            
            # Initialize History BEFORE Brain so Brain has memory
            history = None
            try:
                if config.STORE_CONVERSATION_HISTORY:
                    history = ConversationHistory()
                    ServiceRegistry.register("history", history)
                    logger.info("🧠 Conversation History Loaded")
            except Exception as e:
                 logger.warning(f"⚠️ Failed to load ConversationHistory: {e}")

            brain = AIBrain(
                context_manager=history, # Pass History instead of ContextManager
                offline_cache=OfflineCache()
            )
            ServiceRegistry.register("brain", brain)

            files = FileManager()
            ServiceRegistry.register("files", files)

            sys_info = SystemInfo()
            ServiceRegistry.register("system", sys_info)

            # Phase 5: Health Watchdog
            from core.health import HealthWatchdog
            watchdog = HealthWatchdog()
            watchdog.initialize()
            ServiceRegistry.register("health", watchdog)
            
            # 2. Security (FaceID)
            if getattr(config, "ENABLE_FACE_ID", True):
                try:
                    from modules.security import FaceID
                    face_id = FaceID(reference_image_path="data/me.jpg", hud_queue=self.hud_queue)
                    ServiceRegistry.register("face_id", face_id)
                    logger.info("🔒 FaceID System Loaded")
                except Exception as e:
                    logger.warning(f"⚠️ FaceID Load Failed: {e}")
            
            # 3. Optional Managers (Lazy loading if possible, but instantiating here)
            # (Keeping logic inline for readability during refactor)
            self._init_optional_modules()
            
            # 4. Command Processor (The Brain-Body Connection)
            # Phase 3 will largely empty this init, but for now we pass registry or nothing
            commander = CommandProcessor(ServiceRegistry)
            ServiceRegistry.register("commander", commander)

            logger.info("✅ Command Processor Initialized")

            # Agentic mode is now OFF by default on startup.
            # Use 'agentic mode on' to activate during a session.

        except Exception as e:
            logger.critical(f"❌ FATAL INITIALIZATION ERROR: {e}", exc_info=True)
            self._update_hud("ERROR", "Startup Failed")
            raise e

    def _init_optional_modules(self):
        """Helper to init massive list of optional modules using Background Proxies"""
        
        def load_opt(key, human_name, module_name, class_name, enabled):
            if enabled:
                try:
                    # Create Proxy immediately
                    def factory():
                        # Delayed Import
                        module = __import__(module_name, fromlist=[class_name])
                        return getattr(module, class_name)()
                    
                    proxy = ServiceProxy(key, human_name, factory)
                    ServiceRegistry.register(key, proxy)
                    logger.debug(f"⏳ Scheduled Background Load: {human_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to schedule {key}: {e}")

        # Shortcuts
        load_opt('shortcuts', "Shortcuts Manager", 'modules.shortcuts_manager', 'ShortcutsManager', True)

        # Clipboard
        load_opt('clipboard', "Clipboard Manager", 'modules.clipboard_manager', 'ClipboardManager', True)

        # Alarms
        load_opt('alarms', "Alarm System", 'modules.alarm_manager', 'AlarmManager', config.ENABLE_ALARMS)
        
        # Reminders
        load_opt('reminders', "Reminder System", 'modules.reminder_manager', 'ReminderManager', config.ENABLE_REMINDERS)

        # Calendar
        load_opt('calendar', "Calendar Module", 'modules.calendar_manager', 'CalendarManager', config.ENABLE_CALENDAR)
        
        # Music
        load_opt('music', "Music Controller", 'modules.music_controller', 'MusicController', config.ENABLE_MUSIC_CONTROL)
        
        # Weather
        load_opt('weather', "Weather Service", 'modules.weather_service', 'WeatherService', config.ENABLE_WEATHER)
        
        # News
        load_opt('news', "News Feed", 'modules.news_service', 'NewsService', config.ENABLE_NEWS)
        
        # Calculator
        load_opt('calculator', "Calculator", 'modules.calculator', 'Calculator', config.ENABLE_CALCULATOR)
        
        # Translator
        load_opt('translator', "Translator", 'modules.translator', 'Translator', True)
        
        # Email
        load_opt('email', "Email Client", 'modules.email_manager', 'EmailManager', config.ENABLE_EMAIL)

        # Contacts
        load_opt('contacts', "Address Book", 'modules.contact_manager', 'ContactManager', True)


    def start(self):
        """Main Application Loop"""
        logger.info("🚀 Starting Main Loop")
        
        # 1. Start Socket Server (API)
        api_input_queue = queue.Queue()
        self.api_server = JarvisSocketServer(port=8492, input_queue=api_input_queue, hud_queue=self.hud_queue)
        self.api_server.start()
        # Make the socket server accessible to skills via the registry
        ServiceRegistry.register("socket_server", self.api_server)
        
        # Wrap hud_queue for broadcasting to socket (Desktop App syncing)
        self._wrap_hud_queue_for_sockets()

        # 2. Health Check
        if config.CHECK_HEALTH_ON_STARTUP:
            self._update_hud("BOOTING", "System Check")
            checker = HealthChecker()
            checker.run_all_checks()
            if checker.is_critical_failure():
                logger.error("❌ Health check failed. Aborting start.")
                return

        # 3. Initialize Everything
        self.initialize_systems()

        # 4. Background Services
        reminders = ServiceRegistry.get("reminders")
        if reminders:
            reminders.start_background_check()
        
        # 5. Hotkeys
        self._setup_hotkeys()

        # 6. Welcome
        speech = ServiceRegistry.get("speech")
        if speech:
            speech.play_wake_sound()
            speech.speak("All systems online.")
        
        # 🟢 PROACTIVE SYNC: Broadcast actual agent state to ensure UI is in sync at boot
        status = "ON" if self.agent is not None else "OFF"
        self._update_hud("SYSTEM", f"Agentic Mode: {status}")
        self._update_hud("IDLE", "Online")

        # 7. EVENT LOOP
        while self.is_running:
            try:
                self._main_loop_iteration(api_input_queue)
            except KeyboardInterrupt:
                logger.info("🛑 KeyboardInterrupt caught in Main Loop")
                self.stop()
            except Exception as e:
                # GLOBAL SAFETY NET (Phase 5)
                logger.critical(f"🔥 CRITICAL LOOP CRASH: {e}", exc_info=True)
                self._update_hud("SYSTEM ERROR", "Recovering...")
                play_sound("error")
                
                # Report to Watchdog (if we had a complex one)
                watchdog = ServiceRegistry.get("health")
                # if watchdog: watchdog.report_crash("main_loop")
                
                time.sleep(1) # Prevent rapid loop crashing

    def _main_loop_iteration(self, api_queue):
        """Single iteration of the main event loop"""
        speech = ServiceRegistry.get("speech")
        commander = ServiceRegistry.get("commander")
        brain = ServiceRegistry.get("brain")
        
        # A. Wait for Input
        input_type, input_data = speech.wait_for_wake_or_text(api_queue)
        
        # B. Handle Text Command (Socket/Typing)
        if input_type == "TEXT":
            self._handle_text_command(input_data, commander, brain)
            return

        # C. Handle Voice Command (Wake Word)
        elif input_type == "VOICE":
            logger.debug("🎤 Wake Detected")
            
            # 1. Check Interrupt
            if speech.is_interrupted:
                self._update_hud("IDLE", "Interrupted")
                return

            # 2. FaceID Security Check
            face_id = ServiceRegistry.get("face_id")
            if face_id:
                self._update_hud("SECURITY", "Verifying Face")
                # display_status("🔒 VERIFYING FACE ID...", "bold yellow")
                
                if not face_id.verify_user(timeout=3):
                    self._update_hud("ACCESS DENIED", "Face ID Failed")
                    speech.speak("Access denied.")
                    time.sleep(1)
                    self._update_hud("IDLE", "Standing By")
                    return

            # 3. Listen
            original_volume = duck_audio()
            time.sleep(0.5) # Allow ducking to apply (Prevent VAD false positive)
            
            speech.speak("Yes sir")
            
            # Active Conversation Loop
            active_conversation = True
            stt_retry_count = 0
            while active_conversation:
                # Manual sleep is stronger than interrupt-to-listen: exit immediately.
                if getattr(speech, "manual_sleep_requested", False):
                    logger.info("⛔️ Manual sleep requested. Ending conversation immediately.")
                    break

                # PHASE 15: Interrupt-to-Listen Flow
                if speech.is_interrupted: 
                    logger.info("⚡️ Re-entering Listen Mode after Interrupt")
                    speech.is_interrupted = False
                    # Optional: Play subtle cue?
                    # play_sound("listening") 
                    # Continue loop to listen_command() immediately
                
                # Minimum Listen Duration (Avoid instant sleep)
                command = speech.listen_command(duration=3)
                
                # Removed premature restoration to keep audio ducked during command execution
                # if original_volume is not None:
                #     restore_audio(original_volume)
                #     original_volume = None
                
                if not command:
                    # Master Override: If manual stop was triggered, break immediately
                    if speech.is_interrupted:
                        logger.info("⛔️ Manual stop detected. Ending conversation immediately.")
                        break

                    listen_status = getattr(speech, "last_listen_status", "unknown")

                    # No user input is a normal case: go idle immediately.
                    if listen_status in ("no_speech", "interrupted"):
                        logger.info("🛑 No speech detected. Ending conversation.")
                        break

                    # Retry only transcription/system failures (Apple Speech/engine failure).
                    if listen_status in ("transcribe_failed", "audio_error"):
                        stt_retry_count += 1
                        if stt_retry_count < 3:
                            logger.warning(
                                f"⚠️ Speech engine failure ({listen_status}) "
                                f"(Attempt {stt_retry_count}/3). Retrying..."
                            )
                            continue
                        logger.info("🛑 Speech engine retry limit reached. Ending conversation.")
                        break

                    # Unknown failure mode: fail-safe to idle without loops.
                    logger.info(f"🛑 Ending conversation due to listen status: {listen_status}")
                    break
                else:
                    stt_retry_count = 0 # Reset only on successful transcription
                
                self._update_hud("USER", command)
                self._update_hud("PROCESSING", "Analyzing Request")
                
                # Process
                command, web_search = self._parse_web_search_command(command)
                
                if web_search:
                     self._update_hud("PROCESSING", "🌍 Web Search Active")
                     print(f"🌍 Web Search Query: '{command}'")

                result = self._run_command_with_interrupt_guard(
                    commander=commander,
                    command=command,
                    web_search=web_search,
                    speech=speech
                )
                if result == "INTERRUPTED":
                    active_conversation = False
                    continue
                active_conversation = self._handle_command_result(result, command, commander, brain, speech, web_search=web_search, original_volume=original_volume)
            
            if original_volume is not None:
                    time.sleep(0.5) # Wait for speech to fully finish before restoring media
                    restore_audio(original_volume)
            
            self._update_hud("IDLE", "Standing By")

    def _parse_web_search_command(self, command):
        """
        Parses command for web search triggers and cleans the query.
        Returns: (cleaned_command, web_search_bool)
        """
        web_search = False
        found_explicit = False
        
        # Handle Dict Input (from Socket)
        if isinstance(command, dict):
            web_search = command.get("web_search", False)
            command = command.get("text", "")
        
        # Prepare for Trigger Check
        cmd_lower = command.lower()
        
        # 1. Strip helper prefix but PRESERVE internal and significant whitespace
        # We only strip leading/trailing if it's a single line.
        # For multi-line, we treat it as code/pre-formatted text.
        is_multiline = "\n" in command
        
        explicit_patterns = [
            r"\bgoogle\b",
            r"\bsearch\b",
            r"\bsearch\s+for\b",
            r"\blook\s+up\b",
            r"\bfind\b",
        ]
        if any(re.search(pattern, cmd_lower) for pattern in explicit_patterns):
            web_search = True
            found_explicit = True

        # Only strip prefix if it's there
        prefix_pattern = r"^\s*use search(?:\s+(?:for|on))?\s+"
        if re.search(prefix_pattern, command, flags=re.IGNORECASE):
            command = re.sub(prefix_pattern, "", command, flags=re.IGNORECASE)
            
        if not is_multiline:
            command = command.strip()
        
        # 2. AI-Powered Smart Detection (Fast <500ms)
        if not web_search and not found_explicit:
            # Short-circuit: large pastes are likely code/notes, not factual searches
            if len(command) > 300 or is_multiline:
                web_search = False
            else:
                web_search = self._ai_needs_web_search(command)
                    
        return command, web_search
    
    def _ai_needs_web_search(self, query):
        """
        Smart classifier to determine if query needs web search.
        STRATEGY: Default to YES for any knowledge/factual question.
        Only skip search for: system commands, casual chat, code generation.
        """
        q_lower = query.lower().strip()
        
        # ========== FAST RULE-BASED PRE-FILTER (No LLM needed) ==========
        
        # DEFINITE NO — System commands (these are handled by other skills)
        no_search_starts = [
            "open ", "play ", "pause", "stop", "mute", "unmute", "volume",
            "set alarm", "set timer", "set reminder", "remind me",
            "send email", "send message", "call ", "dial ",
            "cursor control", "cursor", "screenshot",
            "translate ", "calculate ", "convert ",
            "what time", "what's the time", "whats the time",
            "turn on", "turn off", "switch on", "switch off",
            "close ", "quit ", "exit", "shut down", "shutdown",
            "lock", "lock screen", "screen off", "brb", "stepping away",
            "going away", "i'm going", "i am going",
            "mute", "unmute", "make it louder", "make it quieter",
            "turn it up", "turn it down",
            "i'm done", "done for now", "wrap it up", "call it a day",
            "time to go", "end session",
            "start recording", "stop recording",
        ]
        if any(q_lower.startswith(ns) for ns in no_search_starts):
            print(f"🤖 Web Search Skip (command): '{query}'")
            return False
        
        # DEFINITE NO — Pure casual/chat (very short greetings)
        casual_exact = [
            "hello", "hi", "hey", "jarvis", "good morning", "good evening", "good night",
            "thanks", "thank you", "ok", "okay", "yes", "no", "sure",
            "bye", "goodbye", "see you", "let's go", "lets go",
            "tell me a joke", "joke", "sing a song",
        ]
        if q_lower.rstrip("!?.") in casual_exact:
            print(f"🤖 Web Search Skip (casual): '{query}'")
            return False
            
        # DEFINITE NO — Code generation requests
        code_keywords = ["write code", "write a script", "create a function", "write a program",
                         "generate code", "code for", "python code", "javascript code"]
        if any(ck in q_lower for ck in code_keywords):
            print(f"🤖 Web Search Skip (code): '{query}'")
            return False

        # DEFINITE NO — Short conversational follow-ups (answers to Q&A)
        # If the user just gave a short reply (< 8 words) that doesn't look like 
        # a question, it's almost certainly a conversational follow-up, not a search query.
        word_count = len(query.split())
        is_question = any(q_lower.startswith(qw) for qw in ["who ", "what ", "where ", "when ", "how ", "why ", "is ", "are ", "can ", "do ", "does ", "did ", "should "])
        
        if word_count <= 8 and not is_question:
            # Check if it looks like a conversational answer (not a factual question)
            # e.g., "a cramping sensation", "yes", "the left side", "about 2 hours ago"
            factual_markers = ["price of", "cost of", "worth of", "latest", "news", "current",
                              "tell me about", "do you know", "history of", "who is", "what is"]
            if not any(fm in q_lower for fm in factual_markers):
                print(f"🤖 Web Search Skip (short follow-up, {word_count} words): '{query}'")
                return False

        # DEFINITE YES — Obvious factual queries (skip LLM call for speed)
        obvious_search = ["who is", "what is", "where is", "when did", "when was", "when is",
                         "how old", "how many", "how much", "how tall", "how far",
                         "tell me about", "do you know about", "do u know about",
                         "what are", "what was", "what does", "what did",
                         "is it true", "current", "latest", "news",
                         "price of", "cost of", "worth of",
                         "history of", "biography of"]
        if any(q_lower.startswith(os_) or os_ in q_lower for os_ in obvious_search):
            print(f"🤖 Web Search YES (obvious): '{query}'")
            return True
        
        # Check for pronouns (follow-up questions) — search only if they're QUESTIONS
        pronouns = [" he ", " she ", " his ", " her ", " him ", " they ", " them ", " their ",
                    "is he", "is she", "was he", "was she", "does he", "does she", "did he", "did she"]
        if any(p in f" {q_lower} " for p in pronouns) and is_question:
            print(f"🤖 Web Search YES (pronoun question): '{query}'")
            return True

        # ========== SMART DEFAULT (no LLM call needed) ==========
        # For medium-length queries that look like questions, search
        # For everything else (statements, instructions), DON'T search
        if is_question and word_count > 4:
            print(f"🤖 Web Search YES (question, {word_count} words): '{query}'")
            return True
        
        # Default: DON'T search — let the cloud brain handle it with context
        print(f"🤖 Web Search NO (conversational default): '{query}'")
        return False


    def _handle_text_command(self, command_data, commander, brain):
        """Process text input path"""
        # 1. Handle Pydantic Dict or Legacy String
        if isinstance(command_data, dict):
            command = command_data.get("text", "")
            explicit_web_search = command_data.get("web_search", False)
            source = command_data.get("source", "unknown")
        else:
            command = str(command_data)
            explicit_web_search = False
            source = "legacy"

        # 2. INTERCEPT INTERNAL COMMANDS FIRST (Silent/No HUD)
        if command.startswith("__UPDATE_CONFIG__"):
            self._process_internal_config_update(command)
            return

        # 3. Normal Command Processing
        logger.info(f"⌨️ Typed Command ({source}): {command} [Web: {explicit_web_search}]")
        
        # Parse for smart web search
        command, ai_web_search = self._parse_web_search_command(command)
        web_search = explicit_web_search or ai_web_search

        self._update_hud("USER", f"⌨️ {command}")
        self._update_hud("PROCESSING", "Analyzing Text...")
        
# self._update_hud("PROCESSING", "🌍 Web Search Active")
# print(f"🌍 Web Search Query: '{command}'")
        
        speech = ServiceRegistry.get("speech")
        result = self._run_command_with_interrupt_guard(
            commander=commander,
            command=command,
            web_search=web_search,
            speech=speech
        )
        if result == "INTERRUPTED":
            self._update_hud("IDLE", "Interrupted")
            return
        self._handle_command_result(result, command, commander, brain, ServiceRegistry.get("speech"), web_search=web_search, original_volume=None)
        self._update_hud("IDLE", "Standing By")

    def _handle_command_result(self, result, command_text, commander, brain, speech, web_search=False, original_volume=None):
        """
        Interprets return value from CommandProcessor.
        Returns: Boolean (True = Continue Conversation, False = Stop)
        """
        if result == "EXIT":
            if original_volume is not None:
                restore_audio(original_volume)
            self.stop()
            sys.exit(0)
            
        elif result == "STOP_LISTENING":
            return False

        elif result == "USE_AI_BRAIN":
            # PHASE 1 UPDATED: Route to Agent if active
            if getattr(config, "ENABLE_AGENTIC_MODE", False) and self.agent:
                speech.speak("Entering agentic loop.")
                self._update_hud("AGENT", f"Task: {command_text}")
                
                # Run Agent in thread to allow interruptions (same as Brain)
                agent_res_container = {"text": None}
                def run_agent_encapsulated():
                    if not speech.is_interrupted:
                        agent_res_container["text"] = self.agent.run(command_text)
                
                agent_thread = threading.Thread(target=run_agent_encapsulated)
                agent_thread.start()
                
                while agent_thread.is_alive():
                    if self._detect_interrupt(speech):
                        self._cancel_current_cycle(speech, reason="Agent Cancelled")
                        return False
                    time.sleep(0.05)
                
                response = agent_res_container["text"]
                if response:
                    log_history(ServiceRegistry.get("history"), command_text, response, "autonomous_agent")
                    speech.speak(response, allow_interruptions=True)
                return True

            speech.speak("Thinking.")
            self._update_hud("PROCESSING", "Thinking...")
            
            # Run AI in thread to allow interruptions
            ai_response_container = {"text": None}
            
            def ask_brain_encapsulated():
                if not speech.is_interrupted:
                    print(f"🔍 Calling brain.ask() with web_search={web_search}")  # DEBUG
                    ai_response_container["text"] = brain.ask(command_text, web_search=web_search)
            
            think_thread = threading.Thread(target=ask_brain_encapsulated)
            think_thread.start()
            
            # Wait with Interrupt monitor
            while think_thread.is_alive():
                # Check passive voice interrupt
                if self._detect_interrupt(speech):
                    self._cancel_current_cycle(speech, reason="Cancelled")
                    return False
                time.sleep(0.05)
            
            response = ai_response_container["text"]
            if response:
                log_history(ServiceRegistry.get("history"), command_text, response, "ai_brain")
                play_sound("success")
                
                # --- DUCK AUDIO FOR SPEECH ---
                # We reinforce ducking here just in case, but we DO NOT restore.
                # The main loop handles restoration when the conversation ends.
                # This ensures music stays low while Jarvis waits for your next IDLE command.
                duck_audio() 
                time.sleep(0.2)
                
                # FORCE SPEAK: Interruptions Enabled (User Request) but Sensitivity Tuned
                speech.speak(response, allow_interruptions=True)
                # ---------------------------------------
            else:
                pass # Cancelled or empty
            
            return True # Continue conversation? Optional. Usually AI response ends turn.
            
        elif result is True:
            # Command handled successfully
            log_history(ServiceRegistry.get("history"), command_text, "Success", "command")
            return True 
            
        return False

    def _run_command_with_interrupt_guard(self, commander, command, web_search, speech):
        """
        Runs command handling in a worker thread and allows wake-word interruption
        at any point in the command lifecycle.
        """
        cmd_text = str(command).lower() if command is not None else ""
        # Cursor control requires main-thread execution for camera/OpenGL window lifecycle on macOS.
        if any(token in cmd_text for token in ("cursor control", "mouse control", "cur control")):
            return commander.process(command, web_search=web_search)

        if speech is None:
            return commander.process(command, web_search=web_search)

        result_box = {"result": None}

        def _run():
            result_box["result"] = commander.process(command, web_search=web_search)

        worker = threading.Thread(target=_run, daemon=True)
        worker.start()

        while worker.is_alive():
            if self._detect_interrupt(speech):
                self._cancel_current_cycle(speech, reason="Interrupted")
                return "INTERRUPTED"
            time.sleep(0.03)

        return result_box["result"]

    def _detect_interrupt(self, speech):
        if speech is None:
            return False
        try:
            return bool(
                speech.is_interrupted
                or speech.check_for_interrupt_passive()
                or getattr(speech, "manual_sleep_requested", False)
            )
        except Exception:
            return False

    def _cancel_current_cycle(self, speech, reason="Interrupted"):
        """Hard-stop current cycle irrespective of current state."""
        try:
            speech.force_stop()
        except Exception:
            pass
        self._update_hud("IDLE", reason)

    def _setup_hotkeys(self):
        def go_to_sleep():
            logger.info("⛔️ Manual Stop Triggered")
            speech = ServiceRegistry.get("speech")
            if speech:
                speech.force_stop()
            subprocess.run(["pkill", "afplay"], check=False)
            subprocess.run(["pkill", "say"], check=False)
            restore_audio(None)
            self._update_hud("IDLE", "Muted")

        def kill_program():
            logger.critical("🛑 KILL SWITCH ACTIVATED")
            self._update_hud("OFFLINE", "Terminated")
            self.stop()
            os._exit(0)

        self.hotkey_listener = HotkeyManager(on_single_tap=go_to_sleep, on_double_tap=kill_program)
        self.hotkey_listener.start()

    def _update_hud(self, header, detail):
        """Safe HUD Update"""
        try:
            self.hud_queue.put((header, detail))
            # Also Log it for file history
            logger.debug(f"[HUD] {header}: {detail}")
        except: pass

    def _emit_state_cue(self, header):
        """
        Lightweight audio telemetry for non-visual users.
        Plays only on state transitions and debounces noisy updates.
        """
        normalized = str(header).upper().strip()
        if not normalized:
            return

        now = time.time()
        if normalized == self._last_hud_header:
            return

        # Debounce aggressive state chatter
        if now - self._last_state_cue_at < 0.25:
            self._last_hud_header = normalized
            return

        self._last_hud_header = normalized
        self._last_state_cue_at = now

        if normalized in ("LISTENING",):
            play_sound("listening")
        elif normalized in ("PROCESSING", "THINKING", "STREAMING"):
            play_sound("processing")
        elif normalized in ("IDLE",):
            play_sound("idle")
        elif normalized in ("ACCESS DENIED", "ERROR", "SYSTEM ERROR", "OFFLINE"):
            play_sound("error")
        elif normalized in ("MUTED", "CANCELLED", "INTERRUPTED"):
            play_sound("interrupt")

    def _wrap_hud_queue_for_sockets(self):
        """Legacy adaptation for socket server"""
        original_q = self.hud_queue
        server = self.api_server
        
        class SocketQueueProxy:
            def __init__(self, q, srv, cue_cb):
                self.q = q
                self.srv = srv
                self.cue_cb = cue_cb
            def put(self, item):
                self.q.put(item)
                if isinstance(item, tuple) and len(item) >= 2:
                    try:
                        self.cue_cb(str(item[0]))
                    except Exception:
                        pass
                    self.srv.broadcast(str(item[0]), str(item[1]))
        
        self.hud_queue = SocketQueueProxy(original_q, server, self._emit_state_cue)
        # Ensure all registry consumers (skills/services) now use socket-aware HUD queue.
        ServiceRegistry.register("hud", self.hud_queue)

        # Keep existing speech engine HUD-wired after proxy swap.
        speech = ServiceRegistry.get("speech")
        if speech:
            try:
                speech.hud_queue = self.hud_queue
                if hasattr(speech, "tts"):
                    speech.tts.hud_queue = self.hud_queue
            except Exception:
                pass

    def restart_service(self, service_name: str) -> bool:
        """Self-Healing: Restart a crashed service dynamically."""
        logger.warning(f"🔄 Restarting Service: {service_name}")
        try:
            if service_name == "speech":
                old_speech = ServiceRegistry.get("speech")
                if old_speech: old_speech.stop()
                
                new_speech = SpeechEngine(hud_queue=self.hud_queue)
                ServiceRegistry.register("speech", new_speech)
                
                # Re-inject command phrases
                commander = ServiceRegistry.get("commander")
                if commander:
                    new_speech.set_phrases(commander.command_phrases)
                
                logger.info("✅ Speech Engine Restarted Successfully")
                play_sound("startup")
                return True
            
            elif service_name == "brain":
                # Re-init brain
                brain = AIBrain(
                    context_manager=ServiceRegistry.get("history"),
                    offline_cache=OfflineCache()
                )
                ServiceRegistry.register("brain", brain)
                logger.info("✅ AI Brain Restarted")
                return True
                
            return False
        except Exception as e:
            logger.error(f"❌ Failed to restart {service_name}: {e}")
            return False

    def _process_internal_config_update(self, raw_command: str):
        """
        Handles __UPDATE_CONFIG__:{"key": "ENABLE_AGENTIC_MODE", "value": true}
        Persists to config.py atomically and triggers live logic shifts.
        """
        try:
            json_str = raw_command.replace("__UPDATE_CONFIG__:", "").strip()
            data = json.loads(json_str)
            key = data.get("key")
            value = data.get("value")

            if key == "ENABLE_AGENTIC_MODE":
                # Keep the live runtime config in sync with the persisted flag.
                setattr(config, key, value)
                self._toggle_agent(value)
                # Still persist to file
                self._update_atomic_config("ENABLE_AGENTIC_MODE", value)

        except Exception as e:
            logger.error(f"❌ Config Update Error: {e}")

    def _toggle_agent(self, enabled: bool, silent: bool = False):
        """Unified logic to activate/deactivate Agentic Mode"""
        # NO EARLY EXIT: We always proceed to broadcast state to force-sync the UI
        old_agent = self.agent
        
        if enabled:
            if old_agent is None:
                logger.info("🤖 AGENTIC MODE ACTIVATED")
                try:
                    from modules.agent_core import AgentCore
                    agent_cfg = config.AgentConfig(
                        enabled=True,
                        max_iterations=getattr(config, "AGENTIC_MAX_ITERATIONS", 30),
                        timeout=getattr(config, "AGENTIC_TIMEOUT_SECONDS", 30),
                        retry_budget=getattr(config, "TOOL_CALL_MAX_RETRIES", 2)
                    )
                    agent_cfg.validate()
                    
                    self.agent = AgentCore(registry=ServiceRegistry, config=agent_cfg)
                    if not silent:
                        speech = ServiceRegistry.get("speech")
                        if speech:
                            speech.speak("Switched to agentic mode, sir")
                except Exception as e:
                    logger.error(f"❌ Failed to initialize Agentic Mode: {e}")
                    self._update_hud("ERROR", f"Agent Init Failed: {str(e)}")
            
            # FORCE BROADCAST to sync UI
            self._update_hud("SYSTEM", "Agentic Mode: ON")
        else:
            if old_agent is not None:
                logger.info("🔌 AGENTIC MODE DEACTIVATED")
                self.agent = None
                if not silent:
                    speech = ServiceRegistry.get("speech")
                    if speech:
                        speech.speak("Switching back to standard mode")
            
            # FORCE BROADCAST to sync UI
            self._update_hud("SYSTEM", "Agentic Mode: OFF")
        
        # Always end in IDLE state for HUD to clear visual cues
        self._update_hud("IDLE", "Standing By")

    def _update_atomic_config(self, key: str, value):
        """Persists config change to config.py using atomic rename pattern"""
        config_path = os.path.join(os.path.dirname(__file__), "config.py")
        tmp_path = config_path + ".tmp"
        
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()
            
            with open(tmp_path, 'w') as f:
                key_found = False
                for line in lines:
                    if line.strip().startswith(f"{key} ="):
                        val_str = f"'{value}'" if isinstance(value, str) else str(value)
                        f.write(f"{key} = {val_str}\n")
                        key_found = True
                    else:
                        f.write(line)
                
                if not key_found:
                    val_str = f"'{value}'" if isinstance(value, str) else str(value)
                    f.write(f"\n{key} = {val_str}\n")
            
            os.replace(tmp_path, config_path)
            logger.debug(f"💾 Persisted {key}={value} to config.py")
        except Exception as e:
            logger.error(f"❌ Atomic config write failed: {e}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def stop(self):
        """Cleanup and Shutdown"""
        self.is_running = False
        logger.info("🛑 Shutting down JarvisApp...")
        
        reminders = ServiceRegistry.get("reminders")
        if reminders:
            reminders.stop_background_check()
        
        if hasattr(self, 'hotkey_listener'):
            self.hotkey_listener.stop()
            
        if self.api_server:
            self.api_server.stop()

# Helper for history logging
def log_history(history_component, user_text, ai_text, type_):
    if history_component:
        history_component.log_exchange(user_text, ai_text, type_)

# --- ENTRY POINT ---
def _check_single_instance():
    """
    Bulletproof Single Instance Guard.
    If port 8492 is busy, Jarvis is already running.
    In that case, ensure the Swift App is open and exit.
    """
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', 8492)) == 0:
                print("ℹ️ Jarvis backend already running (Port 8492).")
                print("🚀 Activating Jarvis UI...")
                os.system("open /Applications/Jarvis.app &")
                sys.exit(0)
    except Exception:
        pass

def main():
    _check_singleton = "--ignore-singleton" not in sys.argv
    if _check_singleton:
        _check_single_instance()

    api_mode = "--api" in sys.argv
    
    if config.DEV_MODE or api_mode:
        # Single Process Mode or API Mode (No Terminal HUD)
        class LogQueue:
            def put(self, item):
                pass
        
        mode_name = "API" if api_mode else "DEV"
        logger.info(f"🚀 Starting in {mode_name} Mode")
        
        # Use simple queue for API mode
        # This wrapper/queue is critical for internal components expecting a queue
        hud_queue = queue.Queue()
            
        app = JarvisApp(hud_queue)
        app.start()
        
    else:
        # Check if HUD is disabled (cooling optimization)
        if getattr(config, 'DISABLE_HUD', False):
            # Logic-Only Mode: No HUD, plain terminal logs
            logger.info("🚀 Starting in Logic-Only Mode (HUD Disabled)")
            hud_queue = queue.Queue()
            app = JarvisApp(hud_queue)
            app.start()
        else:
            # Multi Process Mode with Terminal HUD
            try:
                 # Lazy import to avoid Top-Level Refers to TTY/Rich hanging in App Bundle
                 from modules.hud import run_hud_process
            except ImportError:
                 logger.error("Failed to import HUD module")
                 return

            hud_queue = multiprocessing.Queue()
            
            jarvis_process = multiprocessing.Process(target=_run_app_process, args=(hud_queue,))
            jarvis_process.start()
            
            # GUI must run in main thread
            run_hud_process(hud_queue)

def _run_app_process(q):
    """Process wrapper"""
    app = JarvisApp(q)
    app.start()

if __name__ == "__main__":
    main()
