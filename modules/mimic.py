import time
import json
import os
import threading
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key, KeyCode

# --- NEW: Import AppKit for Dock Management ---
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    APPKIT_AVAILABLE = True
except ImportError:
    APPKIT_AVAILABLE = False
# ----------------------------------------------

class TheMimic:
    def __init__(self):
        self.is_recording = False
        self.events = []
        self.start_time = 0
        self.mouse_listener = None
        self.keyboard_listener = None
        self.macro_dir = "macros"
        
        # Ensure macro directory exists
        if not os.path.exists(self.macro_dir):
            os.makedirs(self.macro_dir)

        # Controllers for replay
        self.mouse_ctrl = mouse.Controller()
        self.keyboard_ctrl = keyboard.Controller()

    # --- RECORDING ENGINE ---
    def start_recording(self):
        self.events = []
        self.start_time = time.time()
        self.is_recording = True
        
        # Start Non-Blocking Listeners
        self.mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll)
        
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release)
            
        self.mouse_listener.start()
        self.keyboard_listener.start()
        return "I am watching. Perform the task now."

    def stop_and_save(self, name):
        if not self.is_recording:
            return "I wasn't recording anything."
            
        self.is_recording = False
        self.mouse_listener.stop()
        self.keyboard_listener.stop()
        
        # Clean the name
        filename = name.lower().replace(" ", "_").strip() + ".json"
        filepath = os.path.join(self.macro_dir, filename)
        
        # Save to JSON
        with open(filepath, 'w') as f:
            json.dump(self.events, f)
            
        return f"Learned. Saved as '{filename}'."

    # --- EVENT LOGGERS ---
    def _log(self, data):
        if self.is_recording:
            data['delay'] = time.time() - self.start_time
            self.start_time = time.time() # Reset for relative delta
            self.events.append(data)

    def _on_move(self, x, y):
        # Optimization: We don't need every micro-movement.
        self._log({'type': 'move', 'x': x, 'y': y})

    def _on_click(self, x, y, button, pressed):
        self._log({'type': 'click', 'x': x, 'y': y, 'button': str(button), 'pressed': pressed})

    def _on_scroll(self, x, y, dx, dy):
        self._log({'type': 'scroll', 'x': x, 'y': y, 'dx': dx, 'dy': dy})

    def _on_press(self, key):
        self._log({'type': 'press', 'key': self._key_to_str(key)})

    def _on_release(self, key):
        self._log({'type': 'release', 'key': self._key_to_str(key)})

    # --- SERIALIZATION HELPER ---
    def _key_to_str(self, key):
        if isinstance(key, Key):
            return str(key) 
        elif isinstance(key, KeyCode):
            return str(key.char) 
        return str(key)

    def _str_to_key(self, key_str):
        # Convert string back to Key object
        if "Key." in key_str:
            try:
                return getattr(Key, key_str.split(".")[1])
            except:
                return None
        return key_str.strip("'")

    def _str_to_button(self, btn_str):
        if "left" in btn_str: return Button.left
        if "right" in btn_str: return Button.right
        if "middle" in btn_str: return Button.middle
        return Button.left

    # --- REPLAY ENGINE ---
    def execute(self, name, speed_multiplier=1.5):
        filename = name.lower().replace(" ", "_").strip()
        if not filename.endswith(".json"): filename += ".json"
        
        filepath = os.path.join(self.macro_dir, filename)
        
        if not os.path.exists(filepath):
            return f"I don't know the macro '{name}'."

        try:
            with open(filepath, 'r') as f:
                events = json.load(f)
            
            # Run in a separate thread to not block Jarvis
            t = threading.Thread(target=self._replay_thread, args=(events, speed_multiplier))
            t.start()
            return f"Executing {name} at {speed_multiplier}x speed."
        except Exception as e:
            return f"Failed to execute: {e}"

    def _replay_thread(self, events, speed):
        try:
            for event in events:
                # 1. Wait the correct amount of time (Speed adjusted)
                time.sleep(event['delay'] / speed)
                
                # 2. Execute Action
                action = event['type']
                
                if action == 'move':
                    self.mouse_ctrl.position = (event['x'], event['y'])
                    
                elif action == 'click':
                    btn = self._str_to_button(event['button'])
                    if event['pressed']:
                        self.mouse_ctrl.press(btn)
                    else:
                        self.mouse_ctrl.release(btn)
                        
                elif action == 'scroll':
                    self.mouse_ctrl.scroll(event['dx'], event['dy'])
                    
                elif action == 'press':
                    k = self._str_to_key(event['key'])
                    if k: self.mouse_ctrl.keyboard_listener = None # Safety
                    try: self.keyboard_ctrl.press(k)
                    except: pass
                    
                elif action == 'release':
                    k = self._str_to_key(event['key'])
                    try: self.keyboard_ctrl.release(k)
                    except: pass

        except Exception as e:
            print(f"Mimic Replay Error: {e}")

        finally:
            # --- THE FIX: HIDE DOCK ICON AFTER EXECUTION ---
            self._hide_dock_icon()

    def _hide_dock_icon(self):
        """
        Switches the application policy to 'Accessory'.
        This removes it from the Dock and App Switcher without killing the process.
        """
        if APPKIT_AVAILABLE:
            try:
                # Get shared application instance
                app = NSApplication.sharedApplication()
                
                # Set policy to Accessory (Value 1)
                # 0 = Regular (Dock Icon)
                # 1 = Accessory (No Dock Icon, but can have UI)
                # 2 = Prohibited (Background only)
                app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
            except Exception as e:
                print(f"Could not hide dock icon: {e}")