import time
import random
import sys
import shutil
import threading

class VisualsManager:
    def __init__(self):
        self.stop_visuals = False

    def _matrix_rain(self, duration):
        """Generates a Matrix-like rain of green characters"""
        chars = "01xyz789ABCDEF"
        # Get terminal size
        cols = shutil.get_terminal_size().columns
        
        end_time = time.time() + duration
        
        # ANSI colors (Green text)
        GREEN = '\033[92m'
        RESET = '\033[0m'
        
        try:
            while time.time() < end_time and not self.stop_visuals:
                line = ""
                for _ in range(cols):
                    if random.random() > 0.95:
                        line += random.choice(chars)
                    else:
                        line += " "
                print(f"{GREEN}{line}{RESET}")
                time.sleep(0.03)
        except KeyboardInterrupt:
            pass
        
        # Clear screen after
        print("\033c", end="")

    def _system_diagnostics(self):
        """Simulates a rapid-fire system scan"""
        modules = [
            "CORE_PROCESSOR", "NEURAL_ENGINE", "BIOMETRIC_SENSORS", 
            "QUANTUM_DECRYPTION", "NETWORK_INTERFACE", "FIREWALL_INTEGRITY",
            "POWER_CELLS", "AUXILIARY_COOLING", "MEMORY_ALLOCATION"
        ]
        
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        RESET = '\033[0m'
        BOLD = '\033[1m'

        print("\033c", end="") # Clear screen
        print(f"{BOLD}{GREEN}INITIALIZING JARVIS DIAGNOSTIC PROTOCOL v4.2...{RESET}\n")
        time.sleep(1)

        for _ in range(50):
            if self.stop_visuals: break
            
            # Generate random hex memory address
            mem_addr = "0x" + "".join(random.choice("0123456789ABCDEF") for _ in range(8))
            
            # 10% chance of a "warning", 90% chance of "OK"
            if random.random() > 0.9:
                status = f"{YELLOW}[RE-ROUTING]{RESET}"
            else:
                status = f"{GREEN}[OK]{RESET}"
                
            module = random.choice(modules)
            print(f"{mem_addr} : CHECKING {module:<20} ... {status}")
            time.sleep(0.02)
        
        print(f"\n{BOLD}{GREEN}>>> SYSTEM INTEGRITY VERIFIED. ALL SYSTEMS GO. <<<{RESET}")
        time.sleep(2)
        print("\033c", end="") # Clear screen

    def start_hackerman_mode(self, duration=5):
        """Runs the visuals in a separate thread so it doesn't block Jarvis"""
        self.stop_visuals = False
        # We can alternate or choose one. Let's do diagnostics for a true 'Iron Man' feel.
        # If you prefer the raining code, change target to self._matrix_rain
        t = threading.Thread(target=self._system_diagnostics)
        t.start()
        return t