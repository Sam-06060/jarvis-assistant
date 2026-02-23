import json
import os
from datetime import datetime
from collections import Counter, defaultdict

class Analytics:
    """Track usage statistics and performance"""
    
    def __init__(self, data_file="data/analytics.json"):
        self.data_file = data_file
        self.data = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "command_types": {},
            "most_used_commands": [],
            "average_response_time": 0,
            "total_response_time": 0,
            "sessions": [],
            "daily_usage": {},
            "hourly_usage": defaultdict(int),
        }
        self.session_start = datetime.now()
        self.current_session = {
            "start": self.session_start.isoformat(),
            "commands": [],
            "duration": 0
        }
        self.load_data()
    
    def load_data(self):
        """Load analytics from disk"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
                    # Convert hourly_usage back to defaultdict
                    if "hourly_usage" in loaded:
                        self.data["hourly_usage"] = defaultdict(int, loaded["hourly_usage"])
        except Exception as e:
            print(f"Warning: Could not load analytics: {e}")
    
    def save_data(self):
        """Save analytics to disk"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            # Convert defaultdict to regular dict for JSON
            save_data = self.data.copy()
            save_data["hourly_usage"] = dict(self.data["hourly_usage"])
            
            with open(self.data_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save analytics: {e}")
    
    def log_command(self, command, command_type, success, response_time=0):
        """Log a command execution"""
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        hour = now.strftime("%H:00")
        
        # Update totals
        self.data["total_commands"] += 1
        if success:
            self.data["successful_commands"] += 1
        else:
            self.data["failed_commands"] += 1
        
        # Track command types
        if command_type not in self.data["command_types"]:
            self.data["command_types"][command_type] = 0
        self.data["command_types"][command_type] += 1
        
        # Track response time
        if response_time > 0:
            self.data["total_response_time"] += response_time
            self.data["average_response_time"] = (
                self.data["total_response_time"] / self.data["total_commands"]
            )
        
        # Daily usage
        if today not in self.data["daily_usage"]:
            self.data["daily_usage"][today] = 0
        self.data["daily_usage"][today] += 1
        
        # Hourly usage
        self.data["hourly_usage"][hour] += 1
        
        # Current session
        self.current_session["commands"].append({
            "command": command,
            "type": command_type,
            "success": success,
            "timestamp": now.isoformat()
        })
        
        # Update most used commands
        self._update_most_used(command)
        
        self.save_data()
    
    def _update_most_used(self, command):
        """Update most used commands list"""
        commands = [cmd for cmd, count in self.data.get("most_used_commands", [])]
        commands.append(command)
        counter = Counter(commands)
        self.data["most_used_commands"] = counter.most_common(10)
    
    def end_session(self):
        """End current session and save"""
        self.current_session["end"] = datetime.now().isoformat()
        duration = (datetime.now() - self.session_start).total_seconds()
        self.current_session["duration"] = duration
        
        self.data["sessions"].append(self.current_session)
        # Keep only last 30 sessions
        if len(self.data["sessions"]) > 30:
            self.data["sessions"] = self.data["sessions"][-30:]
        
        self.save_data()
    
    def get_stats(self):
        """Get formatted statistics"""
        success_rate = 0
        if self.data["total_commands"] > 0:
            success_rate = (
                self.data["successful_commands"] / self.data["total_commands"] * 100
            )
        
        stats = f"""
📊 JARVIS Usage Statistics:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Commands: {self.data['total_commands']}
Success Rate: {success_rate:.1f}%
Avg Response Time: {self.data['average_response_time']:.2f}s
Total Sessions: {len(self.data['sessions'])}

Most Used Commands:
"""
        
        for cmd, count in self.data["most_used_commands"][:5]:
            stats += f"  • {cmd}: {count} times\n"
        
        # Top command types
        if self.data["command_types"]:
            stats += "\nCommand Types:\n"
            sorted_types = sorted(
                self.data["command_types"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for cmd_type, count in sorted_types:
                stats += f"  • {cmd_type}: {count}\n"
        
        return stats.strip()
    
    def get_today_stats(self):
        """Get today's statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        commands_today = self.data["daily_usage"].get(today, 0)
        return f"Commands today: {commands_today}"
    
    def reset_stats(self):
        """Reset all statistics"""
        self.data = {
            "total_commands": 0,
            "successful_commands": 0,
            "failed_commands": 0,
            "command_types": {},
            "most_used_commands": [],
            "average_response_time": 0,
            "total_response_time": 0,
            "sessions": [],
            "daily_usage": {},
            "hourly_usage": defaultdict(int),
        }
        self.save_data()
        return "Analytics reset successfully."