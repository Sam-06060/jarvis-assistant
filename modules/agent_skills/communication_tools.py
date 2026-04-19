import re
import logging
from .base import AgentTool

logger = logging.getLogger(__name__)

class EmailTool(AgentTool):
    name = "send_email"
    description = "Send an email. Input: {'recipient': str, 'subject': str, 'body': str}. Requires confirmation."
    tier = 2
    permission = "destructive"

    def run(self, inp: dict):
        email_mgr = self.cp.registry.get("email")
        if not email_mgr: return "Email manager unavailable."
        
        recipient = inp.get('recipient', '').lower()
        # PRIORITY RECIPIENTS: Force configured email if it's 'me' or variants
        self_pattern = re.compile(r"^(me|myself|user|your|samson.*)$")
        if self_pattern.match(recipient) or not recipient or "@" not in recipient:
            from config import USER_EMAIL
            recipient = USER_EMAIL
        
        success = email_mgr.send_email(recipient, inp.get('subject', ''), inp.get('body', ''))
        status = str(success)
        is_sent = "sent to" in status.lower() and "failed" not in status.lower()
        return status if is_sent else f"Failed to send email: {status}"

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
