# Data Storage Map

All persistent system data is stored in the `data/` directory.

## Primary Files
| File | Format | Description |
| :--- | :--- | :--- |
| `knowledge.json` | JSON | Permanent long-term memory facts (`remember_fact`). |
| `memory.json` | JSON | Short-term session memory. |
| `reminders.json` | JSON | User-set reminders and their status. |
| `contacts.json` | JSON | Cached address book data for quick lookup. |
| `conversation_history.json`| JSON | Rolling log of last N conversation turns. |
| `persona.txt` | Text | Dynamic prompt instructions that define Jarvis's personality. |
| `offline_cache.json` | JSON | Cached API responses and scraped web content. |

## Specialized Storage
- **`semantic_cache.npz`**: Vector embeddings for the `SemanticRouter` to enable fast tool matching.
- **`skill_performance.json`**: Historical latency and success rates for every registered tool.
- **`file_audit.json`**: Log of all file-system modifications made by the Agent.
- **`me.jpg`**: Reference image used by `FaceID` for user verification.

## Directory Structure
- `logs/`: Contains `jarvis.log` and specialized logs for STT/TTS debugging.
- `scratch/`: Temporary workspace for scripts and one-off data processing.
- `models/`: Local storage for lightweight AI models (if any).
- `.jarvis_sandbox/`: Per-task isolated environments for safe code execution.
