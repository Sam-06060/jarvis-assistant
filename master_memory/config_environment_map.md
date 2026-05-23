# Configuration & Environment Map

## Core Configuration (`config.py`)
| Key | Default | Description |
| :--- | :--- | :--- |
| `USE_APPLE_SPEECH` | `True` | Uses native macOS STT for <200ms latency. |
| `ENABLE_AGENTIC_MODE`| `False` | Master toggle for the ReAct orchestration loop. |
| `LAZY_LOAD_WHISPER` | `True` | Defers loading heavy Whisper model until needed. |
| `VAD_SILENCE_DURATION`| `0.6s` | Voice Activity Detection sensitivity. |
| `AGENTIC_LLM_PROVIDER`| `groq` | Primary LLM provider for the agentic engine. |
| `VOICE_RATE` | `240` | TTS speed (20% faster than default for "Warp Speed"). |

## Environment Variables (`.env`)
| Variable | Purpose |
| :--- | :--- |
| `GROQ_API_KEY` | Primary API for Agentic reasoning and Intent analysis. |
| `PICOVOICE_API_KEY` | Used for Wake Word detection (Porcupine). |
| `SMARTTHINGS_PAT` | Personal Access Token for Samsung IoT control. |
| `MASTER_AGENTIC_KEY` | Unified key for the primary Agentic LLM provider. |
| `PHONE_MAC_ADDRESS` | Used for "Proximity Lock" security feature. |

## Feature Flags
- **`ENABLE_FACE_ID`**: Toggles camera-based user verification.
- **`CLOUD_FIRST_CONVERSATION`**: Routes general chat to Groq (Cloud) with local Ollama fallback.
- **`PLAN_MODE_ENABLED`**: Allows the agent to generate and render `PLAN.md` files in the HUD.
- **`FORCE_MAC_BUILTIN_AUDIO`**: Ensures audio I/O uses system defaults for stability.
