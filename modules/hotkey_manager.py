import time
from pynput import keyboard
from utils.logger import get_logger
logger = get_logger()

class HotkeyManager:
    def __init__(self, on_single_tap=None, on_double_tap=None):
        """
        on_single_tap: Function to run on Single Tap (e.g., Stop Speaking)
        on_double_tap: Function to run on Double Tap (e.g., Kill Switch)
        """
        self.on_single_tap = on_single_tap
        self.on_double_tap = on_double_tap
        self.listener = None
        
        # State
        self.last_tap_time = 0
        self.tap_count = 0
        self.control_pressed = False
        
    def start(self):
        """Start the global keyboard listener in a background thread"""
        logger.info("⌨️ Starting Global Hotkey Listener...")
        try:
            # Removed on_press to simplify. on_release is enough for Taps.
            self.listener = keyboard.Listener(on_release=self.on_release)
            self.listener.start()
            logger.info("✅ Hotkey Listener Active")
        except Exception as e:
            logger.error(f"❌ Hotkey Start Error: {e}")
        
    def stop(self):
        """Stop the listener"""
        if self.listener:
            try:
                self.listener.stop()
            except: pass

    def on_press(self, key):
        # Unused
        pass

    def on_release(self, key):
        """Check for Control Release"""
        try:
            # print(f"DEBUG: Key Released: {key}") # Uncomment if super desperate
            
            # Check for Control Key (Any variant)
            # pynput defines Key.ctrl, Key.ctrl_l, Key.ctrl_r
            is_ctrl = False
            if key == keyboard.Key.ctrl or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
                is_ctrl = True
            
            if is_ctrl:
                curr_time = time.time()
                
                # Check for Double Tap (within 0.4s)
                if (curr_time - self.last_tap_time) < 0.4:
                    logger.info("⌨️ Double Tap Detected!")
                    self.tap_count = 0
                    self.last_tap_time = 0
                    if self.on_double_tap:
                        self.on_double_tap()
                else:
                    logger.info("⌨️ Single Tap Detected")
                    self.tap_count = 1
                    self.last_tap_time = curr_time
                    if self.on_single_tap:
                        self.on_single_tap()
                    
        except Exception as e:
            print(f"Hotkey Error: {e}")