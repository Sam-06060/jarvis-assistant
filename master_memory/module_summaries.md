# Module Summaries

## Core (`core/`)
| Module | Description |
| :--- | :--- |
| `registry.py` | Global `ServiceRegistry` for cross-component access. |
| `mcp.py` | Model Context Protocol layer for structured tool/skill execution. |
| `proxy.py` | Lazy-loading proxy system for heavy module initialization. |
| `events.py` | Event management for system-wide notifications. |
| `health.py` | System health monitoring and crash reporting. |
| `interfaces.py` | Abstract base classes for core components. |

## Primary Modules (`modules/`)
| Module | Description |
| :--- | :--- |
| `agent_core.py` | The main ReAct orchestration loop with execution guards and session tracking. |
| `brain.py` | Interface to the LLM (Large Language Model) for natural language understanding. |
| `speech.py` | STT (Speech-to-Text) and TTS (Text-to-Speech) using Apple's native frameworks. |
| `commands.py` | Command processor that maps natural language to specific tools/skills. |
| `planner.py` | Breaks down complex tasks into a multi-step execution plan. |
| `semantic_router.py` | Routes requests to the most appropriate skill based on semantic similarity. |
| `socket_server.py` | API server (Port 8492) for HUD and UI integration. |
| `intent_router.py` | Classifies user intent to determine if a request needs the Agent or a direct tool. |
| `memory_manager.py` | Manages long-term and short-term knowledge storage. |

## Specialized Managers (`modules/`)
| Module | Description |
| :--- | :--- |
| `alarm_manager.py` | Handles setting and triggering alarms. |
| `calendar_manager.py` | Integration with macOS/iCloud calendars. |
| `clipboard_manager.py` | Access and manipulation of the system clipboard. |
| `file_manager.py` | High-level file operations (read/write/search). |
| `focus_manager.py` | Manages macOS Focus modes and system distractions. |
| `cursor_control.py` | Computer Vision based cursor and mouse control. |
| `smartthings.py` | Integration with Samsung SmartThings IoT devices. |

## Utilities (`utils/`)
| Module | Description |
| :--- | :--- |
| `logger.py` | Custom `JarvisLogger` with HUD stream support. |
| `audio_manager.py` | Handles media ducking, sound effects, and volume. |
| `offline_cache.py` | Caching layer for persistent data and API responses. |
| `permission_checker.py` | Verifies macOS permissions (Camera, Mic, Accessibility). |
