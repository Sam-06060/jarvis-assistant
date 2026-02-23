import os
import sys
import PySide6

# 1. Clear any old "Ghost" variables that might be confusing the system
if "QT_PLUGIN_PATH" in os.environ:
    del os.environ["QT_PLUGIN_PATH"]
if "QT_QPA_PLATFORM_PLUGIN_PATH" in os.environ:
    del os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"]

# 2. Hunt down the REAL path for PySide6
# It's usually inside .../site-packages/PySide6/plugins/platforms
base_dir = os.path.dirname(PySide6.__file__)
plugins_dir = os.path.join(base_dir, 'plugins')
platforms_dir = os.path.join(plugins_dir, 'platforms')

# 3. Force the app to use this path
os.environ['QT_PLUGIN_PATH'] = plugins_dir
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = platforms_dir

print(f"🔧 FOUND PLUGIN PATH: {plugins_dir}")
print(f"🔧 FOUND PLATFORM PATH: {platforms_dir}")
print("-" * 30)

# 4. Now attempt to launch the App
try:
    from PySide6.QtWidgets import QApplication, QLabel
    from PySide6.QtCore import Qt
    
    app = QApplication(sys.argv)
    
    window = QLabel("✅ IT WORKS!\nPySide6 is active.")
    window.setAlignment(Qt.AlignmentFlag.AlignCenter)
    window.setStyleSheet("background-color: green; color: white; font-size: 24px;")
    window.resize(400, 200)
    window.show()
    
    print("🚀 Window launched successfully!")
    app.exec()
except Exception as e:
    print(f"❌ Crash: {e}")