from .base import Skill
import re
import string

class CommunicationSkill(Skill):
    def can_handle(self, command: str) -> bool:
        cmd = command.lower()
        triggers = ["email", "mail", "call", "message", "text", "contact", "whatsapp"]
        return any(t in cmd for t in triggers)

    # ─────────────────────────────────────────────
    # NLP ENTITY EXTRACTOR
    # Handles all natural-language variants for:
    #   "message X saying Y", "send X a whatsapp message to Y",
    #   "tell X that Y", "whatsapp X asking Y", etc.
    # ─────────────────────────────────────────────
    def _parse_message_intent(self, raw_cmd: str):
        """
        Returns (name, body, is_whatsapp) from any natural language messaging command.
        body may be None if no message content was found.
        """
        cmd = raw_cmd.lower().strip()

        # Step 1: Detect WhatsApp intent anywhere in the sentence
        is_whatsapp = bool(re.search(r"\bwhatsapp\b", cmd))

        # Step 2: Strip interjections that never carry meaning
        cmd = re.sub(r"\b(?:please|just|quickly|now|immediately)\b", "", cmd)
        cmd = re.sub(r"\s+", " ", cmd).strip()

        # Step 3: Normalize "on whatsapp" / "via whatsapp" anywhere so it doesn't pollute name extraction
        cmd = re.sub(r"\s*(?:on|via|through|using|in)\s+whatsapp\b", " ", cmd)
        cmd = re.sub(r"\bwhatsapp\s+", " ", cmd)
        cmd = re.sub(r"\s+", " ", cmd).strip()

        # Step 4: Body connector keywords (things that come before the message body)
        bc = r"(?:saying\s+that|saying|says|to say|that|asking|to ask|to tell|to inform|to write|with the message|with message)"

        # Step 5: Prioritized patterns (most-specific → least-specific)
        # Format: (regex_pattern, name_group, body_group_or_None)
        patterns = [
            # "send [name] a message saying [body]"
            (rf"^send\s+(.+?)\s+a\s+message\s+{bc}\s+(.+)$", 1, 2),

            # "send a message to [name] saying [body]"
            (rf"^send\s+a\s+message\s+to\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # "send message to [name] saying [body]"
            (rf"^send\s+message\s+to\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # "send [name] saying [body]"
            (rf"^send\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # "message/text [name] saying [body]"
            (rf"^(?:message|text)\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # "tell [name] that [body]"
            (rf"^tell\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # "ask [name] saying/that [body]"
            (rf"^ask\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # Fallback with body: "[action] to [name] [bc] [body]"
            (rf"^.+?\s+to\s+(.+?)\s+{bc}\s+(.+)$", 1, 2),

            # Generic last-resort: "[name] saying/asking [body]"
            # Must NOT start with a known action verb (already handled above)
            (rf"^(?!(?:send|message|text|tell|ask|call|find|search)\b)([a-z][a-z\s]{{1,40}}?)\s+{bc}\s+(.+)$", 1, 2),

            # No-body patterns (name-only extraction)
            (r"^(?:message|text)\s+(.+)$", 1, None),
            (r"^send\s+(?:a\s+)?message\s+to\s+(.+)$", 1, None),
            (r"^send\s+(.+?)\s+a\s+message$", 1, None),
            (r"^tell\s+(.+)$", 1, None),
            (r"^ask\s+(.+)$", 1, None),
        ]

        name = None
        body = None

        for pattern, name_idx, body_idx in patterns:
            m = re.search(pattern, cmd, re.IGNORECASE)
            if m:
                name = m.group(name_idx).strip()
                if body_idx is not None and body_idx <= len(m.groups()):
                    body = m.group(body_idx).strip()
                break

        # Step 6: Final name cleanup
        if name:
            name = re.sub(r"\b(?:a|an|the|on|via|through|using|in)\b", "", name)
            name = name.strip(string.punctuation).strip()
            name = ' '.join(name.split())
            if len(name) > 50:
                name = None

        return name, body, is_whatsapp

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        contacts = self.app.get('contacts')
        email_manager = self.app.get('email_manager')

        # --- CONTACTS: Add / Find ---
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
                self.speech.speak(contacts.add_email_contact(name, addr))
                return True

            if "find contact" in cmd or "search contact" in cmd:
                name = re.sub(r"\b(?:find|search)\s+contact\b", "", cmd).strip()
                if name:
                    self.speech.speak(contacts.search_contact(name))
                    return True

            if re.match(r"^call\b", cmd) or (
                "call" in cmd and "message" not in cmd and "email" not in cmd
            ):
                name = re.sub(r"\bcall\b", "", cmd).strip()
                if name and len(name) < 50:
                    self.speech.speak(contacts.call_contact(name))
                    return True

            # ─── MESSAGE / WHATSAPP (NLP) ───
            msg_triggers = ["message", "text", "send", "tell", "ask", "whatsapp"]
            if any(t in cmd for t in msg_triggers) and "email" not in cmd and "mail" not in cmd:
                name, body, is_whatsapp = self._parse_message_intent(cmd)

                if not name:
                    return False

                if body:
                    try:
                        if is_whatsapp:
                            phone, resolved_name = contacts.get_whatsapp_contact_info(name)
                            if not phone:
                                self.speech.speak(f"I couldn't find a valid WhatsApp number for {name}.")
                                return True

                            # Show preview in Jarvis chat UI
                            preview = f"WhatsApp Preview\nTo: {resolved_name}\nMessage: {body}"
                            if hasattr(self.speech, 'hud_queue') and self.speech.hud_queue:
                                self.speech.hud_queue.put(("JARVIS", preview))
                            else:
                                print(f"\n{preview}\n")

                            # Voice confirmation
                            self.speech.speak(f"I am ready to send this to {resolved_name}. Yes or no?")
                            auth = self.speech.listen_command()
                            confirm_words = [
                                "yes", "yeah", "yep", "send", "do it", "sure",
                                "ok", "okay", "send it", "please", "go ahead", "confirm"
                            ]
                            if auth and any(w in auth.lower() for w in confirm_words):
                                result = contacts.send_whatsapp_message(resolved_name, body, pre_formatted_phone=phone)
                                self.speech.speak(result)
                            else:
                                self.speech.speak("Message cancelled.")
                        else:
                            self.speech.speak(f"Sending text to {name}.")
                            self.speech.speak(contacts.message_contact(name, body))
                    except Exception as e:
                        print(f"DEBUG messaging error: {e}")
                        self.logger.error(f"Messaging Error: {e}")
                        self.speech.speak("I couldn't send the message. Please try again.")
                    return True
                else:
                    # No body – just open the chat
                    if is_whatsapp:
                        self.speech.speak(contacts.send_whatsapp_message(name))
                    else:
                        self.speech.speak(contacts.message_contact(name))
                    return True

        # --- EMAIL ---
        if email_manager:
            if "check email" in cmd or "check mail" in cmd or "unread emails" in cmd:
                self.speech.speak(email_manager.get_unread_count())
                return True
            if "recent emails" in cmd:
                self.speech.speak(email_manager.get_recent_emails())
                return True

            if "send" in cmd and ("email" in cmd or "mail" in cmd):
                if " to " in cmd and " saying " in cmd:
                    try:
                        parts = cmd.split(" to ", 1)[1]
                        recipient_raw, body = parts.split(" saying ", 1)
                        body = body.strip()
                        recipient_name = recipient_raw.strip()

                        to_address = None
                        if contacts:
                            to_address = contacts.get_email(recipient_name)

                        if not to_address:
                            if " at " in recipient_name or "@" in recipient_name:
                                to_address = recipient_name.replace(" at ", "@").replace(" ", "")
                            else:
                                self.speech.speak(f"I don't have an email for {recipient_name}.")
                                return True

                        self.speech.speak(f"Sending email to {recipient_name}.")
                        result = email_manager.send_email(to_address, "Message from Jarvis", body)
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
