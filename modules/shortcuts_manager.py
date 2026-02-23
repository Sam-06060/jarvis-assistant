import json
import os
from datetime import datetime

class ShortcutsManager:
    """Manage custom command shortcuts and macros"""
    
    def __init__(self, shortcuts_file="data/shortcuts.json"):
        self.shortcuts_file = shortcuts_file
        self.shortcuts = {}
        self.load_shortcuts()
        
        # Pre-defined shortcuts
        self.default_shortcuts = {
            "morning routine": [
                "open mail",
                "open calendar",
                "what's the weather",
                "what's in the news"
            ],
            "work mode": [
                "enable do not disturb",
                "open vscode",
                "open terminal",
                "open spotify"
            ],
            "shutdown routine": [
                "close all apps",
                "clear memory",
                "goodbye"
            ]
        }
    
    def load_shortcuts(self):
        """Load shortcuts from disk"""
        try:
            if os.path.exists(self.shortcuts_file):
                with open(self.shortcuts_file, 'r') as f:
                    self.shortcuts = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load shortcuts: {e}")
            self.shortcuts = {}
    
    def save_shortcuts(self):
        """Save shortcuts to disk"""
        try:
            os.makedirs(os.path.dirname(self.shortcuts_file), exist_ok=True)
            with open(self.shortcuts_file, 'w') as f:
                json.dump(self.shortcuts, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save shortcuts: {e}")
    
    def create_shortcut(self, name, commands):
        """Create a new shortcut"""
        if isinstance(commands, str):
            commands = [cmd.strip() for cmd in commands.split(",")]
        
        from datetime import datetime
        self.shortcuts[name.lower()] = {
            "commands": commands,
            "created": datetime.now().isoformat()
        }
        self.save_shortcuts()
        return f"Shortcut '{name}' created with {len(commands)} commands."
    
    def get_shortcut(self, name):
        """Get commands for a shortcut"""
        name_lower = name.lower()
        
        # Debug
        print(f"🔍 Looking for shortcut: '{name_lower}'")
        print(f"   Available custom shortcuts: {list(self.shortcuts.keys())}")
        print(f"   Available default shortcuts: {list(self.default_shortcuts.keys())}")
        
        # Check custom shortcuts
        if name_lower in self.shortcuts:
            print(f"   ✅ Found in custom shortcuts!")
            return self.shortcuts[name_lower]["commands"]
        
        # Check default shortcuts
        if name_lower in self.default_shortcuts:
            print(f"   ✅ Found in default shortcuts!")
            return self.default_shortcuts[name_lower]
        
        print(f"   ❌ Not found")
        return None
    
    def is_shortcut(self, command):
        """Check if command is a shortcut"""
        command_lower = command.lower().strip()
        
        # Check for "do X" or "run X" or "execute X" patterns
        for prefix in ["do ", "run ", "execute ", "start "]:
            if command_lower.startswith(prefix):
                shortcut_name = command_lower[len(prefix):].strip()
                
                # Check if this shortcut exists
                if self.get_shortcut(shortcut_name) is not None:
                    return True, shortcut_name
        
        # Check direct shortcut name (no prefix)
        if self.get_shortcut(command_lower) is not None:
            return True, command_lower
        
        return False, None
    
    def list_shortcuts(self):
        """List all available shortcuts"""
        all_shortcuts = {**self.default_shortcuts, **{k: v["commands"] for k, v in self.shortcuts.items()}}
        
        if not all_shortcuts:
            return "No shortcuts available. Create one with: 'create shortcut morning as open mail, check weather'"
        
        result = "Available shortcuts:\n\n"
        
        if self.default_shortcuts:
            result += "Default shortcuts:\n"
            for name, commands in self.default_shortcuts.items():
                result += f"  • {name} ({len(commands)} commands)\n"
        
        if self.shortcuts:
            result += "\nCustom shortcuts:\n"
            for name, data in self.shortcuts.items():
                result += f"  • {name} ({len(data['commands'])} commands)\n"
        
        return result.strip()
    
    def delete_shortcut(self, name):
        """Delete a custom shortcut"""
        name_lower = name.lower()
        
        if name_lower in self.default_shortcuts:
            return "Cannot delete default shortcuts."
        
        if name_lower in self.shortcuts:
            del self.shortcuts[name_lower]
            self.save_shortcuts()
            return f"Shortcut '{name}' deleted."
        
        return f"Shortcut '{name}' not found."
    
    def get_shortcut_details(self, name):
        """Get detailed info about a shortcut"""
        commands = self.get_shortcut(name)
        
        if not commands:
            return f"Shortcut '{name}' not found."
        
        result = f"Shortcut: {name}\n"
        result += f"Commands ({len(commands)}):\n"
        for i, cmd in enumerate(commands, 1):
            result += f"  {i}. {cmd}\n"
        
        return result.strip()
    
    def parse_create_shortcut_command(self, command):
        """Parse 'create shortcut X as Y, Z' command"""
        import re
        
        # Pattern: "create shortcut NAME as COMMAND1, COMMAND2, ..."
        match = re.search(r'create shortcut\s+(.+?)\s+as\s+(.+)', command.lower())
        
        if match:
            name = match.group(1).strip()
            commands_str = match.group(2).strip()
            commands = [cmd.strip() for cmd in commands_str.split(",")]
            
            return self.create_shortcut(name, commands)
        
        return "Format: 'create shortcut morning routine as open mail, check weather, play music'"