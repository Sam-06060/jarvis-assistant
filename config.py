import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

# ============== AUDIO I/O SETTINGS ==============
FORCE_MAC_BUILTIN_AUDIO = True

# Assistant Configuration
ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Jarvis")
USER_NAME = os.getenv("USER_NAME", "Sir")
USER_EMAIL = os.getenv("USER_EMAIL", "samson06060@gmail.com")

# API Keys
PICOVOICE_API_KEY = os.getenv("PICOVOICE_API_KEY")

# Wake Words
EXIT_WORDS = ["exit", "quit", "goodbye", "bye jarvis", "shutdown", "shut down", "power off", "terminate", "bye"]
STOP_WORDS = ["stop", "quiet", "enough", "that's all", "never mind", "cancel", "standby"]

# macOS Applications
MAC_APPS = {
    "calculator": "Calculator",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "firefox": "Firefox",
    "finder": "Finder",
    "notes": "Notes",
    "calendar": "Calendar",
    "mail": "Mail",
    "spotify": "Spotify",
    "music": "Music",
    "vscode": "Visual Studio Code",
    "code": "Visual Studio Code",
    "terminal": "Terminal",
    "messages": "Messages",
    "facetime": "FaceTime",
    "photos": "Photos",
    "netflix": "Netflix",
    "discord": "Discord",
    "slack": "Slack",
    "zoom": "zoom.us",
}

# Response Behavior
REQUIRE_CONFIRMATION_FOR = ["delete", "remove", "shutdown", "restart", "quit"]

# System Settings
MEMORY_LIMIT_MB = 500  # Auto-cleanup if memory exceeds this

# Privacy Settings
CONVERSATION_HISTORY_DAYS = 30  # Auto-delete after X days
ENCRYPT_STORED_DATA = False  # Future feature

# VAD Settings (Ultra-Fast Response)
# Resetting to stable values for natural conversation
VAD_SILENCE_DURATION = 0.6  # 600ms (Stable)
VAD_MIN_SPEECH_DURATION = 0.3

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = BASE_DIR  # Alias used by agent_skills modules
DATA_DIR = os.path.join(BASE_DIR, "data")
MEMORY_FILE = os.path.join(DATA_DIR, "memory.json")
REMINDERS_FILE = os.path.join(DATA_DIR, "reminders.json")
SHORTCUTS_FILE = os.path.join(DATA_DIR, "shortcuts.json")
CONVERSATION_HISTORY_FILE = os.path.join(DATA_DIR, "conversation_history.json")
ANALYTICS_FILE = os.path.join(DATA_DIR, "analytics.json")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")

# Persona (Dynamic)
PERSONA_FILE = os.path.join(DATA_DIR, "persona.txt")


# ============== PERFORMANCE OPTIMIZATIONS ==============

# ============== VOICE ENGINE SETTINGS ==============
# NEW: Custom Voice Engine with Apple Speech Recognition
USE_APPLE_SPEECH = True  # Use native macOS Speech Recognition (<200ms latency!)
APPLE_SPEECH_ON_DEVICE = True  # Force on-device processing (privacy + speed)
VOICE_ENGINE_FALLBACK = True  # Fallback to Whisper if Apple fails

# Legacy: Faster Whisper (Fallback Engine)
WHISPER_MODEL_SIZE = "base"  # Options: tiny, base, small, medium, large
WHISPER_DEVICE = "cpu"       # M4 CPU is faster than GPU for Whisper
WHISPER_COMPUTE_TYPE = "int8"  # Quantization for speed

# ============== LAZY LOADING ==============
LAZY_LOAD_WHISPER = True       # Don't load Whisper at startup; load on first Apple Speech failure
LAZY_LOAD_CURSOR = True        # Don't load MediaPipe at startup; load on "cursor control" command


# Voice Settings - FASTER SPEECH
VOICE_RATE = 240  # Increased from 200 (20% faster)
VOICE_FEEDBACK_LEVEL = "verbose"  # Changed from "brief" to allow full responses

# Conversation History - REDUCE MEMORY
MAX_CONVERSATION_HISTORY = 10  # Reduced from 10
STORE_CONVERSATION_HISTORY = True  # Enabled for Memory

# Analytics - DISABLE FOR INSTANT STARTUP
ENABLE_ANALYTICS = True  # Enabled for system stats

