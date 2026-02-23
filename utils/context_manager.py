import time
from datetime import datetime

class ContextManager:
    """Tracks command execution context for AI awareness"""
    
    def __init__(self):
        self.last_command = None
        self.last_result = None
        self.last_app_opened = None
        self.last_file_created = None
        self.last_search_query = None
        self.conversation_start = datetime.now()
        self.command_history = []
        self.max_history = 20
        
    def log_command(self, command, result, command_type="general"):
        """Log a command execution"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "result": result,
            "type": command_type
        }
        
        self.command_history.append(entry)
        if len(self.command_history) > self.max_history:
            self.command_history.pop(0)
        
        self.last_command = command
        self.last_result = result
        
        # Track specific types
        if command_type == "app":
            self.last_app_opened = result
        elif command_type == "file":
            self.last_file_created = result
        elif command_type == "search":
            self.last_search_query = result
    
    def get_context_string(self):
        """Get context summary for AI"""
        context_parts = []
        
        if self.last_command:
            context_parts.append(f"Last command: '{self.last_command}'")
        
        if self.last_app_opened:
            context_parts.append(f"Last app opened: {self.last_app_opened}")
        
        if self.last_file_created:
            context_parts.append(f"Last file created: {self.last_file_created}")
        
        recent_commands = [c["command"] for c in self.command_history[-5:]]
        if recent_commands:
            context_parts.append(f"Recent commands: {', '.join(recent_commands)}")
        
        return " | ".join(context_parts) if context_parts else "No recent activity"
    
    def get_last_command_info(self):
        """Get detailed info about last command"""
        if not self.command_history:
            return None
        return self.command_history[-1]
    
    def clear_context(self):
        """Clear all context"""
        self.last_command = None
        self.last_result = None
        self.last_app_opened = None
        self.last_file_created = None
        self.last_search_query = None
        self.command_history = []
        self.conversation_start = datetime.now()