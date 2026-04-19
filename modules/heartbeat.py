"""
heartbeat.py — Real-time Contextual Status Emitter for Jarvis Agentic Operations

Streams labeled heartbeat events to the Swift UI (via socket_server) during agentic
operations. Each heartbeat carries a label (e.g. "Running script..."), a status
(active → shimmer, success → ✅, failed → ❌), and a step index so the UI can
render a live progress stack.

Protocol:
  Python → SocketServer.broadcast_heartbeat(label, status, step_index)
  → Swift SocketClient parses {"type": "heartbeat", ...}
  → ContentView renders HeartbeatStackView

This module is used exclusively by AgentCore; it does NOT touch the HUD queue.
"""

import json
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class HeartbeatEmitter:
    """Streams contextual status updates to the Swift UI during agentic operations."""

    # UI Slot Definitions
    HEADER = 0  # index 0: Mode/System Header (e.g. "🤖 Entering Agentic Mode")
    STEP = 1    # index 1: Major Plan Step (e.g. "Step 1/3: Gathering Data")
    ACTION = 2  # index 2: Live Action Detail (e.g. "🛠️ Searching...")

    def __init__(self, hud_queue, socket_server=None):
        self._hud = hud_queue
        self._socket = socket_server
        self._last_emit_time: float = 0.0
        self._active_step: Optional[str] = None
        self._step_index: int = 0
        self._total_steps: int = 0

    def set_total_steps(self, total: int):
        """Set the total number of planned steps for progress display."""
        self._total_steps = total

    def emit(self, label: str, status: str = "active", index: Optional[int] = None):
        """
        Emit a heartbeat event to a specific UI slot.

        Args:
            label:  Human-readable status line
            status: One of 'active' (shimmer), 'success' (✅), 'failed' (❌)
            index:  Specific slot index (0, 1, or 2). Defaults to internal _step_index.
        """
        self._last_emit_time = time.time()
        slot = index if index is not None else self._step_index

        # 1. Update the terminal HUD (Original terminal feedback remains unchanged as requested)
        if self._hud:
            try:
                self._hud.put(("PROCESSING", f"💓 {label}"))
            except Exception:
                pass

        # 2. Broadcast structured heartbeat to Swift UI
        if self._socket:
            try:
                msg = json.dumps({
                    "type": "heartbeat",
                    "label": label,
                    "status": status,
                    "step_index": slot,
                    "total_steps": self._total_steps if slot == self.STEP else 0,
                }) + "\n"
                with self._socket.lock:
                    disconnected = []
                    for client in self._socket.clients:
                        try:
                            client.sendall(msg.encode("utf-8"))
                        except Exception:
                            disconnected.append(client)
                    for d in disconnected:
                        if d in self._socket.clients:
                            self._socket.clients.remove(d)
            except Exception as e:
                logger.debug(f"Heartbeat broadcast failed: {e}")

    def header(self, label: str, status: str = "active"):
        """Update the Header slot (index 0)."""
        self.emit(label, status, index=self.HEADER)

    def step_start(self, label: str, step_index: Optional[int] = None):
        """Start a major plan step (index 1)."""
        if step_index is not None:
            self._step_index = step_index
        self._active_step = label
        self.emit(label, "active", index=self.STEP)
        logger.info(f"💓 HEARTBEAT (STEP): {label}")

    def step_complete(self, label: str, success: bool):
        """Complete a major plan step (index 1)."""
        status = "success" if success else "failed"
        self.emit(label, status, index=self.STEP)
        self._active_step = None
        icon = "✅" if success else "❌"
        logger.info(f"💓 HEARTBEAT (STEP DONE): {icon} {label}")

    def action(self, label: str, status: str = "active"):
        """Update the Live Action slot (index 2)."""
        self.emit(label, status, index=self.ACTION)
        # We don't log actions to terminal unless they are significant to avoid spam

    def thinking(self, context: str = "Reasoning about next step..."):
        """Update Action slot with thinking status."""
        self.emit(context, "thinking", index=self.ACTION)

    def ensure_alive(self, max_silence_seconds: float = 3.0):
        """Pulse the Action slot if silent for too long."""
        if time.time() - self._last_emit_time > max_silence_seconds:
            self.action("Still working...", "active")

    def clear(self):
        """Clear all heartbeat slots in the UI."""
        if self._socket:
            try:
                msg = json.dumps({
                    "type": "heartbeat",
                    "label": "",
                    "status": "clear",
                    "step_index": 0,
                    "total_steps": 0,
                }) + "\n"
                with self._socket.lock:
                    for client in self._socket.clients:
                        try:
                            client.sendall(msg.encode("utf-8"))
                        except Exception:
                            pass
            except Exception:
                pass