# Startup - SKIP HEALTH CHECKS
CHECK_HEALTH_ON_STARTUP = False  # Disabled for instant boot
DISABLE_HUD = True               # Use plain terminal logs instead of Rich Iron Man HUD

# Command Confirmation - DISABLE FOR INSTANT ACTIONS
ENABLE_COMMAND_CONFIRMATION = False  # Disabled

# Keep these enabled (they're fast)
ENABLE_FUZZY_MATCHING = True
ENABLE_OFFLINE_MODE = True
ENABLE_VOICE_ACTIVITY_DETECTION = True

# Disable for speed (adjust based on what you use)
ENABLE_CONTEXT_AWARENESS = False
ENABLE_LONG_TERM_MEMORY = False
STREAMING_RESPONSES = False
ENABLE_CONVERSATION_SUMMARIES = False

# Optional Features - Disable what you don't use
ENABLE_CALENDAR = False
ENABLE_CLIPBOARD = False
ENABLE_NEWS = True
ENABLE_TRANSLATION = False
ENABLE_FOCUS_MODE = False

# Keep enabled (commonly used)
ENABLE_REMINDERS = True
ENABLE_MUSIC_CONTROL = True
ENABLE_WEATHER = True
ENABLE_EMAIL = True
ENABLE_CALCULATOR = True
ENABLE_ALARMS = True

# ============== CURSOR CONTROL SETTINGS ==============
ENABLE_CURSOR_CONTROL = True
CURSOR_CAMERA_INDEX = 0

# REMOVE CURSOR_SMOOTHING (We now use adaptive logic)
# REMOVE DRAG_DELAY (We will handle this internally for better feel)

CURSOR_SPEED = 4.0     # Keep this speed
CLICK_THRESHOLD = 10     # Tighter pinch required (was 30)
CLICK_COOLDOWN = 0.5     # Seconds before next click possible

# ============== PROXIMITY SECURITY ==============
ENABLE_PROXIMITY_LOCK = True
PHONE_MAC_ADDRESS = os.getenv("PHONE_MAC_ADDRESS")

# ============== FACE ID ==============
ENABLE_FACE_ID = True # <--- Master Toggle for Face ID Animation & Check
REFERENCE_IMAGE_PATH = os.getenv("REFERENCE_IMAGE_PATH", os.path.join(DATA_DIR, "me.jpg"))

# ============== VOICE ID (Speaker Verification) ==============
ENABLE_VOICE_ID = False
VOICE_ID_THRESHOLD = 0.25       # Cosine similarity threshold (0.0–1.0, lower = stricter)
VOICE_ID_MODEL_DIR = os.path.join(DATA_DIR, "models", "spkrec-ecapa-voxceleb")
VOICE_ID_EMBEDDINGS_DIR = os.path.join(DATA_DIR, "voice_id")



# ============== OLLAMA CONFIG (Simple/Local) ==============
OLLAMA_URL = "http://localhost:11434" # Default Port
OLLAMA_MODEL = "llama3.2" # 3B Model (Cool & Fast)

# ============== GROQ CONFIG (Cloud Code Generation) ==============
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "qwen/qwen3-32b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MAX_TOKENS = 8192
GROQ_INTENT_MODEL = "llama-3.3-70b-versatile"  # Fast, smart model for Intent Analysis

# ============== CLOUD-FIRST CONVERSATION ==============
CLOUD_FIRST_CONVERSATION = True  # Route general conversation through Groq cloud
GROQ_CONVERSATION_MODEL = "llama-3.3-70b-versatile"
GROQ_CONVERSATION_TIMEOUT = 15  # Fallback to Ollama if cloud is slow

# ============== INTENT ROUTER (Cloud-First, Ollama Fallback) ==============
INTENT_ROUTER_MODEL = "llama-3.1-8b-instant"   # Fast Groq model for intent classification
INTENT_ROUTER_MAX_TOKENS = 150                  # Forced tool_choice needs ~120 tokens for response
INTENT_ROUTER_GROQ_RETRIES = 3                  # Retry attempts before falling back to Ollama
INTENT_ROUTER_GROQ_RETRY_WAIT = 10              # Seconds between retries

# ============== OPENROUTER CONFIG (Primary Code Generation) ==============
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
# OPENROUTER_MODEL = "google/gemma-4-26b-a4b-it:free"
# OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# OPENROUTER_MAX_TOKENS = 32000

