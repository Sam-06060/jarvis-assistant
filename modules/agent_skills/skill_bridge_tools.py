"""
skill_bridge_tools.py — AgentTool wrappers for existing Command Skills.

These thin wrappers give the agentic loop access to capabilities that
previously existed only in the command-processing skill system
(modules/skills/) but were invisible to the agent (modules/agent_skills/).

The two systems are now unified through this bridge.
Auto-discovered by SkillRegistrar on startup — no manual registration needed.
"""

import re
import logging
from .base import AgentTool

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# COMMUNICATION
# ─────────────────────────────────────────────────────────────────────────────

class SendMessageTool(AgentTool):
    name = "send_message"
    description = (
        "Send a message to a contact. For WhatsApp use 'send_whatsapp' tool instead — it is more reliable. "
        "Use this only for iMessage. Input: {'contact': str, 'message': str, 'platform': 'whatsapp'|'imessage'}."
    )
    tier = 2  # Requires user confirmation before sending
    permission = "destructive"

    def run(self, inp: dict) -> str:
        contact = inp.get("contact", "").strip()
        message = inp.get("message", "").strip()
        platform = inp.get("platform", "whatsapp").lower()

        if not contact:
            return "Error: 'contact' is required."
        if not message:
            return "Error: 'message' is required."

        # ── WhatsApp: bypass CommunicationSkill and call the shortcut directly ──
        # CommunicationSkill.handle() returns None for WhatsApp and never fires
        # the Apple Shortcut. contacts.send_whatsapp_message() is the correct path.
        if platform == "whatsapp":
            contacts = self.cp.registry.get("contacts")
            if not contacts:
                return "Error: Contact manager is not loaded."
            try:
                result = contacts.send_whatsapp_message(contact, message)
                return result if result else f"✅ WhatsApp message sent to {contact}."
            except Exception as e:
                logger.error(f"SendMessageTool (WhatsApp) error: {e}")
                return f"Error sending WhatsApp to {contact}: {str(e)}"

        # ── iMessage / other: call contact manager directly (bypass CommunicationSkill) ──
        contacts = self.cp.registry.get("contacts")
        if not contacts:
            return "Error: Contact manager is not loaded."
        
        try:
            # We use message_contact which handles platform selection
            result = contacts.message_contact(contact, message)
            return result if result else f"✅ Message sent to {contact} via {platform}."
        except Exception as e:
            logger.error(f"SendMessageTool error: {e}")
            return f"Error sending message to {contact}: {str(e)}"


class SendEmailTool(AgentTool):
    name = "send_email"
    description = (
        "Send an email to a recipient. "
        "Input: {'to': str (email address OR contact name OR 'me'), 'subject': str, 'body': str}. "
        "Use 'me' or 'myself' to email the user. Use a contact name for anyone in the address book."
    )
    tier = 2  # Requires user confirmation
    permission = "destructive"

    # Self-reference patterns — all resolve to USER_EMAIL
    _SELF_REFS = re.compile(
        r"^(me|myself|my email|the user|samson frank ganta|samson ganta|samson)$",
        re.IGNORECASE,
    )

    def run(self, inp: dict) -> str:
        # Accept both 'to' and 'recipient' keys (backward compat)
        to = (inp.get("to") or inp.get("recipient") or "").strip()
        subject = inp.get("subject", "(No Subject)").strip()
        body = inp.get("body", "").strip()

        if not to:
            return "Error: 'to' (recipient) is required."

        email_mgr = self.cp.registry.get("email")
        contacts = self.cp.registry.get("contacts")
        if not email_mgr:
            return "Error: Email manager is not loaded."

        # ── 1. Self-reference priority — always wins ──────────────────────
        if self._SELF_REFS.match(to) or "@" not in to and self._is_self_ref(to):
            import config as _cfg
            to_address = getattr(_cfg, "USER_EMAIL", "")
            if not to_address:
                return "Error: USER_EMAIL is not configured. Please set it in your .env file."
            logger.info(f"📧 Self-reference '{to}' → {to_address}")

        # ── 2. Already a valid email ──────────────────────────────────────
        elif "@" in to:
            to_address = to

        # ── 3. Name-based contact lookup ─────────────────────────────────
        elif contacts:
            resolved = contacts.get_email(to)
            if resolved:
                to_address = resolved
                logger.info(f"📧 Resolved contact '{to}' → {to_address}")
            else:
                # Last resort: try USER_EMAIL if name loosely matches user
                import config as _cfg
                to_address = getattr(_cfg, "USER_EMAIL", "")
                if not to_address:
                    return f"Error: No email found for '{to}' and USER_EMAIL is not configured."
                logger.warning(f"📧 No contact match for '{to}', falling back to USER_EMAIL: {to_address}")
        else:
            import config as _cfg
            to_address = getattr(_cfg, "USER_EMAIL", "")
            if not to_address:
                return f"Error: Contact manager unavailable and '{to}' is not a valid email."

        try:
            result = email_mgr.send_email(to_address=to_address, subject=subject, body=body)
            return f"✅ Email sent to {to_address}." if "sent to" in result.lower() else result
        except Exception as e:
            logger.error(f"SendEmailTool error: {e}")
            return f"Error sending email: {str(e)}"

    def _is_self_ref(self, text: str) -> bool:
        """Check if text loosely refers to the current user."""
        t = text.lower().strip()
        return any(w in t for w in ("samson", "sam", "user", "my email", "myself"))


