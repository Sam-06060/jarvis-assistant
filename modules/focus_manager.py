import subprocess

class FocusManager:
    """Manage macOS Focus modes and Do Not Disturb"""
    
    def __init__(self):
        pass
    
    def enable_do_not_disturb(self):
        """Enable Do Not Disturb mode"""
        try:
            # macOS Monterey and later use Focus modes
            script = '''
            tell application "System Events"
                tell process "Control Center"
                    click menu bar item "Control Center" of menu bar 1
                    delay 0.5
                    click button "Focus" of group 1 of window "Control Center"
                    delay 0.5
                    click button "Do Not Disturb" of group 1 of window "Control Center"
                end tell
            end tell
            '''
            
            # Fallback: Use shortcuts if available
            result = subprocess.run(
                ["shortcuts", "run", "Do Not Disturb"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return "Do Not Disturb enabled."
            else:
                return "Do Not Disturb feature requires manual setup via Shortcuts app."
                
        except Exception as e:
            return f"Could not enable Do Not Disturb: {str(e)}"
    
    def disable_do_not_disturb(self):
        """Disable Do Not Disturb mode"""
        try:
            result = subprocess.run(
                ["shortcuts", "run", "Do Not Disturb Off"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return "Do Not Disturb disabled."
            else:
                return "Could not disable Do Not Disturb. Set up via Shortcuts app."
                
        except Exception as e:
            return f"Could not disable Do Not Disturb: {str(e)}"
    
    def set_focus_mode(self, mode):
        """Set specific focus mode (Work, Personal, Sleep, etc.)"""
        try:
            # This requires Shortcuts to be set up
            result = subprocess.run(
                ["shortcuts", "run", f"Focus - {mode}"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                return f"{mode} focus mode enabled."
            else:
                return f"Could not enable {mode} mode. Create shortcut in Shortcuts app."
                
        except Exception as e:
            return f"Could not set focus mode: {str(e)}"
    
    def get_focus_status(self):
        """Check if Do Not Disturb is enabled"""
        try:
            # This is tricky to check programmatically
            # For now, return a general message
            return "Focus status check requires manual verification."
            
        except Exception as e:
            return f"Could not check focus status: {str(e)}"
    
    def set_work_mode(self):
        """Enable work focus mode"""
        return self.set_focus_mode("Work")
    
    def set_personal_mode(self):
        """Enable personal focus mode"""
        return self.set_focus_mode("Personal")
    
    def set_sleep_mode(self):
        """Enable sleep focus mode"""
        return self.set_focus_mode("Sleep")