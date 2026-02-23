from .base import Skill
import re
import string

class CommunicationSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        triggers = ["email", "mail", "call", "message", "text", "contact"]
        return any(t in cmd for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        contacts = self.app.get('contacts') # ContactManager
        email_manager = self.app.get('email_manager') # EmailManager
        # Note: In CommandProcessor, it was `self.email`. In app_context, I need to check what key I used.
        # Looking at previous step, I haven't added `email` or `contacts` to app_context yet!
        # I will need to update CommandProcessor to pass them.
        
        # --- CONTACTS (Add/Find) ---
        if contacts:
            if "save contact" in cmd or "add contact" in cmd:
                self.speech.speak("What is the person's name?")
                name = self.speech.listen_command(duration=3)
                if not name:
                    self.speech.speak("I didn't hear a name. Cancelling.")
                    return True
                
                name = name.strip(string.punctuation).strip()
                self.speech.speak(f"Okay, what is the email address for {name}?")
                
                addr = self.speech.listen_command(duration=8)
                if not addr:
                    self.speech.speak("I didn't hear an email. Cancelling.")
                    return True
                
                addr = addr.strip(string.punctuation).strip()
                result = contacts.add_email_contact(name, addr)
                self.speech.speak(result)
                return True

            if "find contact" in cmd or "search contact" in cmd:
                name = cmd.replace("find contact", "").replace("search contact", "").strip()
                if name:
                    self.speech.speak(contacts.search_contact(name))
                    return True
                    
            if "call" in cmd:
                name = cmd.replace("call", "").strip()
                if name and len(name) < 50:
                    self.speech.speak(contacts.call_contact(name))
                    return True
            
            if "message" in cmd or "text" in cmd:
                # Avoid capturing "text input" logic if confusing, but usually OK.
                name = cmd.replace("message", "").replace("text", "").strip()
                if name and len(name) < 50:
                     self.speech.speak(contacts.message_contact(name))
                     return True

        # --- EMAIL ---
        if email_manager:
            # CHECK
            if "check email" in cmd or "check mail" in cmd or "unread emails" in cmd:
                self.speech.speak(email_manager.get_unread_count())
                return True
            if "recent emails" in cmd:
                self.speech.speak(email_manager.get_recent_emails())
                return True

            # SEND
            if "send" in cmd and ("email" in cmd or "mail" in cmd):
                if " to " in cmd and " saying " in cmd:
                    try:
                        # Parsing: "send email to [Name] saying [Body]"
                        parts = cmd.split(" to ", 1)[1]
                        recipient_raw, body = parts.split(" saying ", 1)
                        body = body.strip()
                        subject = "Message from Jarvis"
                        
                        recipient_name = recipient_raw.strip()
                        
                        # Lookup
                        to_address = None
                        if contacts:
                            to_address = contacts.get_email(recipient_name)

                        # Fallback parsing
                        if not to_address:
                            if " at " in recipient_name or "@" in recipient_name:
                                to_address = recipient_name.replace(" at ", "@").replace(" ", "")
                            else:
                                self.speech.speak(f"I don't have an email for {recipient_name}.")
                                return True
                        
                        self.speech.speak(f"Sending email to {recipient_name}.")
                        result = email_manager.send_email(to_address, subject, body)
                        self.speech.speak("Email sent." if "sent to" in result else result)
                        return True

                    except Exception as e:
                        self.logger.error(f"Email Error: {e}")
                        self.speech.speak("I couldn't understand the email command.")
                        return True
                else:
                    self.speech.speak("Please say: send email to Name saying Message")
                    return True
                    
        return False
