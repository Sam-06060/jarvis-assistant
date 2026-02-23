import os
import glob
import json
from datetime import datetime

class FileManager:
    def __init__(self, audit_log_file="data/file_audit.json"):
        self.home_dir = os.path.expanduser("~")
        self.audit_log_file = audit_log_file
        
        # Dangerous paths to block
        self.blocked_paths = [
            "/System",
            "/Library",
            "/usr",
            "/bin",
            "/sbin",
            "/etc"
        ]
        
        # Command blacklist
        self.dangerous_operations = [
            "rm -rf /",
            "del /",
            "format",
            "fdisk"
        ]
    
    def _log_operation(self, operation, filepath, success, error=None):
        """Log file operations for audit trail"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "filepath": filepath,
                "success": success,
                "error": str(error) if error else None
            }
            
            # Load existing log
            log = []
            if os.path.exists(self.audit_log_file):
                try:
                    with open(self.audit_log_file, 'r') as f:
                        log = json.load(f)
                except:
                    log = []
            
            log.append(log_entry)
            
            # Keep only last 100 entries
            if len(log) > 100:
                log = log[-100:]
            
            # Save log
            os.makedirs(os.path.dirname(self.audit_log_file), exist_ok=True)
            with open(self.audit_log_file, 'w') as f:
                json.dump(log, f, indent=2)
                
        except Exception as e:
            print(f"Warning: Could not log operation: {e}")
    
    def _is_safe_path(self, filepath):
        """Check if path is safe to modify"""
        abs_path = os.path.abspath(filepath)
        
        for blocked in self.blocked_paths:
            if abs_path.startswith(blocked):
                return False, f"Access to {blocked} is restricted for safety"
        
        return True, "Path is safe"
    
    def create_file(self, filename, content=""):
        """Create a new file with safety checks"""
        try:
            # Safety check
            safe, message = self._is_safe_path(filename)
            if not safe:
                self._log_operation("create", filename, False, message)
                return f"❌ {message}"
            
            # Create file
            with open(filename, 'w') as f:
                f.write(content)
            
            self._log_operation("create", filename, True)
            return f"✅ File created: {filename}"
            
        except Exception as e:
            self._log_operation("create", filename, False, e)
            return f"❌ Error creating file: {e}"
    
    def read_file(self, filename):
        """Read a file"""
        try:
            # Safety check
            safe, message = self._is_safe_path(filename)
            if not safe:
                return f"❌ {message}"
            
            if not os.path.exists(filename):
                return f"❌ File not found: {filename}"
            
            with open(filename, 'r') as f:
                content = f.read()
            
            self._log_operation("read", filename, True)
            
            # Truncate long files for display
            if len(content) > 500:
                return content[:500] + f"\n\n... (truncated, {len(content)} total characters)"
            
            return content
            
        except Exception as e:
            self._log_operation("read", filename, False, e)
            return f"❌ Error reading file: {e}"
    
    def delete_file(self, filename, confirmed=False):
        """Delete a file with confirmation"""
        try:
            # Safety check
            safe, message = self._is_safe_path(filename)
            if not safe:
                self._log_operation("delete", filename, False, message)
                return f"❌ {message}"
            
            if not os.path.exists(filename):
                return f"❌ File not found: {filename}"
            
            # Require confirmation for deletions
            if not confirmed:
                return f"⚠️ Delete '{filename}'? Say 'yes' to confirm."
            
            os.remove(filename)
            self._log_operation("delete", filename, True)
            return f"✅ File deleted: {filename}"
            
        except Exception as e:
            self._log_operation("delete", filename, False, e)
            return f"❌ Error deleting file: {e}"
    
    def list_files(self, directory="."):
        """List files in directory"""
        try:
            # Safety check
            safe, message = self._is_safe_path(directory)
            if not safe:
                return f"❌ {message}"
            
            if not os.path.exists(directory):
                return f"❌ Directory not found: {directory}"
            
            files = os.listdir(directory)
            
            if not files:
                return "No files found."
            
            # Separate directories and files
            dirs = [f for f in files if os.path.isdir(os.path.join(directory, f))]
            files = [f for f in files if os.path.isfile(os.path.join(directory, f))]
            
            result = []
            if dirs:
                result.append("Directories:")
                result.extend([f"  📁 {d}" for d in sorted(dirs)[:10]])
            
            if files:
                result.append("\nFiles:")
                result.extend([f"  📄 {f}" for f in sorted(files)[:10]])
            
            total = len(dirs) + len(files)
            if total > 20:
                result.append(f"\n... and {total - 20} more items")
            
            self._log_operation("list", directory, True)
            return "\n".join(result)
            
        except Exception as e:
            self._log_operation("list", directory, False, e)
            return f"❌ Error listing files: {e}"
    
    def search_files(self, pattern, directory="."):
        """Search for files matching pattern"""
        try:
            # Safety check
            safe, message = self._is_safe_path(directory)
            if not safe:
                return f"❌ {message}"
            
            matches = glob.glob(os.path.join(directory, f"*{pattern}*"))
            
            if matches:
                # Limit results
                result = "Found files:\n"
                for match in matches[:20]:
                    result += f"  📄 {match}\n"
                
                if len(matches) > 20:
                    result += f"... and {len(matches) - 20} more"
                
                self._log_operation("search", f"{directory}/{pattern}", True)
                return result.strip()
            
            return f"No files found matching '{pattern}'"
            
        except Exception as e:
            self._log_operation("search", f"{directory}/{pattern}", False, e)
            return f"❌ Error searching: {e}"
    
    def get_file_info(self, filename):
        """Get detailed file information"""
        try:
            if not os.path.exists(filename):
                return f"❌ File not found: {filename}"
            
            stat = os.stat(filename)
            size_bytes = stat.st_size
            
            # Format size
            if size_bytes < 1024:
                size = f"{size_bytes} B"
            elif size_bytes < 1024**2:
                size = f"{size_bytes/1024:.1f} KB"
            elif size_bytes < 1024**3:
                size = f"{size_bytes/(1024**2):.1f} MB"
            else:
                size = f"{size_bytes/(1024**3):.1f} GB"
            
            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            info = f"""
File: {filename}
Size: {size}
Modified: {modified}
Permissions: {oct(stat.st_mode)[-3:]}
"""
            return info.strip()
            
        except Exception as e:
            return f"❌ Error getting file info: {e}"
    
    def get_audit_log(self, count=10):
        """Get recent file operations"""
        try:
            if not os.path.exists(self.audit_log_file):
                return "No file operations logged yet."
            
            with open(self.audit_log_file, 'r') as f:
                log = json.load(f)
            
            if not log:
                return "No file operations logged yet."
            
            result = "Recent file operations:\n"
            for entry in log[-count:]:
                timestamp = entry['timestamp'][:19]
                operation = entry['operation']
                filepath = entry['filepath']
                status = "✅" if entry['success'] else "❌"
                
                result += f"{status} {timestamp} - {operation}: {filepath}\n"
            
            return result.strip()
            
        except Exception as e:
            return f"❌ Error reading audit log: {e}"