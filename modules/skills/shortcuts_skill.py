from .base import Skill
import string
import time

class ShortcutsSkill(Skill):
    def can_handle(self, command: str) -> bool:
        # Shortcuts are tricky because trigger words are dynamic.
        # We check if 'shortcuts' manager is present, then let handle() verify.
        # But handle() is only called if can_handle() true...
        # So we must verify existence here OR broad match keywords like "run", "do".
        # Or we always say "Yes" if "shortcut" is in cmd, OR if the command starts with "run/do".
        # The original code runs this check AFTER others.
        triggers = ["shortcut", "run", "do", "execute"]
        return any(t in command.lower() for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        shortcuts = self.app.get('shortcuts')
        if not shortcuts: return False

        # 1. Management
        if "list shortcuts" in cmd:
            self.speech.speak(shortcuts.list_shortcuts())
            return True
            
        if "create shortcut" in cmd:
            self.speech.speak(shortcuts.parse_create_shortcut_command(cmd))
            return True

        # 2. Execution
        # Clean prefix
        clean_cmd = cmd.strip(string.punctuation)
        if clean_cmd.startswith("do "): clean_cmd = clean_cmd[3:].strip()
        elif clean_cmd.startswith("run "): clean_cmd = clean_cmd[4:].strip()
        elif clean_cmd.startswith("execute "): clean_cmd = clean_cmd[8:].strip()

        is_shortcut, shortcut_name = shortcuts.is_shortcut(clean_cmd)
        
        if is_shortcut:
            commands = shortcuts.get_shortcut(shortcut_name)
            if commands:
                self.speech.speak(f"Running {shortcut_name}.")
                for sub in commands:
                    self.speech.speak(f"Executing: {sub}")
                    # Recursion: Requires calling back to processor?
                    # Using self.app['command_processor'].process(sub)
                    # We need to ensure 'command_processor' is in context.
                    proc = self.app.get('command_processor')
                    if proc:
                        proc.process(sub, from_routine=True)
                    time.sleep(0.5)
                return True

        return False
