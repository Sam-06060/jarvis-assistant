# Conversation Memory Store

## 🧠 Architectural Decisions
- **Hyper-Parallelism**: Decision to use `ThreadPoolExecutor` and `multiprocessing` at startup to bypass Python's sequential import bottleneck.
- **Agentic Bypass (Fast Path)**: Trivial tasks (casual talk, direct market quotes) MUST bypass the Planner/Executor to save tokens and time (< 2s response target).
- **Verified Session State**: The agent is forced to use an explicit `SessionState` block for memory rather than relying on its own hidden context, significantly reducing hallucinations during complex file operations.

## 🛠️ Previous Fixes & Lessons Learned
| Context | Fix Implemented | Outcome |
| :--- | :--- | :--- |
| **Startup Lag** | Implemented `_warp_speed_prewarm` to background-import `yfinance`, `numpy`, and `pandas`. | Boot time dropped from 15s to ~9s. |
| **Agent Loops** | Added deterministic input hashing in `SessionState` to block identical duplicate actions. | Prevented "infinite loops" on failed commands. |
| **Silent Failures** | Wrapped all optional module imports in `ServiceProxy` with explicit logging. | System no longer crashes if a non-essential module (e.g., Alarms) is missing a dependency. |
| **Audio Quality** | Implemented `duck_audio` / `restore_audio` logic in `audio_manager.py`. | Created a "Premium" feel where background music dips when Jarvis speaks. |
| **Cloud Retry Storm** | Circuit-breaker in `GroqClient` + socket-poll observer in background thread. | Cloud fails 3x → circuit opens, Ollama takes over silently. Recovers in 10s when network returns. |
| **Stale Service Registry** | `_LiveContext` proxy in `commands.py` does live `ServiceRegistry.get()` on every skill call instead of using a boot-time snapshot. | AlarmSkill, WeatherSkill, etc. now always find their service regardless of init order. |
| **ctypes SIGSEGV** | Removed `SCNetworkReachability` ctypes block entirely from `groq_client.py`. Socket-poll observer only. | Backend no longer crashes on startup with signal 11. |
| **Mic Lockout Post Hot-Swap** | `recorder._reinit_audio_system()` now: (1) debounced with 2s lock, (2) force-reopens stream after reinit, (3) validates stream with a test read. | Built-in mic stays alive after rapid System Default ↔ Built-In toggles. |

## ❌ Failed Solutions (Dead Ends)
- **Direct Sequential Imports**: Attempting to load all modules in order led to boot times exceeding 20 seconds. **DO NOT RETURN TO SEQUENTIAL BOOT.**
- **Pure ReAct without State**: Relying on the LLM to "remember" file contents or tool results led to 40% failure rate in multi-step tasks. **ALWAYS USE VERIFIED SESSION STATE.**
- **Aggressive VAD (Voice Activity Detection)**: Initially set too sensitive, causing Jarvis to interrupt its own speech. **SENSITIVITY MUST REMAIN BALANCED.**
- **ctypes for macOS System APIs**: Using `ctypes` to call `SCNetworkReachability` without declaring 64-bit `argtypes`/`restype` causes an instant SIGSEGV. **NEVER USE RAW ctypes ON macOS SYSTEM FRAMEWORK FUNCTIONS WITHOUT FULL TYPE DECLARATIONS.**

## 👤 User Preferences
- **Execution Model**: Strictly pragmatic and high-speed. Avoid "Senior Architect" over-engineering loops.
- **Communication Style**: Professional, "Yes sir" / "No sir" (Jarvis persona), helpful but concise.
- **Interaction Priority**: Visual feedback via the HUD is as important as voice feedback.
- **Hardware Integration**: High focus on macOS native integration (Applescript, native Speech, FaceID).
