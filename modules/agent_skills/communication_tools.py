import re
import logging
from .base import AgentTool

logger = logging.getLogger(__name__)

# NOTE: EmailTool is intentionally NOT defined here.
# The authoritative SendEmailTool lives in skill_bridge_tools.py and
# includes full contact resolution (name → email, "me" → USER_EMAIL).
# Having a duplicate here caused the weaker version to sometimes win
# registration, breaking "email me" / name-based recipient support.

class SearchContactTool(AgentTool):
    name = "search_contact"
    description = "Search for a contact's email or phone by name. Input: {'name': str}"
    permission = "safe"
    
    def run(self, inp: dict):
        contact_mgr = self.cp.registry.get("contacts")
        if not contact_mgr: return "Contact manager unavailable."
        return contact_mgr.search_contact(inp.get('name', ''))

class WhatsAppTool(AgentTool):
    name = "send_whatsapp"
    description = "Send a WhatsApp message. Input: {'name': str, 'message': str}. Requires confirmation."
    tier = 2
    permission = "destructive"

    def run(self, inp: dict):
        contacts = self.cp.registry.get("contacts")
        if not contacts: return "Contact manager unavailable."
        # Accept both 'name' and 'contact' keys — model sometimes uses either
        name = inp.get('name', '') or inp.get('contact', '')
        if not name:
            return "Error: 'name' (contact name) is required."
        return contacts.send_whatsapp_message(name, inp.get('message', ''))