# ============== NVIDIA CONFIG (Primary Code Generation) ==============
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = "nvidia/llama-3.3-nemotron-super-49b-v1"  # Updated: qwen2.5-coder-32b EOL'd 2026-05-12
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NVIDIA_MAX_TOKENS = 8192

# ============== GEMINI CONFIG (Optional) ==============
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"
DEV_MODE = False

# ============== AGENTIC LLM (MASTER CONTROL) ==============
# Set MASTER_AGENTIC_KEY in your .env file for security. 
# JARVIS will auto-detect the provider (Groq, Gemini, or OpenRouter).
MASTER_AGENTIC_KEY = os.getenv("MASTER_AGENTIC_KEY", "")
AUTO_DETECT_AGENTIC_PROVIDER = True

# Choose your provider manually ONLY if auto-detect is False: "groq", "openrouter", "gemini", "ollama"
AGENTIC_LLM_PROVIDER = os.getenv("AGENTIC_LLM_PROVIDER", "groq")

# Choose your model for the agentic loop
# Default: llama-3.3-70b-versatile (Groq), gemini-2.0-flash (Gemini), stepfun/step-3.5-flash:free (OpenRouter)
AGENTIC_LLM_MODEL = os.getenv("AGENTIC_LLM_MODEL", "llama-3.3-70b-versatile")

# ============== AGENTIC MODE (Modular/Toggleable) ==============
ENABLE_AGENTIC_MODE = True
ENABLE_PLANNER_SPLIT = False  # DISABLED: StatelessPlanner created plan-within-plan loops. AgentCore.TaskPlanner handles all agentic tasks directly.
AGENTIC_MAX_ITERATIONS = 20  # Max steps in a single ReAct loop (hard capped by execution guards)
AGENTIC_TIMEOUT_SECONDS = 300 # Per-step guards handle real limits; this is the outer bound'
TOOL_CALL_MAX_RETRIES = 3    # Bounds: 0-5 — each retry MUST use a different approach

# ============== HEARTBEAT & PLAN MODE ==============
HEARTBEAT_MAX_SILENCE_SECONDS = 3  # Max seconds before a generic heartbeat pulse is emitted
PLAN_MODE_ENABLED = True            # Enable inline PLAN.md rendering in chat UI
PLAN_PROJECTS_DIR = os.path.expanduser("~/Jarvis/Projects")

@dataclass
class AgentConfig:
    enabled: bool = field(default=False)
    max_iterations: int = field(default=20)
    timeout: int = field(default=300)
    retry_budget: int = field(default=3)

    def validate(self):
        """Strict bounds validation as per implementation plan"""
        self.max_iterations = max(1, min(30, self.max_iterations))  # Hard cap at 30
        self.timeout = max(5, min(3600, self.timeout))
        self.retry_budget = max(0, min(10, self.retry_budget))

# ============== SMARTTHINGS CONFIGURATION ==============
SMARTTHINGS_PAT = os.environ.get("SMARTTHINGS_PAT")
SMARTTHINGS_DEVICE_ID = os.environ.get("SMARTTHINGS_DEVICE_ID")

# OAuth credentials for the Swift JarvisACController bridge
# These are read directly by the Swift app from its process environment.
# They are declared here so config.py is the single source of truth for all env vars.
ST_CLIENT_ID     = os.environ.get("ST_CLIENT_ID", "")
ST_CLIENT_SECRET = os.environ.get("ST_CLIENT_SECRET", "")
ST_DEVICE_ID     = os.environ.get("ST_DEVICE_ID", SMARTTHINGS_DEVICE_ID or "")
ST_ACCESS_TOKEN  = os.environ.get("ST_ACCESS_TOKEN", "")
ST_REFRESH_TOKEN = os.environ.get("ST_REFRESH_TOKEN", "")

# Boot validation — warn if secrets are missing
_missing = [k for k, v in {
    "SMARTTHINGS_PAT": SMARTTHINGS_PAT,
    "SMARTTHINGS_DEVICE_ID": SMARTTHINGS_DEVICE_ID,
}.items() if not v]

if _missing:
    import warnings
    warnings.warn(
        f"[Jarvis/Config] SmartThings secrets not set: {', '.join(_missing)}. "
        "AC control will be unavailable until these are configured.",
        RuntimeWarning,
        stacklevel=2,
    )

