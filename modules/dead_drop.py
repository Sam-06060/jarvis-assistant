import os
import time
import subprocess
import threading
import json
import qrcode
import sys
import shutil
import tempfile
import re

class DeadDrop:
    def __init__(self):
        self.temp_dir = None

    def get_selected_file(self):
        script = '''
        tell application "Finder"
            set theSelection to selection
            if length of theSelection is 0 then
                return "NONE"
            else
                set theFile to item 1 of theSelection
                return POSIX path of (theFile as text)
            end if
        end tell
        '''
        try:
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            path = result.stdout.strip()
            if path == "NONE" or not path: return None
            return path
        except: return None

    # --- CURL HELPER (IRONCLAD MODE) ---
    def run_curl_progress(self, cmd_list, provider_name, timeout=1200):
        print(f"\n   [DeadDrop] 🚀 Initiating launch to {provider_name}...")
        
        # --http1.1 : The Magic Fix (Prevents HTTP/2 Stream crashes)
        # -H "Expect:" : Don't wait for permission, just send data
        # -k : Ignore SSL
        # -4 : Force IPv4
        # -# : Visual Progress Bar
        base_cmd = [
            "curl", "-k", "-4", "-L", "-#", "--http1.1", "-H", "Expect:",
            "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        full_cmd = base_cmd + cmd_list
        
        try:
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=None, # Show progress bar to user
                text=True
            )
            
            stdout, _ = process.communicate(timeout=timeout)
            
            if process.returncode != 0:
                print(f"   [Error] Upload interrupted.")
                return None
                
            return stdout.strip()
            
        except subprocess.TimeoutExpired:
            print(f"\n   [Error] Connection timed out after {timeout}s.")
            process.kill()
            return None
        except Exception as e:
            print(f"\n   [Error] System Fault: {e}")
            return None

    # --- PROVIDER 1: OSHI.AT (Primary) ---
    def upload_oshi(self, file_path):
        cmd = [
            "-F", f"f=@{file_path}",
            "https://oshi.at"
        ]
        response = self.run_curl_progress(cmd, "Oshi.at")
        
        if response:
            match = re.search(r'DL: (https://oshi\.at/dl/[^\s]+)', response)
            if match: return match.group(1)
        return None

    # --- PROVIDER 2: PIXELDRAIN (The Tank) ---
    def upload_pixeldrain(self, file_path):
        # PixelDrain is extremely stable for 50MB+ files
        # ?download forces the direct save
        cmd = [
            "-u", ":",
            "-F", f"file=@{file_path}",
            "https://pixeldrain.com/api/file"
        ]
        response = self.run_curl_progress(cmd, "PixelDrain")
        
        if response:
            try:
                data = json.loads(response)
                if data.get("success"):
                    file_id = data.get("id")
                    return f"https://pixeldrain.com/api/file/{file_id}?download"
            except: pass
        return None

    # --- PROVIDER 3: LITTERBOX (Backup) ---
    def upload_litterbox(self, file_path):
        cmd = [
            "-F", "reqtype=fileupload",
            "-F", "time=1h", 
            "-F", f"fileToUpload=@{file_path}",
            "https://litterbox.catbox.moe/resources/internals/api.php"
        ]
        link = self.run_curl_progress(cmd, "Litterbox")
        if link and link.startswith("http"):
            return link
        return None

    def show_qr(self, url):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(url)
        qr.make(fit=True)
        
        print("\n" + "█"*40)
        print("   SCAN THIS TERMINAL SCREEN")
        print("█"*40)
        try: qr.print_tty() 
        except: qr.print_ascii(invert=True)
        print("█"*40 + "\n")

        try:
            self.temp_dir = tempfile.mkdtemp()
            img = qr.make_image(fill_color="black", back_color="white")
            qr_path = os.path.join(self.temp_dir, "qrcode.png")
            img.save(qr_path)
            
            subprocess.Popen(["open", qr_path])
            
            detect_script = '''
            delay 0.5
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set frontAppName to name of frontApp
            end tell
            try
                tell application frontAppName to activate
            end try
            '''
            subprocess.Popen(["osascript", "-e", detect_script])
                
        except Exception:
            pass

    def cleanup(self):
        try:
            if self.temp_dir: shutil.rmtree(self.temp_dir)
        except: pass

    def _run_sequence(self):
        print("\n--- DEAD DROP SEQUENCE STARTED ---")
        
        file_path = self.get_selected_file()
        if not file_path:
            print("   [Error] No file selected in Finder.")
            return

        filename = os.path.basename(file_path)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"   [DeadDrop] Target: {filename} ({file_size_mb:.1f} MB)")
        
        cloud_link = None
        
        # 1. Oshi (Fastest)
        cloud_link = self.upload_oshi(file_path)
        
        # 2. PixelDrain (Most Stable for medium files)
        if not cloud_link:
            print("   [DeadDrop] Switching to Stable Backup...")
            cloud_link = self.upload_pixeldrain(file_path)
            
        # 3. Litterbox (Final Resort)
        if not cloud_link:
            print("   [DeadDrop] Switching to Heavy Backup...")
            cloud_link = self.upload_litterbox(file_path)

        if not cloud_link:
            print("   [CRITICAL] Upload failed. Protocol error.")
            return
            
        print(f"\n   [DeadDrop] 🚀 Direct Link: {cloud_link}")
        self.show_qr(cloud_link)
        threading.Timer(120, self.cleanup).start()

    def execute_transfer(self):
        t = threading.Thread(target=self._run_sequence, daemon=True)
        t.start()
        return "Initiating Ironclad transfer protocol."