# Dependency Graph

```mermaid
graph TD
    subgraph Core_Engine
        jarvis[jarvis.py] --> Registry[ServiceRegistry]
        jarvis --> Socket[SocketServer]
        jarvis --> Parallel[ThreadPoolExecutor]
    end

    subgraph Interaction_Layer
        Registry --> Speech[SpeechEngine]
        Registry --> History[ConversationHistory]
        Registry --> HUD[HUD Queue]
    end

    subgraph Intelligence_Stack
        Registry --> Brain[AIBrain]
        Registry --> Agent[AgentCore]
        Agent --> Planner[TaskPlanner]
        Agent --> Router[SemanticRouter]
        Agent --> Budget[TokenBudget]
        Agent --> Session[SessionState]
    end

    subgraph MCP_Protocol
        Agent --> MCPClient[MCPClient]
        MCPClient --> MCPServer[MCPServer]
        MCPServer --> Tools[Skill Handlers]
    end

    subgraph External_Services
        Tools --> Weather[WeatherService]
        Tools --> Stocks[YFinance]
        Tools --> SmartHome[SmartThings]
        Tools --> System[SystemInfo / Files]
    end

    %% Initialization Flow
    Parallel -- initiates --> Speech
    Parallel -- initiates --> Brain
    Parallel -- initiates --> History
    
    %% Communication Flow
    Socket -- sends_input --> jarvis
    jarvis -- updates --> HUD
    Logger[JarvisLogger] -- pipes_to --> HUD
```

## Structural Logic
1. **The Registry** is the central hub. All components depend on it for cross-module communication.
2. **AgentCore** orchestrates the high-level intelligence, depending on the **Brain** for reasoning and the **MCP Layer** for action.
3. **SpeechEngine** is the primary input/output gate for voice-based interaction.
4. **SocketServer** provides the bridge to the Swift-based visual interface (HUD).
