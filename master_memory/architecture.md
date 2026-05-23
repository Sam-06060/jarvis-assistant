# Jarvis Architecture Overview

## System Philosophy
Jarvis is designed as a **Hyper-Parallel, Agentic Assistant** for macOS. It prioritizes "Warp Speed" startup and low-latency interaction, utilizing a decoupled, service-oriented architecture.

## Core Components

### 1. The Registry Pattern (`core/registry.py`)
Centralized service discovery. All major components (Speech, Brain, History, etc.) register themselves here, allowing any part of the system to access shared services without tight coupling.

### 2. Service Proxy & Lazy Loading (`core/proxy.py`)
To achieve sub-8-second boot times, heavy modules are wrapped in `ServiceProxy` objects. These proxies register themselves immediately but only initialize the underlying heavy module when first invoked, often in background threads.

### 3. MCP Layer (Model Context Protocol) (`core/mcp.py`)
A structured communication protocol for tool execution.
- **MCPClient**: The interface used by the Agent/Brain to call tools.
- **MCPServer**: Routes calls, measures latency, and handles "Tier-2" confirmation gates for sensitive actions.

### 4. Agentic Engine (`modules/agent_core.py`)
The "Smart" layer of Jarvis.
- **ReAct Loop**: Reasoning -> Action -> Observation.
- **SessionState**: Explicitly tracks tool outputs to prevent LLM hallucinations.
- **Execution Guards**: Includes deduplication, retry caps, and "Check-Before-Act" file verification.
- **Fast Paths**: Trivial or conversational tasks bypass the complex agent loop for instant response.

### 5. Communication Stack
- **Socket Server**: Facilitates real-time communication with external UIs (e.g., Swift HUD).
- **HUD (Head-Up Display)**: Provides visual feedback on system state, user input, and agent progress.
- **Speech Engine**: Ultra-fast Apple Speech framework integration for low-latency STT/TTS.

## Startup Pipeline (Nuclear Startup)
1. **T+0ms**: `_warp_speed_prewarm` begins background imports of heavy libraries (pandas, numpy, etc.).
2. **T+100ms**: Socket Server binds immediately to allow UI connection.
3. **Parallel Wave 1**: Core interaction systems (Speech, History, Files) initialize in a `ThreadPoolExecutor`.
4. **Parallel Wave 2**: Dependent heavies (Brain, Commander) initialize as soon as Wave 1 dependencies are met.
5. **Background Sync**: Agentic mode, Semantic Router, and optional modules (Alarms, Weather) load without blocking the main loop.

## Design Aesthetic
The system is built to feel "Premium and Alive," with micro-animations in the HUD and smooth audio transitions (ducking/restoring media during speech).
