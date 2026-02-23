"""
🔐 Jarvis Permission Checker
Checks all required macOS permissions on startup.
Only prompts for permissions that are genuinely NOT granted.
"""
import os
import subprocess
import threading


def check_all_permissions():
    """
    Check all 10 required permissions.
    Phase 1: Quietly check everything (no prompts, no Settings).
    Phase 2: Only prompt/open Settings for genuinely MISSING permissions.
    """
    print("\n🔐 JARVIS PERMISSION CHECK")
    print("━" * 40)
    
    results = {}
    
    # ── Check all permissions (quietly) ──
    results["Microphone"] = _check_microphone()
    results["Camera"] = _check_camera()
    results["Speech Recognition"] = _check_speech_recognition()
    results["Accessibility"] = _check_accessibility()
    results["Input Monitoring"] = _check_input_monitoring()
    results["Contacts"] = _check_contacts()
    results["Desktop Files"] = _check_desktop_files()
    results["Music"] = _check_music_automation()
    results["Automation"] = _check_system_events_automation()
    results["Shortcuts"] = _check_shortcuts()
    
    # ── Summary ──
    granted_count = sum(1 for g, _ in results.values() if g)
    total = len(results)
    
    print("━" * 40)
    if granted_count == total:
        print(f"✅ All {total}/{total} Permissions OK — Ready to go!")
    else:
        missing = [name for name, (g, _) in results.items() if not g]
        print(f"⚠️  {granted_count}/{total} Permissions OK")
        print(f"   Missing: {', '.join(missing)}")
        
        # Phase 2: Now prompt ONLY for the missing ones
        print("\n   🔔 Prompting for missing permissions...")
        for name in missing:
            try:
                _prompt_for_permission(name)
            except Exception:
                pass
        print("   Grant the permissions above and restart Jarvis.")
    
    print()
    return results


def _print_status(name, granted, msg):
    icon = "✅" if granted else "❌"
    print(f"  {icon} {name.ljust(20)} — {msg}")


# ════════════════════════════════════════
# PHASE 2: Prompt only for missing ones
# ════════════════════════════════════════
def _prompt_for_permission(name):
    """Trigger system dialog or open Settings for a missing permission"""
    
    # Permissions that support DIRECT system prompts (no Settings needed)
    if name == "Microphone":
        _request_av_access("soun")
        return
    if name == "Camera":
        _request_av_access("vide")
        return
    if name == "Contacts":
        _request_contacts_access()
        return
    
    # Permissions that can only open Settings
    settings_map = {
        "Speech Recognition": "com.apple.preference.security?Privacy_SpeechRecognition",
        "Accessibility":      "com.apple.preference.security?Privacy_Accessibility",
        "Input Monitoring":   "com.apple.preference.security?Privacy_ListenEvent",
        "Desktop Files":      "com.apple.preference.security?Privacy_FilesAndFolders",
    }
    pane = settings_map.get(name)
    if pane:
        _open_settings(pane)


# ════════════════════════════════════════
# CHECK FUNCTIONS (quiet, no side effects)
# ════════════════════════════════════════

# 1. MICROPHONE
def _check_microphone():
    try:
        from AVFoundation import AVCaptureDevice
        status = AVCaptureDevice.authorizationStatusForMediaType_("soun")
        if status == 3:
            _print_status("Microphone", True, "Granted")
            return (True, "Granted")
        elif status == 0:
            _print_status("Microphone", False, "Not yet requested")
            return (False, "Not requested")
        else:
            _print_status("Microphone", False, "Denied")
            return (False, "Denied")
    except ImportError:
        return _check_microphone_fallback()


def _check_microphone_fallback():
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                       input=True, frames_per_buffer=512)
        stream.read(512, exception_on_overflow=False)
        stream.stop_stream()
        stream.close()
        p.terminate()
        _print_status("Microphone", True, "Granted")
        return (True, "Granted")
    except Exception:
        _print_status("Microphone", False, "Cannot access")
        return (False, "Cannot access")


# 2. CAMERA
def _check_camera():
    try:
        from AVFoundation import AVCaptureDevice
        status = AVCaptureDevice.authorizationStatusForMediaType_("vide")
        if status == 3:
            _print_status("Camera", True, "Granted")
            return (True, "Granted")
        elif status == 0:
            _print_status("Camera", False, "Not yet requested")
            return (False, "Not requested")
        else:
            _print_status("Camera", False, "Denied")
            return (False, "Denied")
    except ImportError:
        return _check_camera_fallback()


