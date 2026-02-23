# test_pyside.py
import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

if __name__ == "__main__":
    print("🚀 Testing PySide6...")
    
    try:
        # 1. Initialize the App
        app = QApplication(sys.argv)
        
        # 2. Create the Window
        window = QLabel("JARVIS HUD\n(PySide6 Active)")
        window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setStyleSheet("background-color: black; color: #00F0FF; font-size: 24px; font-family: Menlo;")
        window.resize(400, 200)
        
        # 3. Show it
        window.show()
        print("✅ Window launched! Check your screen.")
        
        # 4. Run the Event Loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Crash: {e}")