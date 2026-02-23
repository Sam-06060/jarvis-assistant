import sys
import os
import PySide6 # We import this first to find the folder

# --- 1. FORCE THE PATHS (The Magic Fix) ---
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins')
platforms_path = os.path.join(plugin_path, 'platforms')

os.environ['QT_PLUGIN_PATH'] = plugin_path
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_path

print(f"🔧 FORCED PLUGIN PATH: {plugin_path}")
print(f"🔧 FORCED PLATFORM PATH: {platforms_path}")
# ------------------------------------------

from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtCore import Qt

if __name__ == "__main__":
    print("🚀 Testing PySide6 with Forced Paths...")
    try:
        app = QApplication(sys.argv)
        
        window = QLabel("✅ IT WORKS!\nPaths are fixed.")
        window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window.setStyleSheet("background-color: green; color: white; font-size: 24px;")
        window.resize(400, 200)
        window.show()
        
        print("✅ Window launched successfully!")
        sys.exit(app.exec())
    except Exception as e:
        print(f"❌ Crash: {e}")