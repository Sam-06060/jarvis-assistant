
import sys
import os

# Add modules path
sys.path.append(os.path.abspath("modules"))
sys.path.append(os.getcwd())

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    # Check imports first
    import face_recognition
    print("face_recognition imported")
    import cv2
    print("cv2 imported")

    from modules.security import FaceID
    print("FaceID imported from modules.security")
    
    f = FaceID()
    print("FaceID initialized")
    
    print("Starting verification...")
    result = f.verify_user(timeout=5)
    print(f"Verify result: {result}")

except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Runtime Error: {e}")
    import traceback
    traceback.print_exc()
