import time
import os
import numpy as np
import subprocess
import sys
import threading

# Lazy imports for speed
face_recognition = None
cv2 = None

class FaceID:
    def __init__(self, reference_image_path="data/me.jpg", hud_queue=None):
        self.reference_image_path = reference_image_path
        self.white_img_path = os.path.abspath("data/white.jpg")
        self.known_face_encoding = None
        self.hud_queue = hud_queue
        # Nuclear Startup: Load reference face in background to avoid blocking boot
        threading.Thread(target=self.load_reference_face, daemon=True, name="FaceID-Loader").start()

    def _ensure_imports(self):
        global face_recognition, cv2
        if face_recognition is None:
            import face_recognition
        if cv2 is None:
            try:
                import cv2
            except ImportError:
                print("⚠️ OpenCV not found")

    def load_reference_face(self):
        self._ensure_imports()
        if os.path.exists(self.reference_image_path):
            try:
                print("🔒 Loading FaceID data...")
                image = face_recognition.load_image_file(self.reference_image_path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    self.known_face_encoding = encodings[0]
                else:
                    print("⚠️ No face found in reference image. Security disabled.")
            except Exception as e:
                print(f"❌ Error loading FaceID: {e}")
        else:
            print(f"⚠️ Reference image not found at {self.reference_image_path}")

    def _get_brightness(self, frame):
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            return np.mean(gray)
        except:
            return 100 

    def _set_mac_brightness(self, level):
        """Helper to physically boost screen brightness"""
        try:
            if level == "max":
                script = 'repeat 16 times\ntell application "System Events" to key code 144\nend repeat'
            else:
                script = 'repeat 8 times\ntell application "System Events" to key code 145\nend repeat'
            subprocess.run(["osascript", "-e", script], check=False)
        except:
            pass

    def _bring_jarvis_to_front(self):
        """Return focus to Jarvis after FaceID overlay/flash windows."""
        try:
            # Primary: explicit app activate via AppleScript.
            subprocess.run(["osascript", "-e", 'tell application "Jarvis" to activate'], check=False)
            # Fallback: ensure the app is frontmost even if naming resolution fails.
            subprocess.run(["open", "-a", "Jarvis"], check=False)
        except Exception:
            pass

    def _emit_flash_event(self, enabled: bool):
        """Notify Jarvis app to show/hide in-app white flash overlay."""
        try:
            if self.hud_queue:
                self.hud_queue.put(("FLASH", "ON" if enabled else "OFF"))
        except Exception:
            pass

    def verify_user(self, timeout=5):
        # If face encoding is still loading from background thread, wait for it.
        # On first wake this prevents bypassing the animation entirely.
        if self.known_face_encoding is None:
            wait_start = time.time()
            while self.known_face_encoding is None and (time.time() - wait_start) < 3.0:
                time.sleep(0.05)
        # If still None after waiting (no reference image / load failed), grant access silently.
        if self.known_face_encoding is None:
            return True
        overlay_process = None
        
        # 1. Launch the Native Swift UI (Compiled Binary)
        # Fix path resolution
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # jarvis root
            executable_path = os.path.join(base_dir, "modules", "FaceIDOverlay", "FaceIDOverlay.app", "Contents", "MacOS", "FaceIDOverlay")
            
            if not os.path.exists(executable_path):
                print(f"⚠️ FaceID Binary NOT FOUND at: {executable_path}")
            else:
                # print(f"🔒 Launching FaceID Overlay: {executable_path}")
                overlay_process = subprocess.Popen(
                    [executable_path],
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=0 
                )
                # Short wait to let the island expand animation begin
                time.sleep(0.2)
        except Exception as e:
            print(f"⚠️ Could not launch FaceID UI: {e}")

        # 2. Camera & Recognition Logic
        video_capture = cv2.VideoCapture(0)
        if not video_capture.isOpened():
            video_capture = cv2.VideoCapture(1)

        access_granted = False
        flash_active = False
        
        try:
            start_time = time.time()
            
            # --- 🌑 LOW LIGHT CHECK ---
            ret, first_frame = video_capture.read()
            if ret:
                brightness = self._get_brightness(first_frame)
                if brightness < 60:
                    self._set_mac_brightness("max")
                    self._emit_flash_event(True)
                    # Legacy path kept for fallback/debug:
                    # subprocess.run(["open", "-a", "Preview", self.white_img_path], check=False)
                    time.sleep(1.0) 
                    flash_active = True

            # --- SCAN LOOP ---
            while (time.time() - start_time) < timeout:
                ret, frame = video_capture.read()
                if not ret: continue

                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])

                face_locations = face_recognition.face_locations(rgb_small_frame)
                
                if face_locations:
                    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                    for face_encoding in face_encodings:
                        matches = face_recognition.compare_faces(
                            [self.known_face_encoding], 
                            face_encoding, 
                            tolerance=0.45
                        )
                        if True in matches:
                            access_granted = True
                            break
                
                if access_granted:
                    break

        except Exception as e:
            print(f"Error during scan: {e}")

        finally:
            if flash_active:
                # Legacy path kept for fallback/debug:
                # subprocess.run(["pkill", "-x", "Preview"], check=False)
                self._emit_flash_event(False)
                self._set_mac_brightness("restore")
            
            # 3. Communicate Result to Swift UI
            if overlay_process and overlay_process.poll() is None:
                try:
                    if access_granted:
                        # Send "success" — triggers Rings -> Checkmark -> Retract animation in Swift UI.
                        # The overlay will self-terminate after its closing animation completes.
                        if overlay_process.stdin:
                            overlay_process.stdin.write("success\n")
                            overlay_process.stdin.flush()

                        # ── PARALLEL WAKE ────────────────────────────────────────────────────────
                        # Return immediately so Jarvis speaks "Yes sir" and activates the mic
                        # WHILE the success animation is still playing on screen.
                        # The overlay runs its ring -> checkmark -> island-retract sequence
                        # independently and self-exits cleanly when done.
                        # A background daemon thread provides a safety-timeout kill (4s)
                        # in case the Swift process fails to self-terminate.
                        def _cleanup_overlay_bg(proc, vid, bring_front_fn):
                            try:
                                proc.wait(timeout=4.0)  # Overlay self-exits after retract anim
                            except Exception:
                                try:
                                    proc.terminate()
                                except Exception:
                                    pass
                            finally:
                                try:
                                    vid.release()
                                    import cv2 as _cv2
                                    _cv2.destroyAllWindows()
                                    _cv2.waitKey(1)
                                except Exception:
                                    pass
                                bring_front_fn()

                        threading.Thread(
                            target=_cleanup_overlay_bg,
                            args=(overlay_process, video_capture, self._bring_jarvis_to_front),
                            daemon=True,
                            name="FaceID-OverlayCleanup"
                        ).start()
                        # ─────────────────────────────────────────────────────────────────────────

                        return True  # ← instant return; cleanup happens in background

                    else:
                        overlay_process.stdin.write("fail\n")
                        overlay_process.stdin.flush()
                        time.sleep(1.0)  # Wait for shake animation before returning denied
                    
                    # Ensure process is killed if it hasn't self-terminated
                    if overlay_process.poll() is None:
                        overlay_process.terminate()
                except Exception as e:
                    print(f"UI Communication error: {e}")
            
            # Failure-path cleanup (success path returns early above)
            video_capture.release()
            cv2.destroyAllWindows()
            cv2.waitKey(1)
            self._bring_jarvis_to_front()
            
        return access_granted
