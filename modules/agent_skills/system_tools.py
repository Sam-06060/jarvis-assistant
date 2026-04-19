import subprocess
import time
import logging
import os
from typing import Optional
from .base import AgentTool

logger = logging.getLogger(__name__)

class AppControlTool(AgentTool):
    name = "control_app"
    description = "Open or quit macOS applications. Input: {'action': 'open'|'quit', 'app_name': str}. Example: {'action': 'open', 'app_name': 'Safari'}"
    permission = "destructive"
    
    def run(self, inp: dict):
        action = inp.get('action', 'open').lower()
        app = inp.get('app_name')
        if not app: return "Error: app_name required."
        try:
            subprocess.run(["open", "-a", app], check=True, capture_output=True)
            return f"Successfully {action}ed {app}."
        except Exception as e:
            return f"Failed to {action} {app}. Error: {str(e)}"

class SystemControlTool(AgentTool):
    name = "system_control"
    description = "Control system volume, brightness, or lock screen. Input: {'action': 'volume_up'|'volume_down'|'mute'|'lock_screen'|'brightness_up'|'brightness_down'}"
    permission = "destructive"
    
    def run(self, inp: dict):
        action = inp.get('action')
        if not action: return "Error: action required."
        skill = self.cp._find_skill("SystemSkill")
        if not skill: return "System Skill unavailable."
        skill.handle(action.replace('_', ' '))
        return f"Successfully executed system action: {action}"

class ACControlTool(AgentTool):
    name = "control_ac"
    description = "Controls the Samsung air conditioner via SmartThings. Input: {'action': 'turn_on'|'turn_off'|'set_temperature'|'set_mode'|'get_status'|'temp_up'|'temp_down', 'temperature_celsius': int (optional), 'mode': str (optional: 'cool'|'heat'|'auto'|'dry'|'fanOnly')}"
    permission = "destructive"
    
    def _emit(self, signal: str) -> Optional[str]:
        """Relay an __AC_*__ signal via the Swift OAuth bridge."""
        server = self.cp.app_context.get('socket_server')
        if server and server.clients:
            server.broadcast_signal(signal)
            return None  # Success — caller builds the response string
        return "The Jarvis Swift app isn't connected. Make sure it's running."

    def run(self, inp: dict):
        action = inp.get("action", "")
        if action == "turn_on":
            return self._emit("__AC_ON__") or "The AC has been turned on."
        elif action == "turn_off":
            return self._emit("__AC_OFF__") or "The AC has been turned off."
        elif action == "temp_up":
            return self._emit("__AC_TEMP_UP__") or "Temperature increased by one degree."
        elif action == "temp_down":
            return self._emit("__AC_TEMP_DOWN__") or "Temperature decreased by one degree."
        elif action == "set_temperature":
            temp = int(float(inp.get("temperature_celsius", 24)))
            return self._emit(f"__AC_TEMP_{temp}__") or f"AC temperature set to {temp}°C."
        elif action == "set_mode":
            mode = str(inp.get("mode", "cool")).lower()
            return self._emit(f"__AC_MODE_{mode}__") or f"AC mode set to {mode}."
        elif action == "get_status":
            return self._emit("__AC_STATUS__") or "Fetching AC status — check the Swift app console."
        return f"Unknown AC action: '{action}'."

class SystemStatusTool(AgentTool):
    name = "get_system_status"
    description = "Get detailed information about the macOS environment (battery, CPU, memory, uptime, network)."
    permission = "safe"
    
    def run(self, inp: dict):
        sys_info = self.cp.registry.get("system")
        if not sys_info: return "System info service unavailable."
        return sys_info.get_detailed_status()

class RunningAppsTool(AgentTool):
    name = "get_running_apps"
    description = "Get a list of currently open applications on this Mac."
    permission = "safe"
    
    def run(self, inp: dict):
        sys_info = self.cp.registry.get("system")
        if not sys_info: return "System info service unavailable."
        return sys_info.get_running_apps()

