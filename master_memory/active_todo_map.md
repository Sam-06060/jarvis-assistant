# Active TODO Map

## High Priority (Immediate Execution)
- [ ] **Camera Guard**: Implement a robust singleton or lock for camera access between `FaceID` and `CursorControl` to prevent AVFoundation crashes. (P-001)
- [ ] **Intent Refinement**: Modify `intent_router.py` to prioritize local sensor/smart home data over web search for keywords like "temperature", "lights", "ac". (L-001)
- [ ] **Planner Mis-routing**: Agentic planner routes `alarm`/`reminder` intents to `web_search` instead of `manage_alarms`. Fix keyword→tool hint in `planner.py`.

## System Enhancements
- [ ] **Autonomous Recovery**: Implement a watchdog in `core/health.py` that can restart crashed modules without killing the main `JarvisApp` process.
- [ ] **Memory Persistence**: Enhance `MemoryManager` to store long-term user preferences across system restarts (currently limited session memory).
- [ ] **Unified Plan View**: Expose the `TaskPlanner`'s JSON output directly to the Swift HUD for a more detailed "Progress Bar" UI.

## Agentic Improvements
- [ ] **Multi-Provider Failover**: Allow `AgentCore` to switch from Groq to Gemini or OpenAI if rate limits are hit or latency spikes.
- [ ] **Tool Discovery**: Implement dynamic tool discovery where the Agent can scan the `modules/agent_skills` folder and learn new tools without manual registration.
- [ ] **Self-Correction Logic**: If a `run_command` fails with a "Command not found", the agent should automatically attempt to search for the correct package name.

## Technical Debt
- [ ] **Refactor `commands.py`**: The file is becoming monolithic (> 40k lines in some iterations). Split into domain-specific command sets.
- [ ] **Standardize MCP Tiers**: Review all tools and ensure Tier-2 (confirmation required) is correctly applied to all side-effecting actions (delete, send email, etc.).
