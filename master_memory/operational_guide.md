# Operational Guide

## Execution Commands
| Task | Command |
| :--- | :--- |
| **Start Jarvis** | `./start_jarvis.sh` |
| **Backend Only** | `./start_backend_only.sh` |
| **Run Tests** | `./test_backend.sh` |
| **Health Check** | `python3 modules/health_checker.py` |
| **Clean Sandbox** | `rm -rf ~/.jarvis_sandbox/*` |

## Debugging & Logs
- **Main Log**: `tail -f logs/jarvis.log`
- **Import Times**: `cat import_times.log` (Check for boot bottlenecks).
- **HUD Stream**: Monitor the socket server on port `8492`.

## System Management
### Adding New Tools
1. Create the tool class in `modules/agent_skills/`.
2. Register it in `modules/agent_skills/_registry.json`.
3. (Optional) Run `SemanticRouter.instance().boot()` to update embeddings.

### Updating the Persona
Modify `data/persona.txt` to adjust Jarvis's conversational tone or core directives. No restart required if the module reloads it dynamically.

### Port Configuration
- **Socket Server**: `8492` (Used for HUD/UI).
- **Ollama**: `11434` (Local LLM fallback).

## Troubleshooting "POSIX Error 8"
If the backend fails to launch with an "Exec format error":
1. Check the shebang line in `jarvis.py` and start scripts.
2. Ensure the virtual environment (`.venv`) is activated.
3. Verify binary compatibility of native extensions (e.g., `pvporcupine`).
