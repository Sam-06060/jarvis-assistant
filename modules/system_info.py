import psutil
import platform
import subprocess
import requests
import config

class SystemInfo:
    def __init__(self):
        self.last_network_check = None
        self.is_online = True
    
    def get_battery(self):
        """Get battery status"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "Plugged in" if battery.power_plugged else "On battery"
                
                # Add time remaining estimate
                if not battery.power_plugged and battery.secsleft > 0:
                    hours = battery.secsleft // 3600
                    minutes = (battery.secsleft % 3600) // 60
                    return f"Battery: {percent}% ({plugged}, {hours}h {minutes}m remaining)"
                
                return f"Battery: {percent}% ({plugged})"
            return "Battery information not available"
        except Exception as e:
            return f"Error getting battery: {e}"
    
    def get_memory(self):
        """Get memory usage"""
        try:
            mem = psutil.virtual_memory()
            used_gb = mem.used / (1024**3)
            total_gb = mem.total / (1024**3)
            available_gb = mem.available / (1024**3)
            
            return f"Memory: {mem.percent}% used ({used_gb:.1f}GB / {total_gb:.1f}GB, {available_gb:.1f}GB available)"
        except Exception as e:
            return f"Error getting memory: {e}"
    
    def get_disk(self):
        """Get disk usage"""
        try:
            disk = psutil.disk_usage('/')
            used_gb = disk.used / (1024**3)
            total_gb = disk.total / (1024**3)
            free_gb = disk.free / (1024**3)
            
            return f"Disk: {disk.percent}% used ({used_gb:.1f}GB / {total_gb:.1f}GB, {free_gb:.1f}GB free)"
        except Exception as e:
            return f"Error getting disk: {e}"
    
    def get_cpu(self):
        """Get CPU usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            freq_info = ""
            if cpu_freq:
                freq_info = f", {cpu_freq.current:.0f} MHz"
            
            return f"CPU: {cpu_percent}% used ({cpu_count} cores{freq_info})"
        except Exception as e:
            return f"Error getting CPU: {e}"
    
    def get_system_info(self):
        """Get overall system info"""
        info = f"""
System: {platform.system()} {platform.release()} ({platform.machine()})
Processor: {platform.processor()}
{self.get_cpu()}
{self.get_memory()}
{self.get_disk()}
{self.get_battery()}
Network: {'Online' if self.check_network() else 'Offline'}
"""
        return info.strip()
    
    def check_network(self):
        """Check internet connectivity"""
        try:
            response = requests.get("https://www.google.com", timeout=2)
            self.is_online = response.status_code == 200
            return self.is_online
        except:
            self.is_online = False
            return False
    
    def get_network_status(self):
        """Get network status"""
        if self.check_network():
            return "Network: Online"
        else:
            return "Network: Offline"
    
    def check_memory_usage(self):
        """Check if memory usage is high"""
        mem = psutil.virtual_memory()
        if config.MEMORY_LIMIT_MB:
            used_mb = mem.used / (1024**2)
            if used_mb > config.MEMORY_LIMIT_MB:
                return True, f"Memory usage high: {used_mb:.0f}MB (limit: {config.MEMORY_LIMIT_MB}MB)"
        return False, "Memory usage normal"
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            boot_time = psutil.boot_time()
            from datetime import datetime
            uptime_seconds = datetime.now().timestamp() - boot_time
            
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return f"Uptime: {days}d {hours}h {minutes}m"
        except Exception as e:
            return f"Error getting uptime: {e}"
    
    def get_running_apps(self):
        """Get list of running applications"""
        try:
            result = subprocess.run(
                ["osascript", "-e", 'tell application "System Events" to get name of every process whose background only is false'],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0:
                apps = result.stdout.strip().split(", ")
                return f"Running apps ({len(apps)}): {', '.join(apps[:10])}"
            return "Could not get running apps"
        except Exception as e:
            return f"Error getting apps: {e}"
    
    def get_temperature(self):
        """Get CPU temperature (macOS specific)"""
        try:
            # macOS temperature requires special tools
            # This is a placeholder - actual implementation would need
            # additional software like osx-cpu-temp
            return "Temperature monitoring requires additional software"
        except Exception as e:
            return f"Error getting temperature: {e}"
    
    def check_microphone_permission(self):
        """Check if microphone permission is granted"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
            stream.stop_stream()
            stream.close()
            p.terminate()
            return True, "Microphone access granted"
        except Exception as e:
            return False, f"Microphone access denied: {str(e)}"
    
    def get_detailed_status(self):
        """Get comprehensive system status"""
        status = f"""
🖥️  SYSTEM STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{self.get_cpu()}
{self.get_memory()}
{self.get_disk()}
{self.get_battery()}
{self.get_uptime()}
{self.get_network_status()}
"""
        return status.strip()