# ─────────────────────────────────────────────────────────────────────────────
# MUSIC / MEDIA
# ─────────────────────────────────────────────────────────────────────────────

class MusicControlTool(AgentTool):
    name = "control_music"
    description = (
        "Control music playback. "
        "Input: {'action': 'play'|'pause'|'resume'|'stop'|'skip'|'previous'|'shuffle', "
        "'song': str (optional, for play action), 'app': str (optional, default 'Spotify')}. "
        "Example: {'action': 'play', 'song': 'Blinding Lights'}"
    )
    permission = "write"

    def run(self, inp: dict) -> str:
        action = inp.get("action", "play").lower()
        song = inp.get("song", "").strip()

        skill = self.cp._find_skill("MusicSkill")
        if not skill:
            return "Error: MusicSkill is not loaded."

        cmd = f"play {song}" if action == "play" and song else action
        try:
            result = skill.handle(cmd)
            if result:
                verb = f"Playing '{song}'" if song else action.capitalize() + "d"
                return f"✅ {verb}."
            return f"⚠️ MusicSkill handled '{cmd}' but returned no confirmation."
        except Exception as e:
            logger.error(f"MusicControlTool error: {e}")
            return f"Error controlling music: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# FOCUS / DO NOT DISTURB
# ─────────────────────────────────────────────────────────────────────────────

class FocusModeTool(AgentTool):
    name = "focus_mode"
    description = (
        "Enable or disable Focus / Do Not Disturb mode. "
        "Input: {'action': 'enable'|'disable'}."
    )
    permission = "write"

    def run(self, inp: dict) -> str:
        action = inp.get("action", "enable").lower()
        skill = self.cp._find_skill("FocusSkill")
        if not skill:
            return "Error: FocusSkill is not loaded."

        cmd = "focus mode on" if action == "enable" else "focus mode off"
        try:
            result = skill.handle(cmd)
            state = "enabled" if action == "enable" else "disabled"
            return f"✅ Focus mode {state}." if result else f"⚠️ FocusSkill returned no confirmation."
        except Exception as e:
            logger.error(f"FocusModeTool error: {e}")
            return f"Error setting focus mode: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# CALENDAR
# ─────────────────────────────────────────────────────────────────────────────

class CalendarTool(AgentTool):
    name = "manage_calendar"
    description = (
        "Add or list calendar events. "
        "Input: {'action': 'add'|'list', 'title': str, 'date': str, 'time': str (optional)}. "
        "Example: {'action': 'add', 'title': 'Doctor appointment', 'date': 'tomorrow', 'time': '3pm'}"
    )
    permission = "write"

    def run(self, inp: dict) -> str:
        action = inp.get("action", "list").lower()
        calendar = self.cp.registry.get("calendar")
        if not calendar:
            return "Error: Calendar manager is not loaded."

        try:
            if action == "list":
                result = calendar.get_events() if hasattr(calendar, "get_events") else "Calendar listing not available."
                return str(result)
            elif action == "add":
                title = inp.get("title", "")
                date = inp.get("date", "")
                t = inp.get("time", "")
                if hasattr(calendar, "add_event"):
                    result = calendar.add_event(title=title, date=date, time=t)
                    return f"✅ Event '{title}' added to calendar." if result else "⚠️ Failed to add event."
                return "Calendar 'add_event' method not available."
            return f"Unknown calendar action: '{action}'."
        except Exception as e:
            logger.error(f"CalendarTool error: {e}")
            return f"Error with calendar: {str(e)}"


# ─────────────────────────────────────────────────────────────────────────────
# SHORTCUTS
# ─────────────────────────────────────────────────────────────────────────────

class RunShortcutTool(AgentTool):
    name = "run_shortcut"
    description = (
        "Run a saved Jarvis macro or Apple Shortcut by name. "
        "Input: {'name': str}. "
        "Example: {'name': 'morning routine'}"
    )
    permission = "write"

    def run(self, inp: dict) -> str:
        name = inp.get("name", "").strip()
        if not name:
            return "Error: 'name' of the shortcut/macro is required."

        skill = self.cp._find_skill("ShortcutsSkill")
        if not skill:
            return "Error: ShortcutsSkill is not loaded."

        try:
            result = skill.handle(f"run {name}")
            return f"✅ Shortcut '{name}' executed." if result else f"⚠️ Shortcut '{name}' returned no confirmation."
        except Exception as e:
            logger.error(f"RunShortcutTool error: {e}")
            return f"Error running shortcut '{name}': {str(e)}"
