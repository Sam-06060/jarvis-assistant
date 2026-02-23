import pyperclip
from datetime import datetime
import json
import os

class ClipboardManager:
    """Manage clipboard operations and history"""
    
    def __init__(self, history_file="data/clipboard_history.json"):
        self.history_file = history_file
        self.history = []
        self.max_history = 20
        self.load_history()
    
    def load_history(self):
        """Load clipboard history from disk"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load clipboard history: {e}")
            self.history = []
    
    def save_history(self):
        """Save clipboard history to disk"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save clipboard history: {e}")
    
    def copy(self, text):
        """Copy text to clipboard"""
        try:
            pyperclip.copy(text)
            self._add_to_history(text)
            return f"Copied to clipboard: {text[:50]}..."
        except Exception as e:
            return f"Could not copy to clipboard: {str(e)}"
    
    def paste(self):
        """Get clipboard content"""
        try:
            content = pyperclip.paste()
            if content:
                return content
            return "Clipboard is empty."
        except Exception as e:
            return f"Could not access clipboard: {str(e)}"
    
    def get_clipboard(self):
        """Get current clipboard content"""
        return self.paste()
    
    def _add_to_history(self, text):
        """Add item to clipboard history"""
        entry = {
            "text": text,
            "timestamp": datetime.now().isoformat()
        }
        
        # Don't add duplicates
        if self.history and self.history[0].get("text") == text:
            return
        
        self.history.insert(0, entry)
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history = self.history[:self.max_history]
        
        self.save_history()
    
    def get_history(self, count=5):
        """Get recent clipboard history"""
        if not self.history:
            return "No clipboard history."
        
        result = "Recent clipboard history:\n"
        for i, entry in enumerate(self.history[:count], 1):
            text = entry["text"]
            # Truncate long text
            if len(text) > 60:
                text = text[:60] + "..."
            result += f"{i}. {text}\n"
        
        return result.strip()
    
    def clear_history(self):
        """Clear clipboard history"""
        self.history = []
        self.save_history()
        return "Clipboard history cleared."
    
    def search_history(self, query):
        """Search clipboard history"""
        query = query.lower()
        matches = [
            entry for entry in self.history
            if query in entry["text"].lower()
        ]
        
        if not matches:
            return f"No clipboard entries matching '{query}'."
        
        result = f"Found {len(matches)} matches:\n"
        for i, entry in enumerate(matches[:5], 1):
            text = entry["text"]
            if len(text) > 60:
                text = text[:60] + "..."
            result += f"{i}. {text}\n"
        
        return result.strip()
    
    def copy_from_history(self, index):
        """Copy an item from history back to clipboard"""
        try:
            index = int(index) - 1
            if 0 <= index < len(self.history):
                text = self.history[index]["text"]
                pyperclip.copy(text)
                return f"Copied from history: {text[:50]}..."
            else:
                return "Invalid history index."
        except Exception as e:
            return f"Could not copy from history: {str(e)}"