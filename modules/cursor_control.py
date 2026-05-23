import cv2
import mediapipe as mp
import pyautogui
import time
import math
import numpy as np
import config
from collections import deque
from utils.logger import get_logger
logger = get_logger()

# --- ONE EURO FILTER (Standard for Low-Jitter Interaction) ---
class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = 0
        self.dx_prev = 0
        self.t_prev = 0

    def smoothing_factor(self, t_e, cutoff):
        r = 2 * math.pi * cutoff * t_e
        return r / (r + 1)

    def exponential_smoothing(self, a, x, x_prev):
        return a * x + (1 - a) * x_prev

    def filter(self, x, t):
        t_e = t - self.t_prev
        if t_e <= 0: return x 
        dx = (x - self.x_prev) / t_e
        dx_hat = self.exponential_smoothing(self.smoothing_factor(t_e, self.d_cutoff), dx, self.dx_prev)
        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        x_hat = self.exponential_smoothing(self.smoothing_factor(t_e, cutoff), x, self.x_prev)
        self.x_prev = x_hat
        self.dx_prev = dx_hat
        self.t_prev = t
        return x_hat

class CursorController:
    def __init__(self):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = False
        
        # --- VISION SETUP ---
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1, 
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.screen_w, self.screen_h = pyautogui.size()
        
        # --- FILTERS ---
        self.filter_x = OneEuroFilter(min_cutoff=0.5, beta=0.2) 
        self.filter_y = OneEuroFilter(min_cutoff=0.5, beta=0.2)
        
        # --- STATE MANAGEMENT ---
        self.gesture_history = deque(maxlen=2)
        self.peace_start_time = 0
        self.is_dragging = False 
        
        # GESTURE LOCKING SYSTEM
        self.active_mode = None  # "CURSOR", "SCROLL", "DRAG", or None
        self.last_gesture_time = 0
        self.lock_duration = 0.5  # Time to unlock after gesture stops
        
        # --- SCROLL SMOOTHING ---
        self.prev_scroll_y = 0
        self.prev_scroll_x = 0
        # History buffer to average out jitters (The "Liquid" feel)
        self.scroll_history_y = deque(maxlen=5) 
        self.scroll_history_x = deque(maxlen=5)
        # Accumulators to handle slow speeds (Decimal storage)
        self.scroll_acc_y = 0.0
        self.scroll_acc_x = 0.0
        
        # --- CONFIGURATION ---
        self.frame_margin = 110  
        self.window_name = "Jarvis Vision"
        
        # Settings
        self.pinch_threshold = 20      
        self.scroll_sensitivity = 0.5  # DRASTICALLY REDUCED (Was 4.0) for normal speed
        
        # Precision Lock State
        self.anchor_x = 0
        self.anchor_y = 0
        self.locked = False

    def get_gesture_refined(self, lm_list):
        if len(lm_list) < 21: return "NEUTRAL"
        
        thumb_tip = lm_list[4]
        index_tip = lm_list[8]
        middle_tip = lm_list[12]
        ring_tip = lm_list[16]
        pinky_tip = lm_list[20]
        
        index_up = index_tip[2] < lm_list[6][2]
        middle_up = middle_tip[2] < lm_list[10][2]
        ring_up = ring_tip[2] < lm_list[14][2]
        pinky_up = pinky_tip[2] < lm_list[18][2]
        
        pinch_dist = math.hypot(thumb_tip[1]-index_tip[1], thumb_tip[2]-index_tip[2])
        fingers_spread_dist = math.hypot(index_tip[1]-middle_tip[1], index_tip[2]-middle_tip[2])
        
        # --- GESTURE DEFINITIONS ---
        current_gesture = "NEUTRAL"

        # 1. SCROLL (2 Fingers)
        if index_up and middle_up and not ring_up and not pinky_up:
            if fingers_spread_dist < 45: current_gesture = "SCROLL_V"
            else: current_gesture = "PEACE"

        # 2. SCROLL HORIZONTAL (3 Fingers)
        elif index_up and middle_up and ring_up and not pinky_up:
            current_gesture = "SCROLL_H"

        # 3. FIST (Window Drag)
        elif not index_up and not middle_up and not ring_up and not pinky_up:
            current_gesture = "FIST"
            
        # 4. PINCH (Click/Drag)
        elif pinch_dist < self.pinch_threshold and index_up and not middle_up:
            current_gesture = "PINCH"
        
        # 5. POINT (Cursor Move)
        elif index_up and not middle_up and not ring_up and not pinky_up:
            current_gesture = "POINT"
            
        # --- LOCKING LOGIC ---
        curr_time = time.time()
        
        if self.active_mode == "SCROLL":
            # If Locked in SCROLL, ignore everything else
            if "SCROLL" in current_gesture:
                self.last_gesture_time = curr_time
                return current_gesture
            elif current_gesture == "PEACE":
                return "PEACE"
            else:
                if curr_time - self.last_gesture_time < self.lock_duration:
                    return "SCROLL_LOCK" # Dummy gesture to hold lock
                else:
                    self.active_mode = None # Unlock
                    return current_gesture

        if self.active_mode == "DRAG":
            if current_gesture == "FIST":
                self.last_gesture_time = curr_time
                return "FIST"
            elif curr_time - self.last_gesture_time < self.lock_duration:
                 return "FIST_LOCK" 
            else:
                self.active_mode = None
                return current_gesture

        # Set Lock
        if "SCROLL" in current_gesture:
            self.active_mode = "SCROLL"
            self.last_gesture_time = curr_time
        elif current_gesture == "FIST":
            self.active_mode = "DRAG"
            self.last_gesture_time = curr_time
        
        return current_gesture

    def map_coordinates(self, x, y, img_w, img_h):
        """Maps camera coordinates to screen coordinates with smoothing."""
        x_norm = np.interp(x, (self.frame_margin, img_w - self.frame_margin), (0, 1))
        y_norm = np.interp(y, (self.frame_margin, img_h - self.frame_margin), (0, 1))
        
        target_x = x_norm * self.screen_w
        target_y = y_norm * self.screen_h
        
        curr_time = time.time()
        smooth_x = self.filter_x.filter(target_x, curr_time)
        smooth_y = self.filter_y.filter(target_y, curr_time)
        
        return int(smooth_x), int(smooth_y)

    def start(self):
        cap = cv2.VideoCapture(config.CURSOR_CAMERA_INDEX)
        cap.set(3, 640)
        cap.set(4, 480)

        logger.info("🚀 Fluid Gesture Engine Active.")

        # Try to create a display window up-front on the main thread.
        # On macOS, cv2.imshow() requires a Cocoa run-loop; if it isn't available
        # (headless CI, wrong thread, etc.) we fall back to gesture-only mode.
        _headless = False
        try:
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        except Exception as _win_err:
            logger.warning(f"⚠️ Cannot open display window ({_win_err}). Running in headless gesture mode.")
            _headless = True

        exit_status = "NORMAL_EXIT"
        
        try:
            while True:
                success, img = cap.read()
                if not success:
                    logger.error("❌ Camera read failed. Check permissions.")
                    # We can't speak here easily without circular import or passing speech engine, 
                    # but raising an exception allows commands.py to catch it.
                    raise Exception("Camera Access Denied or Device Busy")
                
                h, w, c = img.shape
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(img_rgb)
                
                # Visual Margin
                cv2.rectangle(img, (self.frame_margin, self.frame_margin), 
                             (w - self.frame_margin, h - self.frame_margin), (255, 255, 0), 1)
                
                if results.multi_hand_landmarks:
                    for hand_lms in results.multi_hand_landmarks:
                        lm_list = [[id, int(lm.x * w), int(lm.y * h)] for id, lm in enumerate(hand_lms.landmark)]
                        gesture = self.get_gesture_refined(lm_list)
                        
                        # Handle Lock States
                        if "LOCK" in gesture:
                            continue

                        # --- 1. CURSOR MOVEMENT ---
                        if gesture in ["POINT", "PINCH"]:
                            # Reset Scroll State
                            self.prev_scroll_y = 0; self.prev_scroll_x = 0
                            self.scroll_history_y.clear(); self.scroll_history_x.clear()
                            
                            px, py = lm_list[8][1], lm_list[8][2]
                            raw_screen_x, raw_screen_y = self.map_coordinates(px, py, w, h)
                            
                            # Click Logic
                            if gesture == "PINCH":
                                if not self.locked:
                                    self.anchor_x, self.anchor_y = raw_screen_x, raw_screen_y
                                    self.locked = True
                                
                                drag_dist = math.hypot(raw_screen_x - self.anchor_x, raw_screen_y - self.anchor_y)
                                
                                # 15px Deadzone
                                if drag_dist < 15:
                                    final_x, final_y = self.anchor_x, self.anchor_y
                                else:
                                    final_x, final_y = raw_screen_x, raw_screen_y
                                    
                                if not self.is_dragging:
                                    pyautogui.mouseDown()
                                    self.is_dragging = True
                                
                                cv2.circle(img, (px, py), 15, (0, 255, 0), cv2.FILLED)
                            else:
                                self.locked = False
                                if self.is_dragging:
                                    pyautogui.mouseUp()
                                    self.is_dragging = False
                                
                                final_x, final_y = raw_screen_x, raw_screen_y
                                cv2.circle(img, (px, py), 8, (255, 255, 0), cv2.FILLED)

                            final_x = max(0, min(self.screen_w - 1, final_x))
                            final_y = max(0, min(self.screen_h - 1, final_y))
                            
                            # DEBUG PRINT
                            if gesture == "POINT":
                                logger.debug(f"📍 POINT: ({final_x}, {final_y})")
                            elif gesture == "PINCH":
                                logger.debug(f"👌 PINCH: ({final_x}, {final_y})")
                                
                            pyautogui.moveTo(final_x, final_y, duration=0)

                        # --- 2. WINDOW DRAG ---
                        elif gesture == "FIST":
                            kx, ky = lm_list[9][1], lm_list[9][2]
                            screen_x, screen_y = self.map_coordinates(kx, ky, w, h)
                            
                            screen_x = max(0, min(self.screen_w - 1, screen_x))
                            screen_y = max(0, min(self.screen_h - 1, screen_y))
                            pyautogui.moveTo(screen_x, screen_y, duration=0)
                            
                            if not self.is_dragging:
                                pyautogui.mouseDown()
                                self.is_dragging = True
                            
                            cv2.circle(img, (kx, ky), 20, (0, 0, 255), cv2.FILLED)

                        # --- 3. VERTICAL SCROLL (FLUID AVERAGE) ---
                        elif gesture == "SCROLL_V":
                            if self.is_dragging: pyautogui.mouseUp(); self.is_dragging = False
                            
                            curr_y = (lm_list[8][2] + lm_list[12][2]) // 2
                            
                            if self.prev_scroll_y != 0:
                                raw_delta = (self.prev_scroll_y - curr_y)
                                self.scroll_history_y.append(raw_delta)
                                
                                # AVERAGE the last 5 frames for smoothness
                                avg_delta = sum(self.scroll_history_y) / len(self.scroll_history_y)
                                
                                # Apply sensitivity
                                move_amount = avg_delta * self.scroll_sensitivity
                                
                                # Accumulate decimals
                                self.scroll_acc_y += move_amount
                                
                                # If accumulator crosses 1.0, scroll that integer amount
                                if abs(self.scroll_acc_y) >= 1.0:
                                    pixels_to_scroll = int(self.scroll_acc_y)
                                    pyautogui.scroll(pixels_to_scroll)
                                    self.scroll_acc_y -= pixels_to_scroll # Keep remainder
                                    
                            self.prev_scroll_y = curr_y
                            cv2.putText(img, "SCROLL LOCK", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

                        # --- 4. HORIZONTAL SCROLL (FLUID AVERAGE) ---
                        elif gesture == "SCROLL_H":
                            if self.is_dragging: pyautogui.mouseUp(); self.is_dragging = False
                            
                            curr_x = (lm_list[8][1] + lm_list[12][1] + lm_list[16][1]) // 3
                            
                            if self.prev_scroll_x != 0:
                                raw_delta = (curr_x - self.prev_scroll_x)
                                self.scroll_history_x.append(raw_delta)
                                
                                avg_delta = sum(self.scroll_history_x) / len(self.scroll_history_x)
                                move_amount = avg_delta * self.scroll_sensitivity
                                
                                self.scroll_acc_x += move_amount
                                
                                if abs(self.scroll_acc_x) >= 1.0:
                                    pixels_to_scroll = int(self.scroll_acc_x)
                                    pyautogui.hscroll(pixels_to_scroll)
                                    self.scroll_acc_x -= pixels_to_scroll
                            
                            self.prev_scroll_x = curr_x
                            cv2.putText(img, "SCROLL H LOCK", (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

                        # --- 5. EXIT (PEACE) ---
                        elif gesture == "PEACE":
                            if self.peace_start_time == 0: self.peace_start_time = time.time()
                            elapsed = time.time() - self.peace_start_time
                            
                            bar = int(np.interp(elapsed, [0, 1.5], [0, 150]))
                            cv2.rectangle(img, (20, 50), (20+bar, 70), (255, 0, 0), cv2.FILLED)
                            cv2.putText(img, "EXITING...", (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
                            
                            if elapsed > 1.5:
                                exit_status = "SLEEP"
                                raise StopIteration
                        else:
                            self.peace_start_time = 0
                            self.prev_scroll_y = 0
                            self.prev_scroll_x = 0
                            if self.is_dragging: pyautogui.mouseUp(); self.is_dragging = False

                if not _headless:
                    try:
                        cv2.imshow(self.window_name, img)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    except Exception as _disp_err:
                        # cv2.imshow threw a C++ / NSException — switch to headless
                        logger.warning(f"⚠️ Display error ({_disp_err}). Switching to headless gesture mode.")
                        _headless = True
        
        except StopIteration:
            pass
        except Exception as e:
            logger.error(f"Cursor Error: {e}")
        finally:
            # Release mouse if still held
            if self.is_dragging:
                pyautogui.mouseUp()

            # Release camera FIRST so macOS AVFoundation can start its async teardown
            if cap.isOpened():
                cap.release()

            # Destroy OpenCV windows only when we were in visual mode
            if not _headless:
                try:
                    cv2.destroyWindow(self.window_name)
                    # Pump the Cocoa event queue so the window actually closes
                    for _ in range(5):
                        cv2.waitKey(1)
                except Exception:
                    pass  # Window may already be gone

            # ── Camera release cooldown ──────────────────────────────────────
            # macOS AVFoundation session teardown is asynchronous.  Give it
            # ~600 ms before any subsequent camera user (e.g. FaceID) tries
            # to open the same device, otherwise they get a silent timeout.
            import time as _time
            _time.sleep(0.6)

        return exit_status
