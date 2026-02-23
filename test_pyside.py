import sys
from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

if __name__ == "__main__":
    print("🚀 Testing PySide6...")
    try:
        app = QApplication(sys.argv)
        # Using a single line string with \n to avoid syntax errors
        window = QLabel("✅ IT WORKS!\nPySide6 (Stable) is active.")
        window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setStyleSheet("background-color: green; color: white; font-size: 24px;")
        window.resize(400, 200)
        window.show()
        print("✅ Window launched successfully!")
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Crash: {e}")