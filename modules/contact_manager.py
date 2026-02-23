import subprocess
import re
import json
import os
import config

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