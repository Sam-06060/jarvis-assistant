import cv2
import sys

print("📸 Testing Camera Access...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ Failed to open camera (Device 0)")
    sys.exit(1)

success, frame = cap.read()
if success:
    print("✅ Camera read successful!")
    print(f"Dimensions: {frame.shape}")
else:
    print("⚠️ Camera opened but failed to read frame.")

cap.release()
print("Done.")