def _check_camera_fallback():
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        ret = cap.isOpened()
        cap.release()
        if ret:
            _print_status("Camera", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Camera", False, "Cannot access")
            return (False, "Cannot access")
    except Exception:
        _print_status("Camera", False, "Cannot check")
        return (False, "Cannot check")


# 3. SPEECH RECOGNITION
def _check_speech_recognition():
    try:
        from Speech import SFSpeechRecognizer
        status = SFSpeechRecognizer.authorizationStatus()
        if status == 3:
            _print_status("Speech Recognition", True, "Granted")
            return (True, "Granted")
        elif status == 0:
            _print_status("Speech Recognition", False, "Not yet requested")
            return (False, "Not requested")
        else:
            _print_status("Speech Recognition", False, "Denied")
            return (False, "Denied")
    except ImportError:
        _print_status("Speech Recognition", True, "Skipped (no framework)")
        return (True, "Skipped")
    except Exception:
        _print_status("Speech Recognition", True, "Skipped (check failed)")
        return (True, "Skipped")


# 4. ACCESSIBILITY
def _check_accessibility():
    try:
        from ApplicationServices import AXIsProcessTrustedWithOptions
        # Check QUIETLY — no prompt, no dialog, no Settings
        trusted = AXIsProcessTrustedWithOptions({"AXTrustedCheckOptionPrompt": False})
        if trusted:
            _print_status("Accessibility", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Accessibility", False, "Not granted")
            return (False, "Not granted")
    except ImportError:
        return _check_accessibility_fallback()
    except Exception:
        return _check_accessibility_fallback()


def _check_accessibility_fallback():
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get name of first process'],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            _print_status("Accessibility", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Accessibility", False, "Not granted")
            return (False, "Not granted")
    except Exception:
        _print_status("Accessibility", False, "Cannot check")
        return (False, "Cannot check")


# 5. INPUT MONITORING
def _check_input_monitoring():
    try:
        import ctypes
        iokit = ctypes.cdll.LoadLibrary("/System/Library/Frameworks/IOKit.framework/IOKit")
        result = iokit.IOHIDCheckAccess(1)  # 0=granted, 1=denied, 2=unknown
        if result == 0:
            _print_status("Input Monitoring", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Input Monitoring", False, "Not granted")
            return (False, "Not granted")
    except Exception:
        _print_status("Input Monitoring", True, "Skipped (cannot check)")
        return (True, "Skipped")


# 6. CONTACTS
def _check_contacts():
    try:
        from Contacts import CNContactStore
        status = CNContactStore.authorizationStatusForEntityType_(0)
        if status == 3:
            _print_status("Contacts", True, "Granted")
            return (True, "Granted")
        elif status == 0:
            _print_status("Contacts", False, "Not yet requested")
            return (False, "Not requested")
        else:
            _print_status("Contacts", False, "Denied")
            return (False, "Denied")
    except ImportError:
        _print_status("Contacts", True, "Skipped (no framework)")
        return (True, "Skipped")


# 7. DESKTOP FILES
def _check_desktop_files():
    desktop = os.path.expanduser("~/Desktop")
    try:
        os.listdir(desktop)
        _print_status("Desktop Files", True, "Granted")
        return (True, "Granted")
    except PermissionError:
        _print_status("Desktop Files", False, "Denied")
        return (False, "Denied")
    except Exception:
        _print_status("Desktop Files", True, "Skipped")
        return (True, "Skipped")


# 8. MUSIC
def _check_music_automation():
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Music" to get name'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            _print_status("Music", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Music", False, "Not granted")
            return (False, "Not granted")
    except subprocess.TimeoutExpired:
        _print_status("Music", False, "Timeout (may need grant)")
        return (False, "Timeout")
    except Exception:
        _print_status("Music", True, "Skipped")
        return (True, "Skipped")


# 9. AUTOMATION (System Events)
def _check_system_events_automation():
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to get name of first process'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            _print_status("Automation", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Automation", False, "Not granted")
            return (False, "Not granted")
    except subprocess.TimeoutExpired:
        _print_status("Automation", False, "Timeout (may need grant)")
        return (False, "Timeout")
    except Exception:
        _print_status("Automation", True, "Skipped")
        return (True, "Skipped")


# 10. SHORTCUTS
def _check_shortcuts():
    try:
        result = subprocess.run(
            ["shortcuts", "list"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            _print_status("Shortcuts", True, "Granted")
            return (True, "Granted")
        else:
            _print_status("Shortcuts", False, "Not granted")
            return (False, "Not granted")
    except FileNotFoundError:
        _print_status("Shortcuts", True, "Skipped (CLI not found)")
        return (True, "Skipped")
    except subprocess.TimeoutExpired:
        _print_status("Shortcuts", False, "Timeout")
        return (False, "Timeout")
    except Exception:
        _print_status("Shortcuts", True, "Skipped")
        return (True, "Skipped")


# ════════════════════════════════════════
# HELPER FUNCTIONS (only called in Phase 2)
# ════════════════════════════════════════
def _request_av_access(media_type):
    """Trigger system dialog for Microphone/Camera"""
    try:
        from AVFoundation import AVCaptureDevice
        event = threading.Event()
        AVCaptureDevice.requestAccessForMediaType_completionHandler_(media_type, lambda g: event.set())
        event.wait(timeout=10)
    except Exception:
        pass


def _prompt_accessibility():
    """Open the Accessibility prompt dialog"""
    try:
        from ApplicationServices import AXIsProcessTrustedWithOptions
        AXIsProcessTrustedWithOptions({"AXTrustedCheckOptionPrompt": True})
    except Exception:
        _open_settings("com.apple.preference.security?Privacy_Accessibility")


def _request_contacts_access():
    """Trigger system permission dialog for Contacts"""
    try:
        from Contacts import CNContactStore
        event = threading.Event()
        store = CNContactStore.alloc().init()
        store.requestAccessForEntityType_completionHandler_(0, lambda g, e: event.set())
        event.wait(timeout=10)
    except Exception:
        _open_settings("com.apple.preference.security?Privacy_Contacts")


def _open_settings(pane_id):
    """Open a specific System Settings pane"""
    try:
        subprocess.run(["open", f"x-apple.systempreferences:{pane_id}"], check=False)
    except Exception:
        pass


if __name__ == "__main__":
    check_all_permissions()
