from .base import Skill

class FileSkill(Skill):
    def can_handle(self, command: str) -> bool:
        triggers = ["create file", "delete file", "list files", "drop this file", "share this file"]
        return any(t in command.lower() for t in triggers)

    def handle(self, command: str) -> bool:
        cmd = command.lower()
        files = self.app.get('files')
        dead_drop = self.app.get('dead_drop') # Note: Check context key
        
        # DEAD DROP
        if dead_drop and ("drop this file" in cmd or "share this file" in cmd):
            self.speech.speak("Initializing portal.")
            dead_drop.execute_transfer()
            return True

        # FILE OPS
        if not files: return False

        if "create file" in cmd:
            filename = cmd.replace("create file", "").strip()
            if filename:
                try:
                    result = files.create_file(filename)
                    self.speech.speak(result)
                    self.log_usage(f"create file {filename}")
                except Exception as e:
                    self.logger.error(f"Create file error: {e}")
                    self.speech.speak("I couldn't create the file.")
                return True

        if "delete file" in cmd:
            filename = cmd.replace("delete file", "").strip()
            if filename:
                try:
                    # Assuming confirmation is handled by the skills architecture or we bypass it for now.
                    # The original code had confirmation logic inside the processor.
                    # For now, we'll force delete or just call the method.
                    result = files.delete_file(filename, confirmed=True)
                    self.speech.speak(result)
                except FileNotFoundError:
                    self.speech.speak(f"I couldn't find a file named {filename}.")
                except PermissionError:
                    self.speech.speak("I sort of don't have permission to delete that.")
                except Exception as e:
                    self.logger.error(f"Delete file error: {e}")
                    self.speech.speak("I encountered an error deleting the file.")
                return True

        if "list files" in cmd:
            try:
                result = files.list_files()
                self.speech.speak(result)
            except Exception as e:
                 self.logger.error(f"List files error: {e}")
                 self.speech.speak("I couldn't list the files in this directory.")
            return True
            
        return False
