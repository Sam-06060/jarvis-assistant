import os
import config
from .base import AgentTool

class ReadSourceFileTool(AgentTool):
    name = "read_source_file"
    description = "Read the content of a file in the JARVIS codebase. Input: {'path': 'relative/path/to/file.py'}"
    permission = "safe"
    
    def run(self, inp: dict):
        try:
            rel_path = inp.get('path', '').strip()
            if not rel_path: return "Error: No path provided."
            # Security Guard: No absolute paths, no traveling up
            if rel_path.startswith("/") or ".." in rel_path:
                 return "Error: Absolute paths or parent directory travel (..) are forbidden."
            
            full_path = os.path.join(config.ROOT_DIR, rel_path)
            if not os.path.exists(full_path):
                return f"Error: File not found at {rel_path}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class ListSourceDirTool(AgentTool):
    name = "list_source_dir"
    description = "List files and directories in a JARVIS source folder. Input: {'path': 'relative/path'}"
    permission = "safe"
    
    def run(self, inp: dict):
        try:
            rel_path = inp.get('path', '.').strip()
            if rel_path.startswith("/") or ".." in rel_path:
                 return "Error: Forbidden path."
            
            full_path = os.path.join(config.ROOT_DIR, rel_path)
            if not os.path.isdir(full_path):
                return f"Error: Directory not found at {rel_path}"
            
            items = sorted(os.listdir(full_path))
            return f"Contents of {rel_path}:\n" + "\n".join(items)
        except Exception as e:
            return f"Error listing directory: {str(e)}"

class ApplySourceChangeTool(AgentTool):
    name = "apply_code_change"
    description = "Overwrite a source file with new code. Input: {'path': 'relative/path', 'content': 'full file content'}. Requires confirmation."
    tier = 2
    permission = "write"
    
    def run(self, inp: dict):
        try:
            rel_path = inp.get('path', '').strip()
            content = inp.get('content', '')
            if not rel_path or rel_path.startswith("/") or ".." in rel_path:
                 return "Error: Invalid or forbidden path."
            
            full_path = os.path.join(config.ROOT_DIR, rel_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ Successfully updated source file: {rel_path}"
        except Exception as e:
            return f"Error applying change: {str(e)}"
