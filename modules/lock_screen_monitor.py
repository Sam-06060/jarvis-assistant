"""
modules/lock_screen_monitor.py
──────────────────────────────────────────────────────────────────────────────
macOS Lock Screen Monitor for Jarvis.

Security: Jarvis is completely deaf and mute when the Mac screen is locked.
  - Mic input is paused (speech engine stops listening)
  - Socket/typed commands are rejected with no response
  - Jarvis resumes the moment you unlock

How it works:
  Polls CGSessionCopyCurrentDictionary() every second.
  This is the same Quartz API macOS itself uses to determine lock state.
  No browser/UI/notification required — works even in the dark.

Usage:
    from modules.lock_screen_monitor import LockScreenMonitor, is_screen_locked
    monitor = LockScreenMonitor(registry=ServiceRegistry)
    monitor.start()
"""

import threading
import time
import logging

logger = logging.getLogger("jarvis")

# ── Global lock state (fast read, no import needed in hot paths) ──────────────
_SCREEN_LOCKED = False


def is_screen_locked() -> bool:
    """
    Fast, zero-import check for lock state.
    Call this from any hot path (command processor, socket server).
    """
    return _SCREEN_LOCKED


class LockScreenMonitor:
    """
    Monitors macOS screen lock state and pauses/resumes Jarvis accordingly.

    When locked:
      - SpeechEngine.force_stop() is called → mic goes silent
      - Global _SCREEN_LOCKED flag is set → process() rejects commands

    When unlocked:
      - SpeechEngine.start_listening() is called → mic resumes
      - Global _SCREEN_LOCKED flag is cleared
    """

    POLL_INTERVAL = 1.0  # seconds between lock state checks

    def __init__(self, registry=None):
        self._registry = registry
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._was_locked = False  # Previous poll state

    def start(self):
        """Start the lock screen monitor in a daemon thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="LockScreenMonitor",
        )
        self._thread.start()
        logger.info("🔐 [LockMonitor] Lock screen guard active.")

    def stop(self):
        """Stop the monitor."""
        self._stop_event.set()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _check_locked(self) -> bool:
        """
        Check macOS screen lock state via Quartz.
        Returns True if the screen is locked (login window showing).
        """
        try:
            from Quartz import CGSessionCopyCurrentDictionary
            session = CGSessionCopyCurrentDictionary()
            if session is None:
                return False
            return bool(session.get("CGSSessionScreenIsLocked", False))
        except Exception:
            # If Quartz is unavailable (rare), don't block Jarvis
            return False

    def _on_locked(self):
        """Called once when the screen transitions to locked."""
        global _SCREEN_LOCKED
        _SCREEN_LOCKED = True
        logger.info("🔒 [LockMonitor] Screen locked — Jarvis is now deaf.")

        if not self._registry:
            return

        try:
            speech = self._registry.get("speech")
            if speech and hasattr(speech, "lock"):
                speech.lock()
                logger.info("🔇 [LockMonitor] Microphone + wake word fully disabled.")
            elif speech and hasattr(speech, "force_stop"):
                # Fallback for older versions
                speech.force_stop()
        except Exception as e:
            logger.debug(f"[LockMonitor] lock() failed: {e}")

    def _on_unlocked(self):
        """Called once when the screen transitions to unlocked."""
        global _SCREEN_LOCKED
        _SCREEN_LOCKED = False
        logger.info("🔓 [LockMonitor] Screen unlocked — Jarvis is listening again.")

        if not self._registry:
            return

        try:
            speech = self._registry.get("speech")
            if speech and hasattr(speech, "unlock"):
                # Small delay so macOS can fully restore audio session
                time.sleep(0.5)
                speech.unlock()
                logger.info("🎤 [LockMonitor] Microphone + wake word restored.")
            elif speech and hasattr(speech, "start_listening"):
                # Fallback for older versions
                time.sleep(0.5)
                speech.start_listening()
        except Exception as e:
            logger.debug(f"[LockMonitor] unlock() failed: {e}")

    def _monitor_loop(self):
        """Main polling loop — runs every POLL_INTERVAL seconds."""
        while not self._stop_event.is_set():
            try:
                locked = self._check_locked()

                if locked and not self._was_locked:
                    self._on_locked()
                elif not locked and self._was_locked:
                    self._on_unlocked()

                self._was_locked = locked
            except Exception as e:
                logger.debug(f"[LockMonitor] Poll error: {e}")

            self._stop_event.wait(self.POLL_INTERVAL)
