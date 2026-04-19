from .base import AgentTool

class StoreMemoryTool(AgentTool):
    name = "save_info"
    description = "Save a key piece of information to your internal memory vault for later use in this task. Input: {'key': str, 'value': str}. Example: {'key': 'news_summary', 'value': 'Apple released a new Mac...'}"
    permission = "safe"
    
    def run(self, inp: dict):
        key = inp.get('key', 'default')
        val = inp.get('value', '')
        self.cp.memory_vault[key] = val
        return f"✅ Saved to memory vault under '{key}'. Use 'retrieve_info' with this key later."

class RecallMemoryTool(AgentTool):
    name = "retrieve_info"
    description = "Recall a piece of information you saved earlier. Input: {'key': str}"
    permission = "safe"
    
    def run(self, inp: dict):
        key = inp.get('key', 'default')
        val = self.cp.memory_vault.get(key)
        if val: return f"Memory found for '{key}':\n{val}"
        return f"Error: No information found in vault for key '{key}'."

class ListMemoryTool(AgentTool):
    name = "list_memory"
    description = "List all keys currently stored in your memory vault."
    permission = "safe"
    
    def run(self, inp: dict):
        if not self.cp.memory_vault: return "The memory vault is currently empty."
        return f"Information currently in vault: {', '.join(self.cp.memory_vault.keys())}"
