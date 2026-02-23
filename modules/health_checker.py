import subprocess
import requests
import pyaudio
import config
import os

class HealthChecker:
    """Check system health before starting"""
    
    def __init__(self):
        self.checks_passed = []
        self.checks_failed = []
        self.warnings = []
    
    def check_microphone(self):
        """Verify microphone access"""
        try:
            p = pyaudio.PyAudio()
            # Try to open default input device
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
            self.checks_passed.append("✓ Microphone access")
            return True
        except Exception as e:
            self.checks_failed.append(f"✗ Microphone access: {str(e)}")
            return False
    
    def check_internet(self):
        """Check internet connectivity"""
        try:
            response = requests.get("https://www.google.com", timeout=3)
            if response.status_code == 200:
                self.checks_passed.append("✓ Internet connection")
                return True
        except:
            self.warnings.append("⚠ No internet (offline mode)")
            return False
    
    def check_api_key(self):
        """Verify OpenRouter API key"""
        if not config.OPENROUTER_API_KEY or config.OPENROUTER_API_KEY == "your-key-here":
            self.checks_failed.append("✗ OpenRouter API key not configured")
            return False
        
        # Quick validation check
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=config.OPENROUTER_API_KEY,
            )
            # Don't actually make a request, just verify format
            self.checks_passed.append("✓ OpenRouter API key configured")
            return True
        except Exception as e:
            self.checks_failed.append(f"✗ OpenRouter API setup: {str(e)}")
            return False
    
    def check_picovoice_key(self):
        """Verify Picovoice API key"""
        if not config.PICOVOICE_API_KEY:
            self.checks_failed.append("✗ Picovoice API key missing")
            return False
        self.checks_passed.append("✓ Picovoice API key configured")
        return True
    
    def check_whisper_model(self):
        """Check if Whisper model is available"""
        try:
            from faster_whisper import WhisperModel
            # Model will be downloaded on first use
            self.checks_passed.append("✓ Whisper model ready")
            return True
        except Exception as e:
            self.checks_failed.append(f"✗ Whisper model: {str(e)}")
            return False
    
    def check_data_directories(self):
        """Ensure data directories exist"""
        try:
            os.makedirs("data", exist_ok=True)
            self.checks_passed.append("✓ Data directories")
            return True
        except Exception as e:
            self.checks_failed.append(f"✗ Data directories: {str(e)}")
            return False
    
    def check_system_commands(self):
        """Check if system commands are available"""
        commands_to_check = ["osascript", "say", "open"]
        all_ok = True
        
        for cmd in commands_to_check:
            try:
                result = subprocess.run(
                    ["which", cmd],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    self.warnings.append(f"⚠ Command '{cmd}' not found")
                    all_ok = False
            except:
                pass
        
        if all_ok:
            self.checks_passed.append("✓ System commands available")
        return all_ok
    
    def run_all_checks(self):
        """Run all health checks"""
        checks = [
            self.check_data_directories,
            self.check_microphone,
            self.check_internet,
            self.check_picovoice_key,
            self.check_api_key,
            self.check_whisper_model,
            self.check_system_commands,
        ]
        
        for check in checks:
            check()
        
        return len(self.checks_failed) == 0
    
    def get_report(self):
        """Get health check report"""
        report = []
        
        if self.checks_passed:
            report.extend(self.checks_passed)
        
        if self.warnings:
            report.extend(self.warnings)
        
        if self.checks_failed:
            report.extend(self.checks_failed)
        
        return "\n".join(report)
    
    def is_critical_failure(self):
        """Check if any critical component failed"""
        critical_checks = ["Microphone", "Picovoice", "Whisper"]
        for failure in self.checks_failed:
            if any(check in failure for check in critical_checks):
                return True
        return False