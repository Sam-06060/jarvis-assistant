import sys
import os
import importlib

# Add project root to path
sys.path.append(os.getcwd())

print("🔍 Verifying System Imports...\n")

modules_to_check = [
    "config",
    "utils.logger",
    "modules.speech",
    "modules.brain",
    "modules.file_manager",
    "modules.system_info",
    "modules.commands",
    "modules.health_checker",
    "modules.analytics",
    "modules.conversation_history",
    "modules.hotkey_manager",
    "utils.context_manager",
    "utils.fuzzy_matcher",
    "utils.offline_cache",
    "utils.audio_manager",
    "modules.music_controller", # Reported issue here
    "modules.skills.music_skill" # And here
]

failed = []

for mod_name in modules_to_check:
    try:
        importlib.import_module(mod_name)
        print(f"✅ {mod_name}")
    except Exception as e:
        print(f"❌ {mod_name}: {e}")
        failed.append((mod_name, str(e)))

print(f"\nCompleted. {len(failed)} failures.")
if failed:
    sys.exit(1)
