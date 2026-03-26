import subprocess
import re
import json
import os
import config
import urllib.parse

class ContactManager:

    NAME_ALIASES = {
        "samsung": "samson",
        "sam sung": "samson",
        "sam song": "samson",
        "sam san": "samson",
        # add more if needed
    }

    def __init__(self):
        # Initialize the JSON "Black Book" for emails
        self.contacts_file = config.CONTACTS_FILE
        self.email_db = {}
        self.load_email_db()

    # -------------------------
    # 📚 BLACK BOOK (JSON)
    # -------------------------
    
    def load_email_db(self):
        """Load custom email contacts from JSON"""
        try:
            if os.path.exists(self.contacts_file):
                with open(self.contacts_file, 'r') as f:
                    self.email_db = json.load(f)
            else:
                self.email_db = {}
        except Exception as e:
            print(f"⚠️ Error loading contact DB: {e}")
            self.email_db = {}

    def save_email_db(self):
        """Save custom email contacts to JSON"""
        try:
            os.makedirs(os.path.dirname(self.contacts_file), exist_ok=True)
            with open(self.contacts_file, 'w') as f:
                json.dump(self.email_db, f, indent=4)
        except Exception as e:
            print(f"⚠️ Error saving contact DB: {e}")

    def add_email_contact(self, name, email):
        """Add a new contact to the JSON database"""
        clean_name = self.clean_name(name).lower()
        # Clean up spoken email (e.g., "sam at gmail dot com" -> "sam@gmail.com")
        clean_email = email.lower().replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
        
        self.email_db[clean_name] = clean_email
        self.save_email_db()
        return f"Saved {name} to the Black Book with email {clean_email}."

    def get_email(self, name):
        """Retrieve email from JSON database"""
        clean_name = self.clean_name(name).lower()
        return self.email_db.get(clean_name)

    # -------------------------
    # 🛠 NORMALIZATION HELPERS
    # -------------------------

    def apply_name_aliases(self, name):
        """Fix common speech recognition mistakes"""
        name_lower = name.lower().strip()
        if name_lower in self.NAME_ALIASES:
            return self.NAME_ALIASES[name_lower]
        return name

    def clean_name(self, name):
        """Clean and normalize contact name"""
        name = name.lower()
        name = re.sub(r"[.,!?]", "", name)
        name = re.sub(r"\s+", " ", name).strip()
        name = self.apply_name_aliases(name)
        return name.title()

    # -------------------------
    # 🔍 SEARCH (macOS + JSON)
    # -------------------------

    def search_contact(self, name):
        """Search both JSON Black Book and macOS Contacts"""
        name_clean = self.clean_name(name)
        results = []

        # 1. Check JSON Email Book
        email = self.get_email(name)
        if email:
            results.append(f"• {name_clean} (Black Book)\n  Email: {email}")

        # 2. Check macOS Contacts (AppleScript)
        try:
            script = f'''
            tell application "Contacts"
                set matchingPeople to (every person whose name contains "{name_clean}")
                set contactInfo to ""
                repeat with aPerson in matchingPeople
                    set personName to name of aPerson
                    set phoneList to ""
                    try
                        set allPhones to phones of aPerson
                        repeat with aPhone in allPhones
                            set phoneList to phoneList & (value of aPhone) & ", "
                        end repeat
                    end try
                    set contactInfo to contactInfo & personName & "|" & phoneList & "||"
                end repeat
                return contactInfo
            end tell
            '''
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                mac_contacts = self._parse_contact_info(result.stdout.strip())
                results.append(mac_contacts)
        except Exception:
            pass

        if results:
            return "Found:\n" + "\n".join(results)
        return f"No contacts found for '{name_clean}'."

    def _parse_contact_info(self, contact_string):
        """Parse AppleScript contact output"""
        contacts = contact_string.split("||")
        formatted = []
        for contact in contacts:
            if contact.strip():
                parts = contact.split("|")
                name = parts[0]
                phones = parts[1].rstrip(", ") if len(parts) > 1 else "No phone"
                formatted.append(f"• {name} (Mac Contacts)\n  Phone: {phones}")
        return "\n".join(formatted)

    # -------------------------
    # 📞 CALL CONTACT (macOS)
    # -------------------------

    def call_contact(self, name):
        """Initiate FaceTime audio call"""
        try:
            name = self.clean_name(name)
            script = f'''
            tell application "Contacts"
                set matchingPeople to (every person whose name contains "{name}")
                if (count of matchingPeople) > 0 then
                    set firstPerson to item 1 of matchingPeople
                    set phoneList to phones of firstPerson
                    if (count of phoneList) > 0 then
                        return value of item 1 of phoneList
                    end if
                end if
                return ""
            end tell
            '''
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)

            if result.returncode == 0 and result.stdout.strip():
                phone = result.stdout.strip()
                # Clean phone string for URL
                phone_clean = re.sub(r"[^0-9+]", "", phone)
                subprocess.run(["open", f"facetime-audio://{phone_clean}"], check=False)
                return f"Calling {name}..."

            return f"Could not find phone number for {name}."
        except Exception as e:
            return f"Error initiating call: {str(e)}"

    # -------------------------
    # 💬 MESSAGE CONTACT (macOS)
    # -------------------------

    def message_contact(self, name, message=None):
        """Send message via Messages.app"""
        try:
            name = self.clean_name(name)
            script = f'''
            tell application "Contacts"
                set matchingPeople to (every person whose name contains "{name}")
                if (count of matchingPeople) > 0 then
                    set firstPerson to item 1 of matchingPeople
                    set phoneList to phones of firstPerson
                    if (count of phoneList) > 0 then
                        return value of item 1 of phoneList
                    end if
                end if
                return ""
            end tell
            '''
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)

            if result.returncode != 0 or not result.stdout.strip():
                return f"Could not find contact {name}."

            phone = result.stdout.strip()

            if message:
                # Escape quotes in message
                message = message.replace('"', '\\"')
                msg_script = f'''
                tell application "Messages"
                    set targetService to 1st service whose service type = iMessage
                    set targetBuddy to buddy "{phone}" of targetService
                    send "{message}" to targetBuddy
                end tell
                '''
                subprocess.run(["osascript", "-e", msg_script], check=False)
                return f"Message sent to {name}."
            else:
                subprocess.run(["open", f"sms:{phone}"], check=False)
                return f"Opening Messages with {name}."

        except Exception as e:
            return f"Error opening Messages: {str(e)}"

    # -------------------------
    # 🟢 WHATSAPP (macOS)
    # -------------------------

    def format_whatsapp_number(self, raw_number):
        """Format a macOS Contacts phone number for WhatsApp URL (pure digits with country code)"""
        # Remove all non-numeric characters except +
        clean_number = re.sub(r"[^0-9+]", "", raw_number)
        
        # If it already starts with +, just strip the + and keep the rest
        if clean_number.startswith("+"):
            return clean_number[1:]
            
        # If it doesn't start with +, but has 10 digits (India standard), prepend 91
        if len(clean_number) == 10:
            return f"91{clean_number}"
            
        # Otherwise, just return what we stripped (assuming it might be local or already include country code)
        return clean_number

    def _get_all_mac_contacts(self):
        """Fetch all names from macOS contacts for the LLM to search through"""
        script = '''
        tell application "Contacts"
            set contactNames to name of every person
            set AppleScript's text item delimiters to ", "
            return contactNames as text
        end tell
        '''
        try:
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().split(", ")
        except Exception:
            pass
        return []
            
    def _smart_resolve_name(self, requested_name):
        """Use LLM to find the best matching name in macOS contacts"""
        all_contacts = self._get_all_mac_contacts()
        if not all_contacts:
            return requested_name # Fallback
            
        # Optional: We can hook this to Groq or local Ollama. For safety and speed in ContactManager, 
        # we'll do a basic text-based fuzzy match first, and if we have access to the app context's LLM, use it.
        # Since ContactManager is a standalone module, we'll use `difflib` for fast, offline semantic fuzzy matching,
        # which is extremely reliable for "Maa" -> "Mummy" if aliases are set, or slight misspellings.
        import difflib
        
        # 1. Check exact aliases first
        clean_req = self.clean_name(requested_name).lower()
        if clean_req in self.NAME_ALIASES:
            return self.NAME_ALIASES[clean_req]
            
        # 2. Fuzzy match against the address book
        matches = difflib.get_close_matches(requested_name, all_contacts, n=1, cutoff=0.6)
        if matches:
            return matches[0]
            
        return requested_name

    def get_whatsapp_contact_info(self, name):
        """Resolves contact name and retrieves their phone number for WhatsApp."""
        try:
            resolved_name = self._smart_resolve_name(name)
            resolved_name_clean = resolved_name.strip(' "\'')

            script = f'''
            tell application "Contacts"
                set matchingPeople to (every person whose name contains "{resolved_name_clean}")
                if (count of matchingPeople) > 0 then
                    set firstPerson to item 1 of matchingPeople
                    set phoneList to phones of firstPerson
                    if (count of phoneList) > 0 then
                        return value of item 1 of phoneList
                    end if
                end if
                return ""
            end tell
            '''
            
            script_wrapper = f"ignoring case\\n{script}\\nend ignoring"
            result = subprocess.run(["osascript", "-e", script_wrapper], capture_output=True, text=True, timeout=5)

            if result.returncode != 0 or not result.stdout.strip():
                result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=5)
                if result.returncode != 0 or not result.stdout.strip():
                    return None, resolved_name_clean

            raw_phone = result.stdout.strip()
            formatted_phone = self.format_whatsapp_number(raw_phone)
            
            if not formatted_phone:
                return None, resolved_name_clean
                
            return formatted_phone, resolved_name_clean
            
        except Exception as e:
            return None, str(e)

    def send_whatsapp_message(self, name, message=None, pre_formatted_phone=None):
        """Open WhatsApp Desktop chat via Apple Shortcuts with optional pre-filled message"""
        try:
            if pre_formatted_phone:
                formatted_phone = pre_formatted_phone
                resolved_name = name
            else:
                formatted_phone, resolved_name = self.get_whatsapp_contact_info(name)
                
            if not formatted_phone:
                return f"Could not find a valid number for {resolved_name}."


            


            if message:
                # Apple Shortcuts requires E.164 format (+CountryCodeNumber)
                shortcuts_phone = f"+{formatted_phone}" if not formatted_phone.startswith("+") else formatted_phone
                
                # Escape potential delimiter in the message
                safe_message = message.replace("|", " ")
                shortcut_input = f"{shortcuts_phone}|{safe_message}"
                
                # Use stdin (input=) instead of -i to support large multiline content (essays)
                subprocess.run(["shortcuts", "run", "JarvisWhatsApp"], input=shortcut_input, text=True, check=False)
                return f"Message sent to {resolved_name}."
            else:
                url = f"whatsapp://send?phone={formatted_phone}"
                subprocess.run(["open", url], check=False)
                return f"Opening WhatsApp with {resolved_name}."

        except Exception as e:
            return f"Error triggering WhatsApp Shortcut: {str(e)}"