class ClipboardTool(AgentTool):
    name = "clipboard"
    description = "Read or write to the macOS clipboard. Input: {'action': 'read'|'write', 'text': str (for write)}"
    permission = "write"
    
    def run(self, inp: dict):
        clipboard_mgr = self.cp.registry.get("clipboard")
        if not clipboard_mgr: return "Clipboard manager unavailable."
        if inp.get('action') in ('write', 'copy'):
            return clipboard_mgr.copy(inp.get('text', ''))
        return clipboard_mgr.paste()

class TerminalExecutorTool(AgentTool):
    name = "run_command"
    description = "Execute a bash command on the local machine natively. Extremely powerful. IMPORTANT: State is NOT shared between calls. By default, this tool automatically executes inside your active sandbox directory if one exists! Do not try to `cd` to the sandbox yourself. If you need to execute something against the main user project or entirely outside your sandbox, you MUST manually `cd` using absolute paths. ALL commands MUST be 100% non-interactive (e.g. use `-y`). If you spawn an interactive command, the backend will freeze! Input: {'command': str, 'description': str, 'risk_level': 'Low'|'Medium'|'Critical', 'reasoning': str}"
    permission = "destructive"
    self_approving = True  # Has its own socket-based "Approve & Run" UI — skip voice gate
    
    def run(self, inp: dict):
        command = inp.get('command', '')
        desc = inp.get('description', 'No description provided.')
        risk = inp.get('risk_level', 'Medium')
        
        if not command:
            return "Error: No command provided to run."
            
        import uuid
        import threading
        import json
        import subprocess
        
        req_id = str(uuid.uuid4())
        server = self.cp.app_context.get("socket_server")
        if not server:
            return "Observation: Socket server offline. Cannot prompt user for approval."
            
        if not hasattr(server, 'approval_events'):
            server.approval_events = {}
            server.approval_results = {}
            
        event = threading.Event()
        server.approval_events[req_id] = event
        
        reasoning = inp.get('reasoning', 'No reasoning provided.')
        
        payload = {
            "command": command,
            "description": desc,
            "risk": risk,
            "reasoning": reasoning
        }
        
        payload_data = json.dumps({
            "type": "approval_request",
            "header": req_id,
            "data": json.dumps(payload)
        }) + "\n"
        
        # Broadcast the request
        for c in server.clients:
            try:
                c.sendall(payload_data.encode('utf-8'))
            except: pass
            
        # Keep HUD "Thinking" State alive so the Swift framework doesn't think the Agent locked up
        hud_pulse = json.dumps({
            "type": "partial",
            "data": f"⏸️ Awaiting Sandbox Approval before executing: {command[:25]}..."
        }) + "\n"
        for c in server.clients:
            try:
                c.sendall(hud_pulse.encode('utf-8'))
            except: pass
            
        # Wait up to 5 minutes for User UI interaction
        event.wait(timeout=300)
        
        approved = server.approval_results.get(req_id, False)
        
        # Cleanup
        server.approval_events.pop(req_id, None)
        server.approval_results.pop(req_id, None)
        
        if not approved:
            return "CRITICAL ERROR: Execution EXPLICITLY REJECTED by User. DO NOT RETRY this command or any similar variant. You MUST stop your execution plan and ask the user for clarification immediately."
            
        try:
            # Execute Native Command
            # Use sandbox directory if available in the current task memory_vault
            cwd = self.cp.memory_vault.get("_sandbox_dir") if hasattr(self.cp, 'memory_vault') and isinstance(self.cp.memory_vault, dict) else None
            
            # Reassure user of sandbox isolation
            sandbox_header = f"🏠 [SANDBOX MODE ACTIVE: {cwd}]\n" if cwd else "⚠️ [NO SANDBOX FOUND - EXECUTING IN OS CONTEXT]\n"
            logger.info(f"🐚 [Terminal] {sandbox_header.strip()}")
            
            # AUTO-ACTIVATE VENV: If a venv exists in the sandbox, ensure it's used natively.
            if cwd and os.path.isdir(os.path.join(cwd, "venv")):
                if not command.startswith("source venv/"):
                    command = f"source venv/bin/activate && {command}"
                    logger.info(f"🐚 [Terminal] Auto-injected venv activation for command.")

            # Note: We must use executable='/bin/bash' because 'source' is a bash built-in, not purely POSIX sh.
            result = subprocess.run(command, shell=True, executable='/bin/bash', capture_output=True, text=True, timeout=120, cwd=cwd)
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            rc = result.returncode
            
            # Combine header with output
            final_output = f"{sandbox_header}{stdout}" if stdout else sandbox_header

            # ── ERROR MEMORY: Persist stderr for cross-iteration learning ──
            if rc != 0 or stderr:
                error_log = {
                    "command": command,
                    "stderr": stderr[:2000],
                    "returncode": rc,
                    "timestamp": time.time()
                }
                if hasattr(self.cp, 'memory_vault') and isinstance(self.cp.memory_vault, dict):
                    errors = self.cp.memory_vault.get("_error_log", [])
                    errors.append(error_log)
                    self.cp.memory_vault["_error_log"] = errors[-5:]
                    logger.info(f"🧠 Error Memory: Captured stderr for '{command[:40]}...'")

            # ── SMART ERROR INTERPRETATION ────────────────────────────────────
            # When the command fails, classify the error so the agent can
            # give a sensible human-readable response instead of raw stderr.
            if rc != 0 or (stderr and not stdout):
                combined = (stderr + " " + stdout).lower()

                if "no such file or directory" in combined or "can't open file" in combined:
                    human = (
                        f"ERROR — File or directory not found.\n"
                        f"The path referenced in `{command}` does not exist on this machine.\n"
                        f"Raw error: {stderr}"
                    )
                elif "permission denied" in combined:
                    human = (
                        f"ERROR — Permission denied.\n"
                        f"You don't have the required permissions to run `{command}`.\n"
                        f"Raw error: {stderr}"
                    )
                elif "command not found" in combined:
                    cmd_name = command.split()[0] if command.split() else command
                    human = (
                        f"ERROR — Command not found: `{cmd_name}`.\n"
                        f"This program is not installed or not in PATH.\n"
                        f"Raw error: {stderr}"
                    )
                elif "modulenotfounderror" in combined or "no module named" in combined:
                    human = (
                        f"ERROR — Missing Python module.\n"
                        f"A required Python package is not installed.\n"
                        f"Raw error: {stderr}"
                    )
                elif "syntaxerror" in combined or "invalid syntax" in combined:
                    human = (
                        f"ERROR — Syntax error in the script.\n"
                        f"The code has a Python syntax mistake and cannot run.\n"
                        f"Raw error: {stderr}"
                    )
                elif "connection refused" in combined or "network" in combined:
                    human = (
                        f"ERROR — Network or connection issue.\n"
                        f"Raw error: {stderr}"
                    )
                else:
                    human = (
                        f"ERROR (exit code {rc}).\n"
                        f"Raw error: {stderr or stdout}"
                    )

                return f"Execution Result (FAILED):\n{human}"

            # ── SUCCESS PATH ──────────────────────────────────────────────────
            output = final_output
            if not output:
                return f"{sandbox_header}Command executed successfully but produced no output."

            # Protect context limits by truncating very long outputs
            if len(output) > 4000:
                output = output[:2000] + "\n\n...[OUTPUT TRUNCATED (PROTECTING TOKEN LIMITS)]...\n\n" + output[-2000:]

            return f"Execution Result:\n```text\n{output}\n```"
        except subprocess.TimeoutExpired:
            return "Execution Error: Script timed out after 120 seconds."
        except Exception as e:
            return f"Execution Error: {str(e)}"


