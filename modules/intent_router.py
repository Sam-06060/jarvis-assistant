
import json
import os
import re
import requests
import config


class IntentRouter:
    """
    Intelligent Intent Engine (Stage 8).
    Uses LOCAL Ollama for classification (tiny inference, no heat).
    Cloud Groq is reserved for actual conversation.
    """
    
    # Intent Constants
    ACTION_ARCHITECT_NEW = "ARCHITECT_NEW"
    ACTION_ARCHITECT_UPDATE_MINOR = "ARCHITECT_UPDATE_MINOR"
    ACTION_ARCHITECT_UPDATE_MAJOR = "ARCHITECT_UPDATE_MAJOR"
    ACTION_WEB_SEARCH = "WEB_SEARCH"
    ACTION_SYSTEM_CONTROL = "SYSTEM_CONTROL"
    ACTION_GENERAL_CONVERSATION = "GENERAL_CONVERSATION"
    
    def __init__(self):
        self.model = config.OLLAMA_MODEL  # Local Llama 3.2 — fast, no rate limits
        print(f"🧠 Intent Engine Initialized (Local: {self.model})")

    # ============================================================
    # PUBLIC: Analyze user command
    # ============================================================
    # Non-architect keywords: commands that should NEVER go to Architect
    NON_ARCHITECT_KEYWORDS = [
        "contact", "email", "mail", "call", "message", "text",
        "reminder", "alarm", "timer", "weather", "news",
        "music", "play", "pause", "volume", "brightness",
        "battery", "translate", "calculate", "stop", "exit",
        "shut down", "sleep", "cursor control", "shortcut",
    ]

    def analyze(self, command: str, previous_project_path: str = None) -> dict:
        """
        Analyze user command with semantic project context.
        Uses LOCAL Ollama (tiny inference, ~50 tokens output).
        """
        cmd_lower = command.lower()
        
        # --- ULTRA-SHORT GUARD: 1-2 word commands are NEVER code architect ---
        if len(cmd_lower.split()) <= 2:
            return {"intent": self.ACTION_GENERAL_CONVERSATION, "confidence": 0.9,
                    "reason": "Ultra-short command — not architect"}
        
        # --- PRE-FILTER: Skip NLP for obvious non-architect commands ---
        if any(kw in cmd_lower for kw in self.NON_ARCHITECT_KEYWORDS):
            return {"intent": self.ACTION_GENERAL_CONVERSATION, "confidence": 0.9,
                    "reason": "Pre-filter: non-architect keyword detected"}
        
        # --- PHASE 8.1: Extract semantic project info ---
        project_name, project_type = self._extract_project_info(previous_project_path)
        has_context = bool(project_name and project_name != "None")
        
        # --- PHASE 8.2: Build prompt with Subject Comparison ---
        system_prompt = self._build_system_prompt()
        
        if has_context:
            user_prompt = f"""
Current Active Project: "{project_name}" (Type: {project_type})
User Command: "{command}"

TASK: Determine if this command is about the SAME project ("{project_name}") or a COMPLETELY DIFFERENT one.
Output JSON only.
"""
        else:
            user_prompt = f"""
Current Active Project: None (No project is open)
User Command: "{command}"

TASK: Classify this command. Output JSON only.
"""
        
        # Call LOCAL Ollama (fast, no rate limits, minimal heat)
        response = self._call_local(user_prompt, system_prompt)
        
        if not response:
            print("⚠️ Intent Router gave no response. Falling back to REGEX.")
            return self._fallback_regex(command, project_name)
            
        try:
            # Clean JSON from markdown wrappers
            clean_json = re.sub(r'```json\s*', '', response)
            clean_json = re.sub(r'```', '', clean_json).strip()
            
            data = json.loads(clean_json)
            data["intent"] = data.get("intent", "").upper()
            
            print(f"🧠 Intent Detected: {data.get('intent')} (Conf: {data.get('confidence')}) | Thought: {data.get('thought', 'N/A')[:80]}")
            return data
            
        except json.JSONDecodeError:
            print(f"❌ Intent Router JSON Error. Raw: {response[:200]}")
            return self._fallback_regex(command, project_name)
            
        except Exception as e:
            print(f"❌ Intent Router Error: {e}")
            return self._fallback_regex(command, project_name)

    # ============================================================
    # LOCAL: Call Ollama for intent classification
    # ============================================================
    def _call_local(self, prompt, system_prompt=None):
        """Call local Ollama for intent classification. Fast, no rate limits."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 200  # Intent JSON is ~50 tokens, cap at 200 for safety
                }
            }
            
            response = requests.post(
                f"{config.OLLAMA_URL}/api/chat",
                json=payload,
                timeout=8
            )
            
            if response.status_code == 200:
                content = response.json().get("message", {}).get("content", "")
                return content
            else:
                print(f"⚠️ Ollama Intent Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Ollama Intent Exception: {e}")
            return None

    # ============================================================
    # PHASE 8.1: Extract project name + type from manifest or path
    # ============================================================
    def _extract_project_info(self, project_path: str) -> tuple:
        """
        Extract human-readable project name and type.
        
        Strategy:
        1. Try reading jarvis_manifest.json (best source).
        2. Fallback: Parse the folder name.
        3. Fallback: Return "None".
        """
        if not project_path:
            return "None", "unknown"
        
        # Strategy 1: Read manifest (only if path exists)
        if os.path.exists(project_path):
            manifest_path = os.path.join(project_path, "jarvis_manifest.json")
            if os.path.exists(manifest_path):
                try:
                    with open(manifest_path, "r") as f:
                        data = json.load(f)
                        name = data.get("project_name", "")
                        stack = data.get("stack", "unknown")
                        if name:
                            return name, stack
                except Exception:
                    pass
        
        # Strategy 2: Parse folder name (works even if path doesn't exist)
        folder_name = os.path.basename(project_path)
        
        # Remove version suffixes like _v2, _v3
        folder_name = re.sub(r'_v\d+$', '', folder_name)
        
        # Remove timestamp portion (e.g. _20260219_041812)
        folder_name = re.sub(r'_\d{8}_\d{6}$', '', folder_name)
        
        # Convert underscores to spaces for readability
        human_name = folder_name.replace("_", " ").strip()
        
        # Detect type from files present
        project_type = "unknown"
        if os.path.exists(os.path.join(project_path, "index.html")):
            project_type = "website (HTML/CSS/JS)"
        elif os.path.exists(os.path.join(project_path, "main.py")):
            project_type = "python app"
        elif os.path.exists(os.path.join(project_path, "package.json")):
            project_type = "node.js app"
        
        return human_name if human_name else "Unnamed Project", project_type

    # ============================================================
    # PHASE 8.2: System Prompt with Subject Comparison Framework
    # ============================================================
    def _build_system_prompt(self) -> str:
        return """
