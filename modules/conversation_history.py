import json
import os
import config
from datetime import datetime, timedelta

class ConversationHistory:
    """Store and manage conversation history"""
    
    def __init__(self, history_file="data/conversation_history.json"):
        self.history_file = history_file
        self.conversations = []
        self.current_session = {
            "start": datetime.now().isoformat(),
            "exchanges": []
        }
        self.load_history()
    
    def load_history(self):
        """Load conversation history from disk"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.conversations = json.load(f)
                self._cleanup_old_conversations()
        except Exception as e:
            print(f"Warning: Could not load conversation history: {e}")
            self.conversations = []
    
    def save_history(self):
        """Save conversation history to disk"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.conversations, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save conversation history: {e}")
    
    def _cleanup_old_conversations(self):
        """Remove conversations older than configured days"""
        if not hasattr(config, 'CONVERSATION_HISTORY_DAYS'):
            return
        
        cutoff = datetime.now() - timedelta(days=config.CONVERSATION_HISTORY_DAYS)
        cutoff_str = cutoff.isoformat()
        
        self.conversations = [
            conv for conv in self.conversations
            if conv.get("start", "") > cutoff_str
        ]
    
    def log_exchange(self, user_input, assistant_response, command_type="general"):
        """Log a conversation exchange"""
        exchange = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "assistant": assistant_response,
            "type": command_type
        }
        
        self.current_session["exchanges"].append(exchange)
    
    def end_session(self):
        """End current session and save"""
        if not self.current_session["exchanges"]:
            return
        
        self.current_session["end"] = datetime.now().isoformat()
        self.current_session["duration"] = self._calculate_duration()
        
        self.conversations.append(self.current_session)
        
        # Keep only last 50 sessions
        if len(self.conversations) > 50:
            self.conversations = self.conversations[-50:]
        
        self.save_history()
        
        # Start new session
        self.current_session = {
            "start": datetime.now().isoformat(),
            "exchanges": []
        }
    
    def _calculate_duration(self):
        """Calculate session duration in seconds"""
        try:
            start = datetime.fromisoformat(self.current_session["start"])
            end = datetime.now()
            return (end - start).total_seconds()
        except:
            return 0
    
    def search_history(self, query, limit=10):
        """Search conversation history"""
        query_lower = query.lower()
        results = []
        
        for conversation in reversed(self.conversations):
            for exchange in conversation["exchanges"]:
                if query_lower in exchange["user"].lower() or query_lower in exchange["assistant"].lower():
                    results.append({
                        "date": exchange["timestamp"][:10],
                        "user": exchange["user"],
                        "assistant": exchange["assistant"][:100] + "..." if len(exchange["assistant"]) > 100 else exchange["assistant"]
                    })
                    
                    if len(results) >= limit:
                        break
            
            if len(results) >= limit:
                break
        
        if not results:
            return f"No conversations found containing '{query}'"
        
        output = f"Found {len(results)} matches:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. [{result['date']}]\n"
            output += f"   You: {result['user']}\n"
            output += f"   Jarvis: {result['assistant']}\n\n"
        
        return output.strip()
    
    def get_recent_conversations(self, count=5):
        """Get recent conversation exchanges"""
        if not self.conversations:
            return "No conversation history available."
        
        recent = []
        for conversation in reversed(self.conversations):
            for exchange in reversed(conversation["exchanges"]):
                recent.append(exchange)
                if len(recent) >= count:
                    break
            if len(recent) >= count:
                break
        
        output = "Recent conversations:\n\n"
        for i, exchange in enumerate(recent, 1):
            timestamp = exchange["timestamp"][:16].replace("T", " ")
            output += f"{i}. [{timestamp}] {exchange['user']}\n"
        
        return output.strip()
    
    def get_today_summary(self):
        """Get summary of today's conversations"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_exchanges = []
        
        for conversation in self.conversations:
            for exchange in conversation["exchanges"]:
                if exchange["timestamp"].startswith(today):
                    today_exchanges.append(exchange)
        
        if not today_exchanges:
            return "No conversations today yet."
        
        # Count by type
        types = {}
        for exchange in today_exchanges:
            exchange_type = exchange.get("type", "general")
            types[exchange_type] = types.get(exchange_type, 0) + 1
        
        summary = f"Today's activity ({len(today_exchanges)} exchanges):\n"
        for cmd_type, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
            summary += f"  • {cmd_type}: {count}\n"
        
        return summary.strip()
    
    def clear_history(self):
        """Clear all conversation history"""
        self.conversations = []
        self.save_history()
        return "Conversation history cleared."

    def get_context_window(self, limit=5):
        """
        Get the last few exchanges formatted for LLM context injection.
        Returns a string like:
        [User: ...]
        [Jarvis: ...]
        """
        if not self.current_session["exchanges"] and not self.conversations:
            return ""

        # Gather recent exchanges from current session and previous session if needed
        all_exchanges = []
        
        # 1. Add previous session's exchanges if current is empty or small
        if self.conversations:
            last_session = self.conversations[-1]
            all_exchanges.extend(last_session.get("exchanges", []))
            
        # 2. Add current session
        all_exchanges.extend(self.current_session["exchanges"])
        
        # 3. Slice the last 'limit'
        recent = all_exchanges[-limit:]
        
        if not recent:
            return ""

        context_str = "MEMORY (Recent Conversation):\n"
        for ex in recent:
            user_text = ex.get("user", "").replace("\n", " ")
            ai_text = ex.get("assistant", "").replace("\n", " ")
            context_str += f"[User: {user_text}]\n[Jarvis: {ai_text}]\n"
            
        return context_str.strip()