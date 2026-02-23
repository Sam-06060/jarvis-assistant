import sys
import os
import PyQt6
from PyQt6.QtWidgets import QApplication, QLabel
from PyQt6.QtCore import Qt

# --- THE FIX: Find plugins manually relative to the installation ---
# This finds where 'PyQt6' is installed on your disk
package_path = os.path.dirname(PyQt6.__file__)
# It constructs the path to the 'plugins' folder manually
plugin_path = os.path.join(package_path, 'Qt6', 'plugins')

# Tell the OS to look here
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
# ---------------------------------------------

if __name__ == "__main__":
    print(f"🚀 Testing PyQt6...")
    print(f"📂 Forcing Plugin Path: {plugin_path}")
    
    try:
        app = QApplication(sys.argv)
        window = QLabel("✅ IT WORKS!\nPyQt6 is active.")
        window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setStyleSheet("background-color: #007AFF; color: white; font-size: 24px;")
        window.resize(400, 200)
        window.show()
        print("✅ Window launched successfully!")
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Crash: {e}")