You are the Intent Classification Brain of an AI Operating System called Jarvis.
Your job is to determine what the user wants to do.

## CLASSIFICATION CATEGORIES:

1. **ARCHITECT_NEW** — User wants to create a COMPLETELY NEW and DIFFERENT project.
2. **ARCHITECT_UPDATE_MINOR** — User wants to make small tweaks to the CURRENT project (colors, text, layout, add features).
3. **ARCHITECT_UPDATE_MAJOR** — User wants to significantly redesign/rewrite the CURRENT project (but keep it as the same project).
4. **WEB_SEARCH** — User wants information, facts, or news.
5. **SYSTEM_CONTROL** — User wants to control the computer (volume, brightness, open app).
6. **GENERAL_CONVERSATION** — Greetings or casual chat.

## DECISION FRAMEWORK (Follow these steps IN ORDER):

**Step 1: Identify the SUBJECT of the user's command.**
  - What is the user talking about? (e.g., "flappy bird game", "portfolio website", "calculator")

**Step 2: Compare it to the Current Active Project.**
  - Is the subject the SAME as the current project?
  - Or is it a COMPLETELY DIFFERENT thing?

**Step 3: Apply these rules:**
  - **Different subject** → `ARCHITECT_NEW` (even if user didn't say "new")
  - **Same subject + small change** (color, text, fix, add) → `ARCHITECT_UPDATE_MINOR`
  - **Same subject + big change** (recreate, redesign, overhaul) → `ARCHITECT_UPDATE_MAJOR`
  - **No current project** + creation verb → `ARCHITECT_NEW`

## FEW-SHOT EXAMPLES:

| Current Project | Command | Intent | Why |
|---|---|---|---|
| "Portfolio Website" | "Create a flappy bird game" | ARCHITECT_NEW | Different subject (game ≠ portfolio) |
| "Portfolio Website" | "Make the background blue" | ARCHITECT_UPDATE_MINOR | Same subject, small tweak |
| "Portfolio Website" | "Redesign it with glassmorphism" | ARCHITECT_UPDATE_MAJOR | Same subject, big change |
| "Portfolio Website" | "Create a new portfolio" | ARCHITECT_NEW | User explicitly says "new" |
| "Flappy Bird Game" | "Add a score counter" | ARCHITECT_UPDATE_MINOR | Same subject, adding feature |
| "Flappy Bird Game" | "Build a calculator app" | ARCHITECT_NEW | Different subject (calculator ≠ game) |
| None | "Create a landing page" | ARCHITECT_NEW | No project, creation request |
| None | "Who is the CEO of Apple?" | WEB_SEARCH | Information request |
| None | "Turn up the volume" | SYSTEM_CONTROL | System control |

## OUTPUT FORMAT:
You MUST output valid JSON only. No markdown, no explanation outside JSON.
```
{
  "thought": "Step 1: Subject is X. Step 2: Current project is Y. Step 3: X ≠ Y, so...",
  "intent": "CATEGORY",
  "confidence": 0.0-1.0
}
```
"""

    # ============================================================
    # PHASE 8.4: Upgraded Fallback with Subject Comparison
    # ============================================================
    def _fallback_regex(self, command: str, project_name: str = None) -> dict:
        """Backup logic if Brain fails. Now with basic subject comparison."""
        cmd = command.lower()
        
        # Check for non-architect intents first
        if any(kw in cmd for kw in self.NON_ARCHITECT_KEYWORDS):
            return {"intent": self.ACTION_GENERAL_CONVERSATION, "confidence": 0.9}
        
        if any(w in cmd for w in ["search", "who is", "what is", "find", "news"]):
            return {"intent": self.ACTION_WEB_SEARCH, "confidence": 0.5}
        
        if any(w in cmd for w in ["volume", "brightness", "open", "shutdown", "stop", "mute"]):
            return {"intent": self.ACTION_SYSTEM_CONTROL, "confidence": 0.5}
        
        # Architect intents — use subject comparison
        if project_name and project_name != "None":
            # Extract key nouns from both command and project name
            project_words = set(project_name.lower().split())
            command_words = set(cmd.split())
            
            # Check for subject overlap
            # Remove common filler words
            filler = {"a", "the", "and", "with", "it", "my", "is", "to", "of", "in", "for", "on", "new", "create", "build", "make"}
            project_keywords = project_words - filler
            command_keywords = command_words - filler
            
            overlap = project_keywords & command_keywords
            
            if overlap:
                # Same subject detected — it's an update
                if any(w in cmd for w in ["recreate", "redesign", "overhaul", "rewrite"]):
                    return {"intent": self.ACTION_ARCHITECT_UPDATE_MAJOR, "confidence": 0.6}
                if any(w in cmd for w in ["change", "update", "make", "add", "replace", "fix", "move"]):
                    return {"intent": self.ACTION_ARCHITECT_UPDATE_MINOR, "confidence": 0.6}
            
            # No overlap — different subject → NEW
            if any(w in cmd for w in ["create", "build", "develop", "code"]):
                return {"intent": self.ACTION_ARCHITECT_NEW, "confidence": 0.6}
        
        # No context — default creation detection
        if any(w in cmd for w in ["create", "build", "develop", "code a"]):
            return {"intent": self.ACTION_ARCHITECT_NEW, "confidence": 0.5}
        
        return {"intent": self.ACTION_GENERAL_CONVERSATION, "confidence": 0.1}
