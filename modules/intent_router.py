"""
IntentRouter — 3-Layer Cloud-First Architecture

Layer 1: Deterministic pre-filter     (microseconds, zero API calls)
Layer 2: Groq function calling         (cloud, ~300ms, zero local heat)
Layer 3: Ollama offline fallback       (lazy-loaded ONLY if Groq fails)

Ollama is NEVER loaded at startup. Your Mac stays cool 24/7.
"""

import json
import os
import re
import time
import requests
import config

from utils.logger import get_logger
logger = get_logger()


# ─────────────────────────────────────────────────────────────
# HUD helper — pushes messages into the Jarvis Swift UI chatbox
# ─────────────────────────────────────────────────────────────
def _hud_msg(text: str):
    """Send a status message to the Jarvis app chatbox + terminal."""
    logger.info(f"[IntentRouter] {text}")
    try:
        from core.registry import ServiceRegistry
        hud = ServiceRegistry.get("hud")
        if hud:
            hud.put(("JARVIS", text))
    except Exception:
        pass


class IntentRouter:
    """
    Intelligent Intent Engine — Cloud-First, Ollama Fallback.
    """

    # ── Intent Constants (keep identical to old API so commands.py needs no changes) ──
    ACTION_ARCHITECT_NEW           = "ARCHITECT_NEW"
    ACTION_ARCHITECT_UPDATE_MINOR  = "ARCHITECT_UPDATE_MINOR"
    ACTION_ARCHITECT_UPDATE_MAJOR  = "ARCHITECT_UPDATE_MAJOR"
    ACTION_WEB_SEARCH              = "WEB_SEARCH"
    ACTION_SYSTEM_CONTROL          = "SYSTEM_CONTROL"
    ACTION_GENERAL_CONVERSATION    = "GENERAL_CONVERSATION"
    ACTION_AGENTIC_TASK            = "AGENTIC_TASK"
    ACTION_SKILL_DISPATCH          = "SKILL_DISPATCH"  # skill handles it directly

    # Groq config
    _groq_api_key   = getattr(config, "GROQ_API_KEY", "")
    _groq_url       = "https://api.groq.com/openai/v1/chat/completions"
    _router_model   = getattr(config, "INTENT_ROUTER_MODEL", "llama-3.1-8b-instant")
    _max_tokens     = getattr(config, "INTENT_ROUTER_MAX_TOKENS", 80)
    _max_retries    = getattr(config, "INTENT_ROUTER_GROQ_RETRIES", 3)
    _retry_wait     = getattr(config, "INTENT_ROUTER_GROQ_RETRY_WAIT", 10)

    # Ollama lazy-load state
    _ollama_confirmed_running = False

    def __init__(self):
        logger.info(f"🧠 Intent Engine Initialized — Cloud-First (Groq/{self._router_model})")

    # ════════════════════════════════════════════════════════════
    # PUBLIC: Main entry point
    # ════════════════════════════════════════════════════════════
    def analyze(self, command: str, previous_project_path: str = None) -> dict:
        """
        Classify user command through the 3-layer pipeline.
        Returns: {"intent": "...", "confidence": 0.0–1.0, "thought": "..."}
        """
        cmd = command.strip()

        # ── Layer 1: Fast deterministic pre-filter ──────────────
        result = self._layer1_prefilter(cmd)
        if result:
            logger.debug(f"⚡ Pre-filter hit: {result['intent']}")
            return result

        # ── Layer 2: Groq function calling ──────────────────────
        result = self._layer2_groq(cmd, previous_project_path)
        if result:
            logger.info(f"☁️ Groq intent: {result['intent']} (conf: {result.get('confidence', '?')})")
            return result

        # ── Layer 3: Ollama offline fallback ────────────────────
        result = self._layer3_ollama(cmd, previous_project_path)
        if result:
            logger.info(f"🏠 Ollama intent: {result['intent']}")
            return result

        # Ultimate fallback
        return {"intent": self.ACTION_GENERAL_CONVERSATION, "confidence": 0.1,
                "thought": "All layers failed — defaulting to conversation"}

    # ════════════════════════════════════════════════════════════
    # LAYER 1 — Deterministic Pre-filter (zero LLM, ~0ms)
    # ════════════════════════════════════════════════════════════
    def _layer1_prefilter(self, cmd: str) -> dict | None:
        """
        Fast keyword/pattern matching for the 85% of commands that don't need an LLM.
        Returns intent dict or None if ambiguous.
        """
        c = cmd.lower()
        all_words = c.split()
        unique_words = set(all_words)

        # ── GLOBAL MACRO-COMMAND GUARD ──
        # If this looks like a prompt, code, or complex instruction, BYPASS all pre-filters.
        # This prevents technical words (like "lock" or "pause") from triggering system actions.
        is_macro = (
            len(all_words) > 12 or 
            len(cmd) > 120 or 
            "\n" in cmd or 
            "{" in cmd or 
            "---" in cmd
        )
        if is_macro:
            logger.debug("🧠 Macro-command detected — sending to LLM for context analysis")
            return None

        # Very short commands (1–2 words) → conversation, never code architect
        if len(unique_words) <= 2:
            return self._ok(self.ACTION_GENERAL_CONVERSATION, 0.9, "Ultra-short, clearly not architect")

        # Music/Media
        music_kw = {"play", "pause", "resume", "skip", "next", "previous", "shuffle",
                    "spotify", "music", "song", "track", "album", "artist", "playlist"}
        if unique_words & music_kw:
            return self._ok(self.ACTION_SYSTEM_CONTROL, 0.95, "Music keyword")

        # System control
        system_kw = {"volume", "brightness", "battery", "lock", "mute", "unmute",
                     "ram", "cpu", "memory", "disk", "storage", "uptime", "screen"}
        if unique_words & system_kw:
            return self._ok(self.ACTION_SYSTEM_CONTROL, 0.95, "System keyword")

        # NLP volume patterns (no "volume" keyword needed)
        if re.search(r"\b(make\s+it\s+(louder|quieter)|turn\s+(it\s+)?(up|down)|louder|quieter)\b", c):
            return self._ok(self.ACTION_SYSTEM_CONTROL, 0.95, "Volume NLP")

        # Lock screen NLP
        if re.search(r"\b(brb|be\s+right\s+back|stepping\s+away|going\s+away|take\s+a\s+break)\b", c):
            return self._ok(self.ACTION_SYSTEM_CONTROL, 0.95, "Lock screen NLP")

        # Communication — still GENERAL_CONVERSATION (brain handles compose/send flow)
        comm_kw = {"message", "text", "whatsapp", "email", "mail", "call", "contact", "send"}
        if unique_words & comm_kw and not ({"build", "create", "make"} & unique_words):
            return self._ok(self.ACTION_GENERAL_CONVERSATION, 0.9, "Communication keyword")

        # Weather — handled by WeatherSkill (SKILL_DISPATCH lets skill iteration run)
        if (unique_words & {"weather", "forecast", "temperature", "rain", "humidity"}) and not ({"build", "create", "make", "develop"} & unique_words):
            return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "WeatherSkill")

        # Time / Date
        # GUARD: compound query mixing time + another domain (e.g. weather, news) must
        # bypass this pre-filter so Groq can route it properly — TimeSkill alone can't answer both.
        _other_domains = {"weather", "forecast", "temperature", "rain", "humidity",
                          "news", "headline", "stock", "price",
                          "email", "message", "whatsapp", "remind", "alarm"}
        if unique_words & {"time", "date", "clock", "today", "tomorrow"}:
            if unique_words & _other_domains:
                return None  # compound query — let Groq handle the full thing
            if len(unique_words) <= 6:
                return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "TimeSkill")

        # Alarms / Reminders
        if re.search(r"\b(set\s+(alarm|reminder|timer)|wake\s+me\s+up|remind\s+me)\b", c):
            return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "AlarmSkill / ReminderSkill")

        # Calculator
        if re.search(r"\b(calculate|compute|convert|tip|percent|math)\b", c):
            return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "CalculatorSkill")

        # Translator
        if re.search(r"\b(translate|how\s+do\s+you\s+say|how\s+to\s+say)\b", c):
            return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "TranslatorSkill")

        # News
        if unique_words & {"news", "headlines"} or (unique_words & {"latest"} and unique_words & {"news", "headlines", "stories", "updates"}):
            return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "NewsSkill")

        # Focus / DND
        if re.search(r"\b(focus\s+mode|do\s+not\s+disturb|dnd)\b", c):
            return self._ok(self.ACTION_SKILL_DISPATCH, 0.95, "FocusSkill")

        # Obvious web search
        if re.search(r"\b(who\s+is|what\s+is|where\s+is|when\s+(did|was)|how\s+old|tell\s+me\s+about)\b", c):
            return self._ok(self.ACTION_WEB_SEARCH, 0.85, "Obvious factual question")

        # If none of the above → ambiguous, let Groq decide
        return None

    # ════════════════════════════════════════════════════════════
    # LAYER 2 — Groq Function Calling (cloud, ~300ms)
    # ════════════════════════════════════════════════════════════
    def _layer2_groq(self, cmd: str, project_path: str = None) -> dict | None:
        """
        Call Groq using JSON-mode (simpler + more reliable than tool_choice).
        Retries 3× with 10s gap + live UI status messages.
        """
        if not self._groq_api_key:
            logger.warning("⚠️ No GROQ_API_KEY — skipping cloud intent router")
            return None

        project_context = ""
        if project_path:
            project_name = os.path.basename(project_path)
            project_context = f'\nCurrent active project: "{project_name}"'

        # Determine if agentic mode is active for AGENTIC_TASK classification
        agentic_mode = getattr(config, 'ENABLE_AGENTIC_MODE', False)
        agentic_intent_line = (
            '- AGENTIC_TASK: Multi-step tasks requiring tools (run code, scrape data, build projects, research + act)\n'
            if agentic_mode else ''
        )

        system_prompt = (
            'You are an intent classifier for Jarvis. Respond ONLY with valid JSON, no extra text.\n'
            'Classify the command into exactly one of these intents:\n'
            '- ARCHITECT_NEW: Build/create/make a new app, website, game, or script\n'
            '- ARCHITECT_UPDATE_MINOR: Small fix/tweak to the current project\n'
            '- ARCHITECT_UPDATE_MAJOR: Redesign/overhaul/refactor the current project\n'
            '- WEB_SEARCH: Factual questions, news, current data (who is X, what is Y)\n'
            '- SYSTEM_CONTROL: Control the computer (open app, volume, brightness, lock screen)\n'
            f'{agentic_intent_line}'
            '- GENERAL_CONVERSATION: Everything else — chat, messaging, reminders, weather, music\n'
            f'{project_context}\n\n'
            'Output exactly this JSON structure:\n'
            '{"intent": "INTENT_NAME", "confidence": 0.9, "thought": "one sentence reason", "tool_hints": ["tool1", "tool2"]}\n'
            'tool_hints: optional list of tools the task likely needs (e.g. ["web_search", "write_file"]). Omit if not applicable.'
        )

        headers = {
            "Authorization": f"Bearer {self._groq_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self._router_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f'Command: "{cmd}"'}
            ],
            "response_format": {"type": "json_object"},
            "max_tokens": self._max_tokens,
            "temperature": 0.1
        }

        valid_intents = {
            "ARCHITECT_NEW", "ARCHITECT_UPDATE_MINOR", "ARCHITECT_UPDATE_MAJOR",
            "WEB_SEARCH", "SYSTEM_CONTROL", "GENERAL_CONVERSATION", "AGENTIC_TASK"
        }

        for attempt in range(1, self._max_retries + 1):
            try:
                response = requests.post(
                    self._groq_url,
                    headers=headers,
                    json=payload,
                    timeout=8
                )

                if response.status_code == 200:
                    content = (
                        response.json()
                        .get("choices", [{}])[0]
                        .get("message", {})
                        .get("content", "")
                    )
                    data = json.loads(content)
                    intent = data.get("intent", self.ACTION_GENERAL_CONVERSATION).upper().strip()
                    if intent not in valid_intents:
                        intent = self.ACTION_GENERAL_CONVERSATION
                    return {
                        "intent": intent,
                        "confidence": float(data.get("confidence", 0.8)),
                        "thought": data.get("thought", ""),
                        "tool_hints": data.get("tool_hints", []),
                    }

                elif response.status_code == 429:
                    logger.warning(f"⚠️ Groq rate limited (429) on attempt {attempt}")
                else:
                    logger.warning(f"⚠️ Groq HTTP {response.status_code} on attempt {attempt}: {response.text[:100]}")

            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                logger.warning(f"⚠️ Groq connection error (attempt {attempt}/{self._max_retries}): {e}")
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ Groq JSON parse error on attempt {attempt}: {e}")
            except Exception as e:
                logger.error(f"❌ Groq unexpected error: {e}")
                return None  # Don't retry unexpected errors

            # ── Show live retry status in UI + terminal ──
            if attempt < self._max_retries:
                _hud_msg(f"Connecting to Groq... ({attempt}/{self._max_retries})")
                time.sleep(self._retry_wait)
            else:
                _hud_msg(f"Connecting to Groq... ({attempt}/{self._max_retries})")

        # All retries exhausted
        _hud_msg("⚠️ Groq unreachable. Falling back to Ollama.")
        logger.warning("❌ Groq intent router: all retries failed. Falling back to Ollama.")
        return None

    # ════════════════════════════════════════════════════════════
    # LAYER 3 — Ollama Offline Fallback (lazy-loaded on demand)
    # ════════════════════════════════════════════════════════════
    def _layer3_ollama(self, cmd: str, project_path: str = None) -> dict | None:
        """
        Lazy-load Ollama and run the same JSON classification prompt.
        Ollama is NOT started at startup — only here, on demand.
        """
        if not self._ensure_ollama():
            logger.error("❌ Ollama not reachable. No fallback available.")
            return self._fallback_regex(cmd, project_path)

        project_name, project_type = self._extract_project_info(project_path)

        if project_name and project_name != "None":
            user_prompt = (
                f'Current Active Project: "{project_name}" (Type: {project_type})\n'
                f'User Command: "{cmd}"\nTASK: Classify. Output JSON only.'
            )
        else:
            user_prompt = f'User Command: "{cmd}"\nTASK: Classify. Output JSON only.'

        try:
            payload = {
                "model": config.OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": self._build_system_prompt()},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 80}
            }
            response = requests.post(
                f"{config.OLLAMA_URL}/api/chat",
                json=payload,
                timeout=8
            )
            if response.status_code == 200:
                content = response.json().get("message", {}).get("content", "")
                clean = re.sub(r'```json\s*', '', content)
                clean = re.sub(r'```', '', clean).strip()
                data = json.loads(clean)
                data["intent"] = data.get("intent", "").upper()
                return data
        except Exception as e:
            logger.error(f"❌ Ollama fallback error: {e}")

        return self._fallback_regex(cmd, project_path)

    def _ensure_ollama(self) -> bool:
        """
        Check/start Ollama on-demand. Returns True if reachable.
        Only pings once per session once confirmed running.
        """
        if self._ollama_confirmed_running:
            return True
        try:
            r = requests.get(config.OLLAMA_URL, timeout=3)
            if r.status_code == 200:
                IntentRouter._ollama_confirmed_running = True
                logger.info("🏠 Ollama is available (offline fallback active)")
                return True
        except Exception:
            pass

        # Try to wake Ollama
        logger.info("📦 Attempting to start Ollama...")
        _hud_msg("Starting Ollama (offline mode)...")
        try:
            import subprocess
            subprocess.Popen(
                ["ollama", "run", config.OLLAMA_MODEL],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(4)  # Give it time to load
            r = requests.get(config.OLLAMA_URL, timeout=3)
            if r.status_code == 200:
                IntentRouter._ollama_confirmed_running = True
                _hud_msg("✅ Ollama loaded. Running in offline mode.")
                return True
        except Exception as e:
            logger.error(f"❌ Cannot start Ollama: {e}")
        return False

    # ════════════════════════════════════════════════════════════
    # HELPERS
    # ════════════════════════════════════════════════════════════
    def _ok(self, intent: str, confidence: float, thought: str) -> dict:
        return {"intent": intent, "confidence": confidence, "thought": thought}

    def _extract_project_info(self, project_path: str) -> tuple:
        if not project_path:
            return "None", "unknown"
        if os.path.exists(project_path):
            manifest = os.path.join(project_path, "jarvis_manifest.json")
            if os.path.exists(manifest):
                try:
                    with open(manifest) as f:
                        data = json.load(f)
                        name = data.get("project_name", "")
                        if name:
                            return name, data.get("stack", "unknown")
                except Exception:
                    pass
        folder = os.path.basename(project_path)
        folder = re.sub(r'_v\d+$', '', folder)
        folder = re.sub(r'_\d{8}_\d{6}$', '', folder)
        human = folder.replace("_", " ").strip()
        ptype = "unknown"
        if os.path.exists(os.path.join(project_path, "index.html")):
            ptype = "website"
        elif os.path.exists(os.path.join(project_path, "main.py")):
            ptype = "python app"
        elif os.path.exists(os.path.join(project_path, "package.json")):
            ptype = "node.js app"
        return human or "Unnamed", ptype

    def _build_system_prompt(self) -> str:
        return (
            "You are the Intent Classification Brain of Jarvis. "
            "Classify commands into: ARCHITECT_NEW, ARCHITECT_UPDATE_MINOR, ARCHITECT_UPDATE_MAJOR, "
            "WEB_SEARCH, SYSTEM_CONTROL, GENERAL_CONVERSATION. "
            'Output ONLY valid JSON: {"intent": "...", "confidence": 0.9, "thought": "..."}'
        )

    def _fallback_regex(self, command: str, project_path: str = None) -> dict:
        """Last-resort regex fallback if all LLM layers fail."""
        cmd = command.lower()

        if any(kw in cmd for kw in ["search", "who is", "what is", "find", "news"]):
            return self._ok(self.ACTION_WEB_SEARCH, 0.5, "Regex: search keywords")

        if any(kw in cmd for kw in ["volume", "brightness", "open", "lock", "mute"]):
            return self._ok(self.ACTION_SYSTEM_CONTROL, 0.5, "Regex: system keywords")

        if any(kw in cmd for kw in ["create", "build", "develop", "code a"]):
            return self._ok(self.ACTION_ARCHITECT_NEW, 0.5, "Regex: build keywords")

        return self._ok(self.ACTION_GENERAL_CONVERSATION, 0.1, "Regex: default")
