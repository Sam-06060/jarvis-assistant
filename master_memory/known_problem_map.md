# Known Problem Map

## Critical Runtime Issues
| ID | Problem | Context | Current Status |
| :--- | :--- | :--- | :--- |
| **P-001** | **Camera Session Race** | FaceID and CursorControl both request camera access. Sequential initialization often fails on macOS. | 🚧 Investigating delay-based fix. |
| **P-002** | **Startup Race Condition** | `AlarmSkill` sometimes attempts to initialize before the `ServiceRegistry` is fully populated. | ✅ Fixed with `_LiveContext` dynamic proxy in `commands.py`. |
| **P-003** | **POSIX Error 8** | "Exec format error" when launching the backend on certain macOS environments. | 🔍 Suspected binary compatibility or script header issue. |
| **P-004** | **ctypes SIGSEGV on Boot** | `SCNetworkReachability` called via `ctypes` without declaring 64-bit argtypes/restype. Truncated pointer → instant segfault (signal 11) immediately after Groq observer log. | ✅ Fixed: removed all ctypes code; replaced with pure socket-poll observer in `groq_client.py`. |
| **P-005** | **Mic Lockout After Audio Hot-Swap** | Rapid successive hot-swaps (System Default → Built-In within <2s) caused `_reinit_audio_system` to destroy the PyAudio stream without re-opening it. PortAudio device enumeration also returns stale handles when recreated too quickly. | ✅ Fixed: debounce lock (2s), force stream re-open + validation read after every reinit in `recorder.py`. |

## Logical & Behavioral Issues
| ID | Problem | Context | Current Status |
| :--- | :--- | :--- | :--- |
| **L-001** | **Intent Collision** | "Room temperature" is frequently classified as "Weather" (web search) instead of a local sensor check. | 🛠️ Needs intent priority refining. |
| **L-002** | **Persona Over-Engineering** | Agent tends to create complex plans for trivial tasks like "get a stock price." | ✅ Mitigated with "Fast Path" guards in `AgentCore`. |
| **L-003** | **Stuck Planner** | In complex multi-step tasks, the agent sometimes loops on the same failed command. | ✅ Fixed with `SessionState` deduplication. |

## Infrastructure & Environment
| ID | Problem | Context | Current Status |
| :--- | :--- | :--- | :--- |
| **E-001** | **Dependency Bottleneck** | Importing `yfinance`, `sklearn`, and `numpy` adds > 3s to boot time. | ✅ Fixed with `_warp_speed_prewarm` and background imports. |
| **E-002** | **Token Budget Exhaustion** | Long agent sessions consume large amounts of context, leading to slow or truncated responses. | ✅ Mitigated with `ContextCompressor`. |
| **E-003** | **Stale App Context (Service Registry)** | `CommandProcessor` captured `app_context` as a static dict at boot; async-registered services (alarms, weather) were always `None`. | ✅ Fixed with `_LiveContext` proxy in `commands.py` that does live `ServiceRegistry` lookups. |
| **E-004** | **Blind Cloud Retry Storm** | `GroqClient` retried the cloud API on every prompt even after the circuit was open, causing ~90s latency during network outage. | ✅ Fixed with persistent circuit-breaker + socket-poll recovery observer in `groq_client.py`. |
