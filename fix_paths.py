import os
import sys
import PyQt6

def find_cocoa_plugin():
    print("🔍 Hunting for libqcocoa.dylib...")
    
    # Get the base path of PyQt6
    base_path = os.path.dirname(PyQt6.__file__)
    print(f"📂 PyQt6 is installed in: {base_path}")
    
    # Walk through the directory to find the specific file
    plugin_path = None
    for root, dirs, files in os.walk(base_path):
        if "libqcocoa.dylib" in files:
            # We found the file! The plugin path is the 'platforms' folder containing it.
            # However, Qt expects the folder *containing* the 'platforms' folder.
            # usually: .../PyQt6/Qt6/plugins
            
            # Check if we are inside a 'platforms' folder
            if os.path.basename(root) == 'platforms':
                plugin_path = os.path.dirname(root)
                print(f"✅ Found Cocoa driver at: {os.path.join(root, 'libqcocoa.dylib')}")
                break

    if plugin_path:
        print(f"🔧 Setting QT_PLUGIN_PATH to: {plugin_path}")
        os.environ['QT_PLUGIN_PATH'] = plugin_path
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(plugin_path, 'platforms')
        return True
    else:
        print("❌ CRITICAL: libqcocoa.dylib not found. Your installation is corrupt.")
        return False

# --- RUN THE FIX ---
if find_cocoa_plugin():
    print("\n🚀 Attempting to launch HUD with corrected paths...")
    
    # Now import the HUD and run it
    try:
        from PyQt6.QtWidgets import QApplication, QLabel
        app = QApplication(sys.argv)
        window = QLabel("IT WORKS! \n(Close this and run jarvis.py)")
        window.resize(400, 200)
        window.setStyleSheet("font-size: 24px; color: green; qproperty-alignment: AlignCenter;")
        window.show()
        print("✅ GUI Launched successfully!")
        app.exec()
    except Exception as e:
        print(f"💥 Still crashed: {e}")
else:
    print("\nSOLUTION: Run 'pip install --force-reinstall PyQt6 PyQt6-Qt6'")