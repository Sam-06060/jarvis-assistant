import subprocess

class EmailManager:
    """Manage emails via Mail.app (macOS)"""
    
    def __init__(self):
        pass
    
    def get_unread_count(self):
        """Get count of unread emails"""
        try:
            script = '''
            tell application "Mail"
                set unreadCount to count of (messages of inbox whose read status is false)
                return unreadCount
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                count = int(result.stdout.strip())
                if count == 0:
                    return "No unread emails."
                elif count == 1:
                    return "You have 1 unread email."
                else:
                    return f"You have {count} unread emails."
            
            return "Could not check emails."
            
        except Exception as e:
            return f"Email check failed: {str(e)}"
    
    def get_recent_emails(self, count=5):
        """Get recent email subjects"""
        try:
            script = f'''
            tell application "Mail"
                set recentMessages to messages 1 thru {count} of inbox
                set emailList to ""
                repeat with msg in recentMessages
                    set emailInfo to (subject of msg) & "|" & (sender of msg) & "||"
                    set emailList to emailList & emailInfo
                end repeat
                return emailList
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return self._parse_email_list(result.stdout.strip())
            
            return "Could not fetch recent emails."
            
        except Exception as e:
            return f"Error fetching emails: {str(e)}"
    
    def _parse_email_list(self, email_string):
        """Parse email list from AppleScript output"""
        emails = email_string.split("||")
        formatted_emails = []
        
        for i, email in enumerate(emails, 1):
            if email.strip():
                parts = email.split("|")
                if len(parts) >= 2:
                    subject = parts[0]
                    sender = parts[1]
                    formatted_emails.append(f"{i}. From: {sender}\n   Subject: {subject}")
        
        if formatted_emails:
            return "Recent emails:\n" + "\n".join(formatted_emails)
        return "No emails found."
    
    def send_email(self, to_address, subject, body):
        """Send an email (requires Mail.app to be configured)"""
        try:
            # Escape quotes in strings
            subject = subject.replace('"', '\\"')
            body = body.replace('"', '\\"')
            
            script = f'''
            tell application "Mail"
                set newMessage to make new outgoing message with properties {{subject:"{subject}", content:"{body}"}}
                tell newMessage
                    make new to recipient at end of to recipients with properties {{address:"{to_address}"}}
                end tell
                send newMessage
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return f"Email sent to {to_address}"
            else:
                return f"Failed to send email: {result.stderr}"
                
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    def open_mail_app(self):
        """Open Mail application"""
        try:
            subprocess.Popen(["open", "-a", "Mail"])
            return "Opening Mail app."
        except Exception as e:
            return f"Could not open Mail: {str(e)}"
    
    def check_for_sender(self, sender_name):
        """Check if there are emails from specific sender"""
        try:
            script = f'''
            tell application "Mail"
                set matchingMessages to (messages of inbox whose sender contains "{sender_name}")
                set msgCount to count of matchingMessages
                return msgCount
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                count = int(result.stdout.strip())
                if count == 0:
                    return f"No emails from {sender_name}."
                elif count == 1:
                    return f"You have 1 email from {sender_name}."
                else:
                    return f"You have {count} emails from {sender_name}."
            
            return f"Could not search for emails from {sender_name}."
            
        except Exception as e:
            return f"Email search failed: {str(e)}"